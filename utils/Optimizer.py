from typing import List, Dict
from copy import deepcopy
from .base_class import BuilderFactory
from RouteResourceCalculator import RouteResourceCalculator
Solution = Dict[int,List[int]] # e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
class Optimizer(BuilderFactory):
    def __init__(self):
        super().__init__()
        self.resource_calc = RouteResourceCalculator()
        
    def _find_shortage_point_in_route(self, vehicle_idx:int,route:List[int]) -> int:
        '''
        A helper function aiming to find 'shortage point' during delivery, 
        returns 'depot_name' not the index of depot
        '''
        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        for depot_name in route:
            current_depot = self.depots[depot_name]
#             print("Current Capacity", copy_vehicle.capacity)
#             print("Demand",current_depot.demand)
            
            # product is a dict
            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():
                return depot_name
            
    
    def _find_optimal_replenish_point_in_route(self, vehicle_idx:int,route:List[int]) -> List[int]:
        '''
        Opitmal point is based on distance, 
        thus, using RouteResourceCalculator._calculate_distance to find optimal point
        '''
        shortage_point = self._find_shortage_point_in_route(vehicle_idx,route)
        possible_solutions = []
        warehouse_depot = 0
        for idx in range(len(route) - 1): # excluding 0(warehouse)
            route_copy = route.copy()
            current_depot = route[idx]
            previous_depot = route[idx - 1]
            
            
            if (current_depot == 0 or previous_depot == 0):
                 #preventing situation like [0,(0), 1,2(0),0] X
                continue
                           
            route_copy.insert(idx, warehouse_depot)

            total_distance = self.resource_calc._calculate_distance(route_copy)
            
            possible_solutions.append(
                (route_copy, total_distance)
            )
            
            if current_depot == shortage_point:
                break
        
        possible_solutions.sort(key= lambda route_with_distance: route_with_distance[1])
        
        if len(possible_solutions) == 0:
            return route
        
        shortest_route, _ = possible_solutions[0]
        
        return shortest_route
    
    def optimize(self, solution:Solution) -> Solution:
        solution = deepcopy(solution)
        for vehicle_idx, route in solution.items():
            solution[vehicle_idx] = self._find_optimal_replenish_point_in_route(vehicle_idx,route)
        return solution