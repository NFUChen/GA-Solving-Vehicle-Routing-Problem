from typing import Dict, List
from copy import deepcopy
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator

# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class ConstraintChecker(BuilderFactory):
    def __init__(self) -> None:
        super().__init__()
        self.resource_calc = RouteResourceCalculator()

    def _is_need_to_replenish_during_delivery(self, vehicle_idx: int, route: List[int]) -> bool:
        '''
        A solution checker for checking if a given route should replenish during delivery
        '''

        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        warehouse_depot = 0
        for depot_name in route[1:-1]:  # [0,1,2,3,0] -> [1,2,3]
            current_depot = self.depots[depot_name]
            # product is a dict
            if current_depot.depot_name == warehouse_depot:
                copy_vehicle.replenish()

            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():
                return True  # need to replenish

        return False

    def _is_all_depots_servered(self, solution: Solution) -> bool:
        all_depots = deepcopy(self.depots.all_depot_names)

        for route in solution.values():
            for depot_idx in route:
                if depot_idx in all_depots:
                    all_depots.remove(depot_idx)
        return len(all_depots) == 0

    def is_passing_time_window_constraints(self, vehicle_idx: int, route: List[int], checking_depot_idx: int) -> bool:
        checking_depot = self.depots[checking_depot_idx]
        current_vehicle = self.vehicles[vehicle_idx]

        total_time_of_current_route = self.resource_calc._calculate_time_for_current_route(
            vehicle_idx, route)

        if (total_time_of_current_route < checking_depot.earilest_time_can_be_delivered):
            # print("earilest_time_can_be_delivered")
            return False

        if (total_time_of_current_route > checking_depot.latest_time_must_be_delivered):
            # print("latest_time_must_be_delivered")
            return False

        if (total_time_of_current_route > current_vehicle.maximum_available_time):
            # print("maximum_available_time")
            return False

        return True

    def is_all_depot_passing_time_window_constraints(self, vehicle_idx: int, route: List[int]):
        checking_route = route[:-1]
        for checking_depot_idx in checking_route:
            if not self.is_passing_time_window_constraints(vehicle_idx, route, checking_depot_idx):
                return False

        return True
