from copy import deepcopy
from typing import List, Dict
from random import choice
from time import time

from .constraint_checker import ConstraintChecker
from .base_class import BuilderFactory
from .optimizer import Optimizer
from .solution_chromosome import SolutionChromosome

# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


def timer(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(
            f'Function {func.__name__!r} executed in {(t2-t1):.4f}s', end="\t")
        return result
    return wrap_func


class SolutionGenerator(BuilderFactory):
    def __init__(self, constraint_checker: ConstraintChecker = ConstraintChecker()) -> None:
        super().__init__()
        if not isinstance(constraint_checker, ConstraintChecker):
            raise TypeError(
                f"'constraint_checker' is not a ConstraintChecker instance, given {type(constraint_checker)} type")
        self.checker = constraint_checker
        self.optimizer = Optimizer()

        self.all_depot_names = self.depots.all_depot_names
        print(f"Available Depot Names: {self.all_depot_names}")
        self.all_vehicle_names = self.vehicles.all_vehicle_names
        print(f"Available Vehicle Names: {self.all_vehicle_names}")
        self.all_depots_to_be_assigned = [
            name for name in self.all_depot_names if name != 0]
        self.vehicles_with_assigned_depots = {vehicle_name: []
                                              for vehicle_name in self.all_vehicle_names}

    def _start_from_warehouse_and_go_back_to_warehouse_helper(self, route: List[int]) -> List[int]:
        '''
        A helper function for .generate_initial_raw_solution(), 
        which adds 1 zero at the beginning and at the end of the route, 
        indicating that the route should be starting from warehouse, and going back to warehouse
        '''
        return [0, *route, 0]

    @timer
    def _generate_initial_raw_solution(self) -> Solution:
        '''
        .generate_initial_raw_solution generates a raw solution that is subject to further check with constraint checker (i.e., ConstraintChecker)

        P.S. This method generates a solution at least doesn't violate the constraint that an undeliverable depot is assigned to a given vehicle.

        '''
        # [1,2 ...., n], 0(warehouse) should be excluded
        all_depots_to_be_assigned = deepcopy(self.all_depots_to_be_assigned)
        vehicles_with_assigned_depots = deepcopy(
            self.vehicles_with_assigned_depots)  # {0:[], 1:[], 2:[] ..., n:[]}
        # while there exists any depot in all_depots_to_be_assigned
        while (len(all_depots_to_be_assigned) > 0):
            select_depot_idx = choice(all_depots_to_be_assigned)
            vehicle_idx_assigned = self.depots[select_depot_idx].assign_vehicles(
            )
            vehicles_with_assigned_depots[vehicle_idx_assigned].append(
                select_depot_idx)

            all_depots_to_be_assigned.remove(select_depot_idx)

        # use helper function i.e., [0, *route, 0]
        for vehicle_idx, assigned_depots in vehicles_with_assigned_depots.items():
            if len(assigned_depots) == 0:  # if assigned route is a empty list
                continue

            route = self._start_from_warehouse_and_go_back_to_warehouse_helper(
                assigned_depots)
            shortage_points = self.optimizer.find_shortage_points_in_route(
                vehicle_idx, route)
            non_shortage_route = self.optimizer.insert_replenish_points_for_route(
                shortage_points, route)

            vehicles_with_assigned_depots[vehicle_idx] = non_shortage_route

        return vehicles_with_assigned_depots

    @timer
    def generate_valid_solutions(self, number_of_solutions: int) -> List[SolutionChromosome]:
        solution_count = 0
        valid_solutions = []
        while (len(valid_solutions) < number_of_solutions):
            solution = self._generate_initial_raw_solution()
            if solution in valid_solutions:
                continue
            solution_count += 1
            solution_chromosome = SolutionChromosome(solution)
            valid_solutions.append(solution_chromosome)

            print(f"No. {solution_count}")

        return valid_solutions
