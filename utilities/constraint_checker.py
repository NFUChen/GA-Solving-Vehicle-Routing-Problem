from typing import Dict, List
from copy import deepcopy
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
from .route_status_code import RouteStatusCode


# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class ConstraintChecker(BuilderFactory):
    def __init__(self) -> None:
        super().__init__()
        self.resource_calc = RouteResourceCalculator()

    def _is_not_need_to_replenish_during_delivery(self, vehicle_idx: int, route: List[int]) -> bool:
        '''
        A solution checker for checking if a given route should replenish during delivery
        '''

        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        warehouse_depot = 0
        for depot_name in route:

            current_depot = self.depots[depot_name]
            # product is a dict
            if current_depot.depot_name == warehouse_depot:
                copy_vehicle.replenish()

            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():

                return False  # need to replenish

        return True

    def _is_replenish_one_time_can_fullfill_route_demand(self, vehicle_idx: int, route: List[int]) -> bool:
        '''
        A solution checker for checking if driver replenish one time, 
        total capacity can fullfill the total route demand
        '''
        route_demand = self.resource_calc._calculate_demand(route)
        vehicle_max_capacity = self.vehicles[vehicle_idx]._MAXIXMUM_CAPACITY

        for product, demand_quantity in route_demand.items():
            if vehicle_max_capacity[product] * 2 < demand_quantity:
                return False  # replenish one time can't fullfill route demand

        return True

    def respond_route_status(self, solution: Solution) -> List[RouteStatusCode]:
        status_codes = []
        for vehicle_idx, route in solution.items():
            if self._is_not_need_to_replenish_during_delivery(vehicle_idx, route):
                status_codes.append(RouteStatusCode.SUCCESSFUL_ROUTE)
                continue
            if self._is_replenish_one_time_can_fullfill_route_demand(vehicle_idx, route):
                status_codes.append(RouteStatusCode.SHORTAGE_ROUTE)
                continue

            status_codes.append(RouteStatusCode.FAILED_ROUTE)
        return status_codes

    def _is_not_all_depots_servered(self, solution: Solution) -> bool:
        all_depots = deepcopy(self.depots.all_depot_names)

        for route in solution.values():
            for depot_idx in route:
                if depot_idx in all_depots:
                    all_depots.remove(depot_idx)
        return len(all_depots) != 0

    def is_valid_solution(self, solution: Solution) -> bool:

        if self._is_not_all_depots_servered(solution):
            return False

        return True
