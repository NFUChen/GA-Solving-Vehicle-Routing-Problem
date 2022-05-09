from typing import Dict, List
from random import random, choice
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
from .mutation_strategy import MutationStrategy
from .crossover_strategy import CrossoverStrategy
# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class SolutionChromosome:
    pass


class SolutionChromosome(BuilderFactory):
    def __init__(self,
                 solution: Solution,
                 immutable_depot_names: List[int],
                 resources_used: Dict[str, float] = None,
                 generation: int = 0, is_children: bool = False) -> None:
        self.solution = solution

        # dont' choose vehicle without any depots being assigned, or len(route) < 3, [0,1,0] -> will cause mutation error,
        # mutation strategy need to pick two 'DIFFERENT' route index and that it shouldn't be 0

        self.resource_calc = RouteResourceCalculator()
        self.immutable_depot_names = immutable_depot_names
        self.generation = generation

        self._vehicle_mutaion_and_crossover_dict = self._filter_vehicle_can_be_chosen_for_mutation_and_crossover()
        self.vehicles_can_be_chosen_for_mutation = self._vehicle_mutaion_and_crossover_dict[
            "mutation"]
        self.vehicles_can_be_chosen_for_crossover = self._vehicle_mutaion_and_crossover_dict[
            "crossover"]
        self.is_children = is_children
        self.mutation_strategy = MutationStrategy(immutable_depot_names)
        self.crossover_strategy = CrossoverStrategy(solution, immutable_depot_names,
                                                    self.vehicles_can_be_chosen_for_crossover,
                                                    )

        if resources_used is not None:
            self.resources_used = resources_used
            return
        self.resources_used = self.resource_calc.calculate_solution_resources(
            solution)

    def mutate(self, mutation_rate: float, chosen_vehicle_idx: int = None) -> SolutionChromosome:
        random_value = random()
        if random_value > mutation_rate:  # 0.05
            return self
        for chosen_vehicle_idx in self.vehicles_can_be_chosen_for_mutation:
            mutation_func = self.mutation_strategy.randomly_choose_mutation_strategy()
            chosen_vehicle_route = self.solution[chosen_vehicle_idx]
            mutated_route = mutation_func(chosen_vehicle_route)

            # after mutation, update chromosome fitness ( based on self.resources_used, and self.solution)
            self._update_resources_used(chosen_vehicle_idx, mutated_route)
            self.solution[chosen_vehicle_idx] = mutated_route

        return self

    def crossover(self, _other_solution_chromosome: SolutionChromosome, crossover_rate: float) -> 'List[SolutionChromosome] | None':

        random_value = random()
        if random_value > crossover_rate:
            child_x = self._create_next_generation_self_with_new_solution(
                self.solution)
            child_y = self._create_next_generation_self_with_new_solution(
                self.solution)
            return [child_x, child_y]

        child_x_solution, child_y_solution = self.crossover_strategy.single_point_crossover(
            _other_solution_chromosome.solution, _other_solution_chromosome.vehicles_can_be_chosen_for_crossover)

        child_x = self._create_next_generation_self_with_new_solution(
            child_x_solution)
        child_y = self._create_next_generation_self_with_new_solution(
            child_y_solution)
        return [child_x, child_y]

    def __repr__(self) -> str:
        chromosome = f"Chromosome: {self.solution}"
        resources = self.resources_used

        fuel_fee = f"Fuel Fee: ${int(resources['fuel_fee'])}"
        distance = f"Distance: {int(resources['distance'])} km"
        total_delivery_time = f"Total Delivery Time: {round(resources['delivery_time'] + resources['service_time'], 2)} Mins"
        vehicle_fixed_cost = f"Vehicle Fixed Cost: ${int(resources['vehicle_fixed_cost'])}"
        driver_cost = f"Driver Cost: ${int(resources['driver_cost'])}"
        total_cost_amount = int(
            resources['fuel_fee']) + resources['vehicle_fixed_cost'] + int(resources['driver_cost'])
        total_cost = f"Total Cost: ${total_cost_amount}"
        number_of_vehicles_assigned = f"Number of Vehicles Assigned: {resources['number_of_vehicles_assigned']}"
        number_of_replenishment = f"Number of Replenishsments: {resources['number_of_replenishment']}"
        generation = f"Generation: {self.generation}"
        fitness = f"Fitness: {round(self.fitness, 4)}"
        sep = "-" * 60

        _repr = [
            chromosome,
            total_cost,
            fuel_fee,
            vehicle_fixed_cost,
            driver_cost,
            distance,
            total_delivery_time,
            number_of_vehicles_assigned,
            number_of_replenishment,
            generation,
            fitness,
            sep
        ]

        return "\n".join(_repr)

    def __eq__(self, _other_solution_chromosome: SolutionChromosome) -> bool:
        return self.fitness == _other_solution_chromosome.fitness

    def __gt__(self, _other_solution_chromosome: SolutionChromosome) -> bool:
        # 總配送車數最小化為主要目標，
        # 降低總配送距離與減少每趟次的花費時間為次要目標，
        # 以求取最佳的配送路線。所以目標函數(1)為最小化車輛的固定成本、
        # 車輛行駛的距離成本、每趟次花費的司機員薪資成本。

        return self.fitness > _other_solution_chromosome.fitness

    @property
    def fitness(self) -> float:
        resources = self.resources_used
        total_cost = (
            resources["fuel_fee"] +
            resources["vehicle_fixed_cost"] +
            resources["driver_cost"]
        )

        return (1 / total_cost) * 1000000

    def _create_next_generation_self_with_new_solution(self, new_solution: Solution) -> SolutionChromosome:
        # passing in self.resources_used is for performance concern, which avoidss duplicate computation.
        if new_solution == self.solution:  # two parents are not successfully crossovered
            return SolutionChromosome(new_solution, self.immutable_depot_names, self.resources_used, self.generation + 1, is_children=True)

        return SolutionChromosome(new_solution, self.immutable_depot_names, None, self.generation + 1, is_children=True)

    def _randomly_choose_a_vehicle(self) -> int:
        
        return choice(self.vehicles_can_be_chosen_for_mutation)

    def _update_resources_used(self, vehicle_idx: int, updated_route: List[int]) -> None:
        '''
        After mutation, make sure we update chromosome 
        (e.g., self.resources_used, self.solution)
        '''

        original_route_resources = self.resource_calc.calculate_route_resources(
            vehicle_idx, self.solution[vehicle_idx])
        updated_route_resources = self.resource_calc.calculate_route_resources(
            vehicle_idx, updated_route
        )

        for resource in self.resources_used.keys():
            self.resources_used[resource] -= original_route_resources[resource]
            self.resources_used[resource] += updated_route_resources[resource]

    def _is_route_contains_immutable_depots(self, route: List[int]) -> bool:
        if len(route) == 0:
            return False

        for depot in route[1:-1]:  # [0,1,2,3,0] -> [1,2,3]
            if depot in self.immutable_depot_names:
                return True
        return False

    def _filter_vehicle_can_be_chosen_for_mutation_and_crossover(self) -> Dict[str, List[int]]:
        vehicle_mutaion_and_crossover_dict = {}
        vehicle_mutaion_and_crossover_dict["mutation"] = [].copy()
        vehicle_mutaion_and_crossover_dict["crossover"] = [].copy()
        for vehicle_idx, route in self.solution.items():

            if len(route) <= 3:
                continue

            vehicle_mutaion_and_crossover_dict["mutation"].append(
                vehicle_idx)

            # [0,1,0] -> [1]
            if not self._is_route_contains_immutable_depots(route):
                vehicle_mutaion_and_crossover_dict["crossover"].append(
                    vehicle_idx)
        return vehicle_mutaion_and_crossover_dict

    def _is_route_contains_immutable_depots(self, route) -> bool:
        route_without_warehouse_depot = route[1:-1]

        for depot in route_without_warehouse_depot:
            if depot in self.immutable_depot_names:
                return True
        return False

    def _reproduction_mutate(self) -> SolutionChromosome:
        for vehicle_idx in self.vehicles_can_be_chosen_for_mutation:
            self.mutate(1, vehicle_idx)

        return self
