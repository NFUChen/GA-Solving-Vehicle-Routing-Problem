from typing import Dict, List
from .base_class import BuilderFactory


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

    def calculate_route_resources(self, vehicle_idx: int, route: List[int]) -> 'Dict[str, int|Dict[str, int]]':
        '''
        This method is a public API expected to expose to users.
        Functionality:
            Calculate total resources needed for 'a given route with a given vehicle'
        '''

        if len(route) == 0:
            return

        route_distance = self._calculate_distance(route)
        route_delivery_time, route_service_time = self._calculate_time(
            vehicle_idx, route)
        fuel_fee = route_delivery_time * self.vehicles[vehicle_idx].fuel_fee
        vehicle_fixed_cost = self.vehicles[vehicle_idx].fixed_cost

        time_on_duty_in_minute = route_delivery_time + route_service_time
        driver_cost = self._calculate_driver_cost(168, time_on_duty_in_minute)

        return {"fuel_fee": fuel_fee,  # 路徑需求
                "distance": route_distance,  # 路徑距離
                "delivery_time": route_delivery_time,  # 路徑所需運送時間
                "service_time": route_service_time,  # 總卸貨時間
                "vehicle_fixed_cost": vehicle_fixed_cost,  # 載具固定成本
                "driver_cost": driver_cost}  # 司機成本
