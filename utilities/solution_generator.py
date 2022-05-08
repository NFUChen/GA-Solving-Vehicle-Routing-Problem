from typing import List, Dict, Union
from copy import deepcopy
from time import time

from click import progressbar
from .base_class import BuilderFactory
from .constraint_checker import ConstraintChecker
from .route_resource_calculator import RouteResourceCalculator
from .optimizer import Optimizer
from .solution_chromosome import SolutionChromosome
from tqdm import tqdm

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
        self.resource_calc = RouteResourceCalculator()

        self.all_depot_names = self.depots.all_depot_names
        self.all_vehicle_names = self.vehicles.all_vehicle_names
        self.sorted_depots_to_be_assigned = self.sorted_depots  # from BuilderFactry
        self.all_depot_names_with_time_window_constraints = self.depot_builder.all_depot_names_with_time_window_constraint
        self.vehicles_with_assigned_depots = {vehicle_name: []
                                              for vehicle_name in self.all_vehicle_names}

        print(f"Available Vehicle Names: {self.all_vehicle_names}")
        print(f"Available Depot Names: {self.all_depot_names}")
        print(
            f"All Depots With Time Window Constraints: {self.all_depot_names_with_time_window_constraints}")

    def _start_from_warehouse_and_go_back_to_warehouse_helper(self, route: List[int]) -> List[int]:
        '''
        A helper function for .generate_initial_raw_solution(),
        which adds 1 zero at the beginning and at the end of the route,
        indicating that the route should be starting from warehouse, and going back to warehouse
        '''
        return [0, *route, 0]

    @timer
    def _generate_initial_raw_solution(self) -> 'Solution | int':
        '''
        .generate_initial_raw_solution generates a raw solution that is subject to further check with constraint checker (i.e., ConstraintChecker)

        P.S. This method generates a solution at least doesn't violate the constraint that an undeliverable depot is assigned to a given vehicle.

        '''
        # [1,2 ...., n], 0 (warehouse) should be excluded
        all_depots_to_be_assigned = deepcopy(self.sorted_depots_to_be_assigned)

        vehicles_with_assigned_depots = deepcopy(
            self.vehicles_with_assigned_depots)  # {0:[], 1:[], 2:[] ..., n:[]}

        for depot in all_depots_to_be_assigned:
            #-----------------------------------------------------------------------#
            # 無需延遲配送的站點, 需當墊背的增取時間
            vehicle_idx_assigned = depot.assign_vehicle()
            if (depot.earilest_time_can_be_delivered == 0):
                vehicles_with_assigned_depots[vehicle_idx_assigned].append(
                    depot.depot_name)
                continue
            #-----------------------------------------------------------------------#
            #!= 0 需延遲配送的站點
            available_vehicles_for_current_depot = depot.available_vehicles

            is_delayed_depot_assigned = False
            for vehicle_idx in available_vehicles_for_current_depot:
                current_route = vehicles_with_assigned_depots[vehicle_idx]
                current_depot_idx = depot.depot_name
                if len(current_route) < 2:
                    continue
                if self.checker.is_passing_time_window_constraints(vehicle_idx, current_route, current_depot_idx):
                    # only execute once, once complete appending operation, break current loop
                    vehicles_with_assigned_depots[vehicle_idx].append(
                        current_depot_idx)
                    is_delayed_depot_assigned = True
                    break
            if not is_delayed_depot_assigned:
                return depot.depot_name

        # use helper function i.e., [0, *route, 0]
        for vehicle_idx, assigned_depots in vehicles_with_assigned_depots.items():
            if len(assigned_depots) == 0:  # if assigned route is a empty list
                continue

            shortage_route = self._start_from_warehouse_and_go_back_to_warehouse_helper(
                assigned_depots)
            shortage_points = self.optimizer.find_shortage_points_in_route_helper(
                vehicle_idx, shortage_route)
            non_shortage_route = self.optimizer.insert_replenish_points_for_route_helper(
                shortage_points, shortage_route)

            vehicles_with_assigned_depots[vehicle_idx] = non_shortage_route

        return vehicles_with_assigned_depots

    @timer
    def generate_valid_solutions(self, number_of_solutions: int) -> List[SolutionChromosome]:
        solution_count = 0
        total_count = 0
        failed_solution_count = 0
        valid_solutions = []
        while len(valid_solutions) < number_of_solutions:
            total_count += 1
            solution = self._generate_initial_raw_solution()
            if solution in valid_solutions:
                print("**Same Answer Generated**")
                failed_solution_count += 1
                continue
            if isinstance(solution, int):
                print(f"**Depot {solution} Is Not Assigned**")
                failed_solution_count += 1
                continue

            solution_count += 1
            valid_solutions.append(solution)

            print(f"No. {solution_count} Success")
        failed_rate = failed_solution_count / total_count
        print(f"Successful Rate: {round((1 - failed_rate), 4) * 100}%")
        valid_solution_chromosomes = []
        print("Processing Solution Chromosomes...")
        # tqdm for progress tqdm(iterable)

        for solution in tqdm(valid_solutions):
            valid_solution_chromosomes.append(
                SolutionChromosome(solution, self.all_depot_names_with_time_window_constraints))
        valid_solution_chromosomes.sort()

        return valid_solution_chromosomes
