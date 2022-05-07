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

            distance = self.depots[start_depot].get_distance_to_depot(
                end_depot)
            total_distance += distance

        return total_distance

    def _calculate_time(self, vehicle_idx: int, route: List[int]) -> List[int]:
        '''
        Unit: minute
        Returns total delivery time and total service time as a list for a given route.
        '''
        delivery_time = 0
        service_time = 0
        for idx in range(len(route) - 1):
            start_depot = route[idx]
            end_depot = route[idx + 1]

            delivery_time += self.depots[start_depot].get_delivery_time_to_depot(
                end_depot)
            service_time += self.vehicles[vehicle_idx].shipement_discharging_time

        return [delivery_time, service_time]

    def _calculate_time_before_depot_idx(self, vehicle_idx: int, route: List[int], target_depot_name: int) -> int:
        if len(route) < 2:  # [0]
            return 0

        delivery_time = 0
        service_time = 0
        target_depot_idx = route.index(target_depot_name)
        trimmed_route = route[:target_depot_idx + 1]

        for idx in range(len(trimmed_route) - 1):
            start_depot = route[idx]
            end_depot = route[idx + 1]
            if end_depot == target_depot_name:
                break

            delivery_time += self.depots[start_depot].get_delivery_time_to_depot(
                end_depot)
            service_time += self.vehicles[vehicle_idx].shipement_discharging_time
        total_time = delivery_time + service_time
        return total_time

    def _calculate_driver_cost(self, hourly_wage: int, time_on_duty_in_minute: int) -> int:
        '''
        Params:
        total_time_on_duty: minute
        '''

        return (time_on_duty_in_minute / 60) * hourly_wage

    def _calculate_number_of_replenishments(self, route: List[int]) -> int:
        trimmed_route = route[1:-1]  # [0,1,2,3,0] -> [1,2,3]
        total_number_of_replenishments = 0
        warehose_depot = 0
        for depot in trimmed_route:
            if depot == warehose_depot:
                total_number_of_replenishments += 1

        return total_number_of_replenishments

    # {0: [(0, 7)]

    def _get_all_route_info_as_dict(self, solution: Solution) -> Dict[int, List[Tuple[int, int]]]:
        route_info_dict = {}
        for vehicle_idx, route in solution.items():
            if len(route) == 0:
                continue
            if vehicle_idx not in route_info_dict:
                route_info_dict[vehicle_idx] = []

            for idx in range(len(route)-1):
                if idx < len(route) - 2:
                    check_start_depot = route[idx]
                    check_warehouse_depot = route[idx + 1]
                    check_end_depot = route[idx + 2]
                    if check_warehouse_depot != 0:  # this is replenish point
                        continue
                    replenish_route_info = (
                        check_start_depot, check_warehouse_depot, check_end_depot)
                    route_info_dict[vehicle_idx].append(replenish_route_info)

                start_depot = route[idx]
                end_depot = route[idx + 1]
                regular_route_info = (start_depot, end_depot)
                route_info_dict[vehicle_idx].append(regular_route_info)
        return route_info_dict

    def calculate_solution_resources(self, solusion: Solution) -> Dict[str, 'float | int']:

        route_info_dict = self._get_all_route_info_as_dict(
            solusion)  # {0: [(0, 7)]
        number_of_vehicles_assigned = len(route_info_dict)
        total_delivery_time = 0
        total_service_time = 0
        total_distance = 0
        number_of_replenishments = 0
        for vehicle_idx, route_info in route_info_dict.items():
            for start_depot_to_end_depot in route_info:
                if len(start_depot_to_end_depot) != 2:  # e.g., (1,0, 2) replenishment point
                    number_of_replenishments += 1
                    continue
                start_depot, end_depot = start_depot_to_end_depot
                total_delivery_time += self.depots[start_depot].get_delivery_time_to_depot(
                    end_depot)
                total_service_time += self.vehicles[vehicle_idx].shipement_discharging_time
                total_distance += self.depots[start_depot].get_distance_to_depot(
                    end_depot)

        fuel_fee = total_delivery_time * self.vehicles[vehicle_idx].fuel_fee
        vehicle_fixed_cost = self.vehicles[vehicle_idx].fixed_cost

        time_on_duty_in_minute = total_delivery_time + total_service_time
        driver_cost = self._calculate_driver_cost(168, time_on_duty_in_minute)

        return {"fuel_fee": fuel_fee,  # 路徑需求
                "distance": total_distance,  # 路徑距離
                "delivery_time": total_delivery_time,  # 路徑所需運送時間
                "service_time": total_service_time,  # 總卸貨時間
                "vehicle_fixed_cost": vehicle_fixed_cost,  # 載具固定成本
                "driver_cost": driver_cost,  # 司機成本
                "number_of_replenishment": number_of_replenishments,
                "number_of_vehicles_assigned": number_of_vehicles_assigned}  # 總派送車輛

    def calculate_route_resources(self, vehicle_idx: int, route: List[int]) -> Dict[str, 'float | int']:
        '''
        This method is a public API expected to expose to users.
        Functionality:
            Calculate total resources needed for 'a given route with a given vehicle'
        '''

        if len(route) == 0:
            return

        solution = {vehicle_idx: route}

        resources = self.calculate_solution_resources(solution)

        return resources
