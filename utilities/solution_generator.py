from typing import List, Dict
from copy import deepcopy
from time import time
from random import choice
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
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s', end="\t")
        return result
    return wrap_func


class SolutionGenerator(BuilderFactory):
    def __init__(self, constraint_checker: ConstraintChecker = ConstraintChecker()) -> None:
        super().__init__()
        if not isinstance(constraint_checker, ConstraintChecker):
            raise TypeError(f"'constraint_checker' is not a ConstraintChecker instance, given {type(constraint_checker)} type")
        self.checker = constraint_checker
        self.optimizer = Optimizer()
        self.resource_calc = RouteResourceCalculator()

        self.all_depot_names = self.depots.all_depot_names
        self.all_vehicle_names = self.vehicles.all_vehicle_names
        self.sorted_vehicles_can_be_assigned = self.vehicle_builder.sorted_vehicles
        


        self.all_depot_names_with_time_window_constraints = self.depot_builder.all_depot_names_with_time_window_constraint
        self.vehicles_with_assigned_depots = {vehicle_name: []
                                              for vehicle_name in self.all_vehicle_names}

        print(f"Available Vehicle Names: {self.all_vehicle_names}")
        print(f"Available Depot Names: {self.all_depot_names}")
        print(f"All Depots With Time Window Constraints: {self.all_depot_names_with_time_window_constraints}")

    def _start_from_warehouse_and_go_back_to_warehouse_helper(self, route: List[int]) -> List[int]:
        '''
        A helper function for .generate_initial_raw_solution(),
        which adds 1 zero at the beginning and at the end of the route,
        indicating that the route should be starting from warehouse, and going back to warehouse
        '''
        return [0, *route, 0]

    @timer
    def _generate_initial_raw_solution(self) -> 'Solution | List[int]':
        '''
        .generate_initial_raw_solution generates a raw solution that is subject to further check with constraint checker (i.e., ConstraintChecker)

        P.S. This method generates a solution at least doesn't violate the constraint that an undeliverable depot is assigned to a given vehicle.

        '''
        # [1,2 ...., n], 0 (warehouse) should be excluded
        # all_depots_to_be_assigned = deepcopy(self.sorted_depots_to_be_assigned)
        vehicles_with_assigned_depots = deepcopy(self.vehicles_with_assigned_depots)  # {0:[], 1:[], 2:[] ..., n:[]}
        
        early_assigned_depots = self.depot_builder.depots_need_to_be_assigned_early
        regular_depots = self.depot_builder.depots_without_time_window_constraints
        late_assigned_depots = self.depot_builder.depots_need_to_be_assigned_late
        
        order_of_depots_assigning = [early_assigned_depots, regular_depots]

        while (True):
            current_vehicle_idx = choice(self.all_vehicle_names)
            current_assigned_route = vehicles_with_assigned_depots[current_vehicle_idx]
            for existing_depots in order_of_depots_assigning:
                self._assign_depots(vehicles_with_assigned_depots, current_vehicle_idx, existing_depots)

            if len(early_assigned_depots) == 0 and len(regular_depots) == 0:
                break

        vehicles_with_task = [
            vehicle_idx 
            for vehicle_idx, assigned_route in vehicles_with_assigned_depots.items()
            if len(assigned_route) != 0
        ]

        for vehicle_idx in vehicles_with_task:
            for depot_idx in late_assigned_depots.copy():
                current_vehicle = self.vehicles[vehicle_idx]
                current_route = vehicles_with_assigned_depots[vehicle_idx]
                if (current_vehicle.is_depot_can_be_delivered(depot_idx)  and 
                self.checker.is_passing_time_window_constraints(vehicle_idx, current_route, depot_idx) ):
                    vehicles_with_assigned_depots[vehicle_idx].append(depot_idx)
                    late_assigned_depots.remove(depot_idx)
        if len(late_assigned_depots) != 0:
            return late_assigned_depots


        # use helper function i.e., [0, *route, 0]
        for vehicle_idx, assigned_depots in vehicles_with_assigned_depots.items():
            if len(assigned_depots) == 0:  # if assigned route is a empty list
                continue

            shortage_route = self._start_from_warehouse_and_go_back_to_warehouse_helper(assigned_depots)
            shortage_points = self.optimizer.find_shortage_points_in_route_helper(vehicle_idx, shortage_route)
            non_shortage_route = self.optimizer.insert_replenish_points_for_route_helper(shortage_points, shortage_route)

            vehicles_with_assigned_depots[vehicle_idx] = non_shortage_route
        return vehicles_with_assigned_depots

    def _assign_depots(self, vehicles_with_assigned_depots:Dict[int, List[int]], current_vehicle_idx:int,existing_depots:List[int]) -> None:
        if (existing_depots) == 0:
            return
        current_assigned_route = vehicles_with_assigned_depots[current_vehicle_idx]
        for depot in existing_depots:
            if not depot in self.vehicles[current_vehicle_idx]._available_depots:
                continue
            if not self.checker.is_passing_time_window_constraints(current_vehicle_idx, current_assigned_route, depot):
                continue
            current_assigned_route.append(depot)
            existing_depots.remove(depot)
        
        vehicles_with_assigned_depots[current_vehicle_idx] = current_assigned_route




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
            if isinstance(solution, list):
                print(f"**Depot {solution} Not Assigned**")
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
