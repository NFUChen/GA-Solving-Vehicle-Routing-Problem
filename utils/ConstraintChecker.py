from typing import Dict, List
from copy import deepcopy
from .base_class import BuilderFactory
from RouteResourceCalculator import RouteResourceCalculator
from SolutionStatusCode import SolutionStatusCode

Solution = Dict[int,List[int]] # e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}

class ConstraintChecker(BuilderFactory):
    def __init__(self) -> None:
        super().__init__()
        self.resource_calc = RouteResourceCalculator()
    
    def _is_not_need_to_replenish_during_delivery(self,vehicle_idx:int,route:List[int]) -> bool:
        '''
        A solution checker for checking if a given route should replenish during delivery
        '''
        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        for depot_name in route:
            current_depot = self.depots[depot_name]
            # product is a dict
            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():
                return False # need to replenish
        
        return True
            
    
    
    def _is_replenish_one_time_can_fullfill_route_demand(self, vehicle_idx:int, route:List[int]) -> bool:
        '''
        A solution checker for checking if driver replenish one time, 
        total capacity can fullfill the total route demand
        '''
        route_demand = self.resource_calc._calculate_demand(route)
        vehicle_capacity = self.vehicles[vehicle_idx].capacity
        
            
        for product, demand_quantity in route_demand.items():
            if vehicle_capacity[product] * 2 < demand_quantity:
                return False # replenish one time can't fullfill route demand
        
        return True
    
    
        
        
    def solution_report(self, solution:Solution) -> SolutionStatusCode:
        '''
        A function produce report for solution report
        '''
        VALIDATORS_WITH_STATUS_CODES = (
            (self._is_not_need_to_replenish_during_delivery, SolutionStatusCode.NON_SHORTAGE_ROUTE),
            (self._is_replenish_one_time_can_fullfill_route_demand, SolutionStatusCode.SHORTAGE_ROUTE),
            
            (True, SolutionStatusCode.FAILED_ROUTE)
        )
        
        for vehicle_idx, route in solution.items():
            for validator_with_statu_code in VALIDATORS_WITH_STATUS_CODES:
                validator, status_code = validator_with_statu_code
                if validator(vehicle_idx, route):
                    return status_code