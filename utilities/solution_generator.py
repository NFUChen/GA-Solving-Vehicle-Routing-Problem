from typing import List, Dict
from random import choice
from urllib import response

from .constraint_checker import ConstraintChecker
from .base_class import BuilderFactory
from .optimizer import Optimizer
from .solution_chromosome import SolutionChromosome
from .route_status_code import RouteStatusCode

# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


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

    def _start_from_warehouse_and_go_back_to_warehouse_helper(self, route: List[int]) -> List[int]:
        '''
        A helper function for .generate_initial_raw_solution(), 
        which adds 1 zero at the beginning and at the end of the route, 
        indicating that the route should be starting from warehouse, and going back to warehouse
        '''
        return [0, *route, 0]

    def _generate_initial_raw_solution(self) -> Solution:
        '''
        .generate_initial_raw_solution generates a raw solution that is subject to further check with constraint checker (i.e., ConstraintChecker)

        P.S. This method generates a solution at least doesn't violate the constraint that an undeliverable depot is assigned to a given vehicle.

        '''
        # [1,2 ...., n], 0(warehouse) should be excluded
        all_depots_to_be_assigned = [
            name for name in self.all_depot_names if name != 0]

        vehicles_with_assigned_depots = {vehicle_name: []
                                         for vehicle_name in self.all_vehicle_names}  # {0:[], 1:[], 2:[] ..., n:[]}

        # while there exists any depot in all_depots_to_be_assigned
        while (len(all_depots_to_be_assigned) > 0):
            selected_vehicle = choice(self.all_vehicle_names)
            selected_depot = all_depots_to_be_assigned.pop()
            if not self.vehicles[selected_vehicle].is_depot_can_be_delivered(selected_depot):
                continue

            vehicles_with_assigned_depots[selected_vehicle].append(
                selected_depot)

        # use helper function i.e., [0, *route, 0]
        for vehicle_name, assigned_depots in vehicles_with_assigned_depots.items():
            if len(assigned_depots) == 0:  # if assigned route is a empty list
                continue

            vehicles_with_assigned_depots[vehicle_name] = self._start_from_warehouse_and_go_back_to_warehouse_helper(
                assigned_depots)

        return vehicles_with_assigned_depots

    def generate_valid_solutions(self, number_of_solutions: int) -> List[SolutionChromosome]:
        valid_solutions = []
        while (len(valid_solutions) < number_of_solutions):
            solution = self._generate_initial_raw_solution()
            if solution in valid_solutions:
                continue
            # e.g. ,[2,1,1]
            route_status_reponse = self.checker.respond_route_status(
                solution)

            if RouteStatusCode.FAILED_ROUTE in route_status_reponse:
                continue

            if RouteStatusCode.SHORTAGE_ROUTE in route_status_reponse:
                shortage_vehicle_idx = [vehicle_idx
                                        for vehicle_idx, response in enumerate(route_status_reponse)
                                        if response == RouteStatusCode.SHORTAGE_ROUTE]

                for vehicle_idx in shortage_vehicle_idx:
                    shortage_route = solution[vehicle_idx]
                    solution[vehicle_idx] = self.optimizer.optimize(
                        vehicle_idx, shortage_route)
                    if len(shortage_route) == 0:
                        continue
                    # print(shortage_vehicle_idx,
                    #       route_status_reponse, solution[vehicle_idx])

            if self.checker.is_valid_solution(solution):
                valid_solutions.append(solution)

        return valid_solutions
