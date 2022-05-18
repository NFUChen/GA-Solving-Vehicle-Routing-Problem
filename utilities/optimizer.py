from typing import List, Dict
from copy import deepcopy
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class Optimizer:
    def __init__(self) -> None:
        factory = BuilderFactory()
        self.depots = factory.depots
        self.vehicles = factory.vehicles
        self.resource_calc = RouteResourceCalculator()

    def _find_shortage_points_in_route_helper(self, vehicle_idx: int, route: List[int]) -> List[int]:
        '''
        A helper function aiming to find 'shortage point' during delivery,
        returns 'depot_name' not the index of depot
        '''
        shortage_points = []
        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        for depot_name in route:
            current_depot = self.depots[depot_name]
            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():
                shortage_points.append(depot_name)
                copy_vehicle.replenish()
        return shortage_points

    def _insert_replenish_points_for_route_helper(self, replenish_points: List[int], route: List[int]) -> List[int]:
        if len(replenish_points) == 0:
            return route

        route = route.copy()
        for point in replenish_points:
            inserted_idx = route.index(point)
            route.insert(inserted_idx, 0)
        return route

    def _start_from_warehouse_and_go_back_to_warehouse_helper(self, route: List[int]) -> List[int]:
        '''
        A helper function for .generate_initial_raw_solution(),
        which adds 1 zero at the beginning and at the end of the route,
        indicating that the route should be starting from warehouse, and going back to warehouse
        '''
        return [0, *route, 0]

    def insert_warehouse_depots_and_relenish_points(self, vehicle_idx:int,route:List[int]) -> List[int]:
        copy_route = route.copy()

        shortage_route = self._start_from_warehouse_and_go_back_to_warehouse_helper(copy_route)
        shortage_points = self._find_shortage_points_in_route_helper(vehicle_idx, shortage_route)
        non_shortage_route = self._insert_replenish_points_for_route_helper(shortage_points, shortage_route)

        return non_shortage_route

