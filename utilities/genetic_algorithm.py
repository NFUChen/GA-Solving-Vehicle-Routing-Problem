from typing import List
from .solution_chromosome import SolutionChromosome
from .solution_generator import SolutionGenerator
from random import random
from copy import deepcopy
import numpy as np


class GeneticAlgorithm:
    def __init__(self, population_size,
                 mutation_rate,
                 crossover_rate,
                 maximum_iteration) -> None:
        self.solution_generator = SolutionGenerator()
        self.population_size = population_size
        self.population = None
        self.total_fitness_of_current_population = None

        self.current_iteration = 0
        self.maximum_iteration = maximum_iteration

        self.global_best_solution = None
        self.current_best_solution = None

        self.max_mutation_rate = mutation_rate
        self.max_crossover_rate = crossover_rate

        self.mutation_rate_lookup = np.linspace(self.max_mutation_rate, 0, self.maximum_iteration)

        self.crossover_rate_lookup = np.linspace(0, self.max_crossover_rate, self.maximum_iteration)

    @property
    def current_level_mutation_rate(self) -> float:
        if self.current_iteration > len(self.mutation_rate_lookup) - 1:
            return self.mutation_rate_lookup[-1]

        return self.mutation_rate_lookup[self.current_iteration]

    @property
    def current_level_crossover_rate(self) -> float:
        if self.current_iteration > len(self.crossover_rate_lookup) - 1:
            return self.crossover_rate_lookup[-1]

        return self.crossover_rate_lookup[self.current_iteration]

    def _generate_initial_population(self) -> List[SolutionChromosome]:

        initial_population = self.solution_generator.generate_valid_solutions(self.population_size)
        # -> [0, 1, 2, 3], remember to choose last one to get the best fitness, chromosome is sorted by 'FITNESS'
        initial_population.sort()

        self.population = initial_population
        self.global_best_solution = initial_population[-1]
        self.current_best_solution = initial_population[-1]

    def _calculate_total_fitness_of_population(self) -> float:
        total_fitness = 0
        for chromosome in self.population:
            total_fitness += chromosome.fitness

        return total_fitness

    def _select_a_parent(self) -> List[SolutionChromosome]:
        '''
        This function simulates roulette wheel selection
        '''

        total_fitness = self._calculate_total_fitness_of_population()
        self.total_fitness_of_current_population = total_fitness
        random_value = random() * total_fitness
        check_sum = 0
        selected_idx = 0
        while (check_sum < random_value and selected_idx < self.population_size):
            check_sum += self.population[selected_idx].fitness
            selected_idx += 1

        return deepcopy(self.population[selected_idx - 1])

    def _crossover_two_parents_and_get_new_generation_children(self) -> List[SolutionChromosome]:
        '''
        Create two offsprings with crossover
        '''
        while (True):
            parent_x = self._select_a_parent()  # returns a copy of a parent
            parent_y = self._select_a_parent()
            if (parent_x.fitness != parent_y.fitness):
                break

        next_generation_children = parent_x.crossover(parent_y, self.current_level_crossover_rate)

        return next_generation_children

    def _mutate_two_children_and_get_mutated_children(self, children: List[SolutionChromosome]) -> List[SolutionChromosome]:
        children_copy = deepcopy(children)
        for child in children_copy:
            child.mutate(self.current_level_mutation_rate)

        return children_copy


    def _update_population_info(self, new_population: List[SolutionChromosome]) -> None:
        new_population.sort()
        self.population = new_population
        self.current_best_solution = new_population[-1]
        self.global_best_solution = max(self.global_best_solution, self.current_best_solution)

    @property
    def _is_termination_criteria_met(self) -> bool:
        if self.current_iteration >= self.maximum_iteration:
            return True

        return False

    def solve(self) -> None:
        self._generate_initial_population()
        print(f"First Generation Population is Initialized")
        while not (self._is_termination_criteria_met):
            next_generation_population = []
            while (len(next_generation_population) < self.population_size):
                crossovered_children = self._crossover_two_parents_and_get_new_generation_children()
                mutated_children = self._mutate_two_children_and_get_mutated_children(crossovered_children) 
                next_generation_population.extend(mutated_children)
            self._update_population_info(next_generation_population)
            print(f"Iteration: {self.current_iteration} ")
            print(f"Total Fitness: {self.total_fitness_of_current_population}")
            print(f"Best Fitness: {self.current_best_solution.fitness}")
            print(f"New Population Fitness: {','.join([str(round(chromosome.fitness, 4)) for chromosome in self.population])}")
            print("-" * 100, '\n')
            self.current_iteration += 1
