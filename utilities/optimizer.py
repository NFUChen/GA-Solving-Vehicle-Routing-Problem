from typing import List, Dict
from copy import deepcopy
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
from .constraint_checker import ConstraintChecker
# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]
checker = ConstraintChecker()


class Optimizer(BuilderFactory):
    def __init__(self):
        super().__init__()
        self.resource_calc = RouteResourceCalculator()

    def find_shortage_points_in_route(self, vehicle_idx: int, route: List[int]) -> List[int]:
        '''
        A helper function aiming to find 'shortage point' during delivery,
        returns 'depot_name' not the index of depot
        '''
        shortage_points = []
        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        for depot_name in route:
            current_depot = self.depots[depot_name]
#             print("Current Capacity", copy_vehicle.capacity)
#             print("Demand",current_depot.demand)
            # product is a dict
            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():
                shortage_points.append(depot_name)
                copy_vehicle.replenish()
        return shortage_points

    def insert_replenish_points_for_route(self, replenish_points: List[int], route: List[int]) -> List[int]:
        if len(replenish_points) == 0:
            return route

        route = route.copy()
        for point in replenish_points:
            inserted_idx = route.index(point)
            route.insert(inserted_idx, 0)
        return route

    def _find_optimal_replenish_point_in_route(self, vehicle_idx: int, route: List[int]) -> List[int]:
        '''
        Opitmal point is based on distance,
        thus, using RouteResourceCalculator._calculate_distance to find optimal point
        '''
        shortage_point = self._find_shortage_point_in_route(vehicle_idx, route)
        possible_routes = []
        warehouse_depot = 0
        for idx in range(len(route) - 1):  # excluding 0(warehouse)
            route_copy = route.copy()
            current_depot = route[idx]
            previous_depot = route[idx - 1]

            if (current_depot == 0 or previous_depot == 0):
                # preventing situation like [0,(0), 1,2(0),0] X
                continue

            route_copy.insert(idx, warehouse_depot)

            total_distance = self.resource_calc._calculate_distance(route_copy)

            possible_routes.append(
                (route_copy, total_distance)
            )

            if current_depot == shortage_point:
                break
        # need to further check if the possible route is actually a SUCCESSFUL_ROUTE
        possible_routes = [(_route, _total_distance)
                           for _route, _total_distance in possible_routes
                           if checker._is_not_need_to_replenish_during_delivery(vehicle_idx, _route)]

        possible_routes.sort(
            key=lambda route_with_distance: route_with_distance[1])
        # print(vehicle_idx, possible_routes)
        if len(possible_routes) == 0:
            return []

        shortest_route, _ = possible_routes[0]

        return shortest_route

    def optimize(self, vehicle_idx: int, route: List[int]) -> List[int]:

        shortest_route = self._find_optimal_replenish_point_in_route(
            vehicle_idx, route)

        return shortest_route
