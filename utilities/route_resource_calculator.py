from typing import Dict, List, Tuple
from .base_class import BuilderFactory
Solution = Dict[int, List[int]]


class RouteResourceCalculator(BuilderFactory):
    def __init__(self) -> None:
        '''
        RouteResourceCalculator responsible for calculating the resources needed for "A GIVEN ROUTE"
        -------------------------------------------------------------------------------------------
        Params:
        depot_builder: storing information for 'EACH' depot
        vehicle: storing information for a 'GIVEN' vehicle
        route: storing a path that the input vehicle needs to go through.
        '''
        super().__init__()

    def _calculate_demand(self, route: List[int]) -> Dict[str, int]:
        total_demand = {}
        for depot_id in route:
            for product in self.depots[depot_id].demand.keys():
                if product not in total_demand:
                    total_demand[product] = 0
                total_demand[product] += self.depots[depot_id].demand[product]
        return total_demand

    def _calculate_distance(self, route: List[int]) -> int:
        '''
        Unit: km
        '''
        total_distance = 0
        for idx in range(len(route) - 1):
            start_depot = route[idx]
            end_depot = route[idx + 1]

            distance = self.depots[start_depot].get_distance_to_depot(end_depot)
            total_distance += distance

        return total_distance

    def _calculate_time_for_current_route(self, vehicle_idx: int, route: List[int]) -> int:
        if len(route) < 2:  # [], [1] -> no distance
            return 0

        delivery_time = 0
        service_time = 0

        for idx in range(len(route) - 1):
            start_depot = route[idx]
            end_depot = route[idx + 1]

            delivery_time += self.depots[start_depot].get_delivery_time_to_depot(end_depot)
            service_time += self.vehicles[vehicle_idx].shipement_discharging_time
        total_time = delivery_time + service_time
        return total_time

    def _calculate_driver_cost(self, hourly_wage: int, time_on_duty_in_minute: int) -> int:
        '''
        Params:
        total_time_on_duty: minute
        '''

        return (time_on_duty_in_minute / 60) * hourly_wage

    # {0: [(0, 7)]
    def _get_all_route_info_as_dict(self, solution: Solution) -> Dict[int, 'List[Tuple[int, int] | Tuple[int, int, int]']:
        route_info_dict = {}
        for vehicle_idx, route in solution.items():
            if len(route) == 0:
                continue
            if vehicle_idx not in route_info_dict:
                route_info_dict[vehicle_idx] = []

            for idx in range(len(route)-1):
                start_depot = route[idx]
                end_depot = route[idx + 1]
                regular_route_info = (start_depot, end_depot)
                route_info_dict[vehicle_idx].append(regular_route_info)
                if idx < len(route) - 2:
                    check_start_depot = route[idx]
                    check_warehouse_depot = route[idx + 1]
                    check_end_depot = route[idx + 2]
                    if check_warehouse_depot != 0: 
                        continue
                    replenish_route_info = (check_start_depot, check_warehouse_depot, check_end_depot)
                    route_info_dict[vehicle_idx].append(replenish_route_info)
        return route_info_dict

    def calculate_solution_resources(self, solution: Solution) -> Dict[str, 'float | int']:
        '''
        This method is a public API expected to expose to users.
        Functionality:
            Calculate total resources needed for 'a given solution'
        '''

        route_info_dict = self._get_all_route_info_as_dict(
            solution)  # {0: [(0, 7)]
        number_of_vehicles_assigned = len(route_info_dict)
        total_delivery_time = 0
        total_service_time = 0
        total_distance = 0
        number_of_replenishments = 0
        vehicle_total_fixed_cost = 0
        for vehicle_idx, route_info in route_info_dict.items():
            for start_depot_to_end_depot in route_info:
                if len(start_depot_to_end_depot) != 2:  # e.g., (1,0, 2) replenishment point
                    number_of_replenishments += 1
                    continue
                start_depot, end_depot = start_depot_to_end_depot
                total_delivery_time += self.depots[start_depot].get_delivery_time_to_depot(end_depot)
                total_service_time += self.vehicles[vehicle_idx].shipement_discharging_time
                total_distance += self.depots[start_depot].get_distance_to_depot(end_depot)
                
            vehicle_total_fixed_cost += self.vehicles[vehicle_idx].fixed_cost
        fuel_fee = total_distance * self.vehicles[vehicle_idx].fuel_fee * self.vehicles[vehicle_idx].fuel_efficiency
        time_on_duty_in_minute = total_delivery_time + total_service_time
        driver_cost = self._calculate_driver_cost(60, time_on_duty_in_minute)

        return {"fuel_fee": fuel_fee,
                "distance": total_distance,
                "delivery_time": total_delivery_time,
                "service_time": total_service_time,  # 總卸貨時間
                "total_time": time_on_duty_in_minute,
                "vehicle_total_fixed_cost": vehicle_total_fixed_cost,
                "driver_cost": driver_cost,
                "number_of_replenishment": number_of_replenishments,
                "number_of_vehicles_assigned": number_of_vehicles_assigned}

    def calculate_route_resources(self, vehicle_idx: int, route: List[int]) -> Dict[str, 'float | int']:
        '''
        This method is a public API expected to expose to users.
        Functionality:
            Calculate total resources needed for 'a given route with a given vehicle'
        '''

        if len(route) == 0:
            return

        mock_solution = {vehicle_idx: route}

        resources = self.calculate_solution_resources(mock_solution)

        return resources
