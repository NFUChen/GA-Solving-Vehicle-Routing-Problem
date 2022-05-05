from typing import List


class Depot:
    def __init__(self,
                 demand: int,
                 earilest_time_can_be_delivered: int,
                 latest_time_must_be_delivered: int,
                 distance_to_other_depots: List[int],
                 delivery_time_to_other_depots: List[int],
                 vehicle_depots_delivery_status: List[int],
                 depot_name: str = None) -> None:
        '''
        Data Source:
        demand: d_i.csv
        earilest_time_can_be_delivered: e_i.csv
        latest_time_must_be_delivered: l_i.csv
        distance_to_other_depot: c_ij.csv
        time_to_other_depot: t_ij.csv
        '''
        self.depot_name = depot_name
        self.demand = demand
        self.earilest_time_can_be_delivered = earilest_time_can_be_delivered
        self.latest_time_must_be_delivered = latest_time_must_be_delivered
        self._distance_to_other_depots = {depot_name: distance
                                          for depot_name, distance in enumerate(distance_to_other_depots)}
        self._delivery_time_to_other_depots = {depot_name: time
                                               for depot_name, time in enumerate(delivery_time_to_other_depots)}
        self._vehicle_depots_delivery_status = {
            depot_name: delivery_status for depot_name, delivery_status in enumerate(vehicle_depots_delivery_status)
        }
        self._all_depot_names = [
            name for name in self._distance_to_other_depots]
        self._available_vehicles = [
            vehicle_idx for vehicle_idx, status in self._vehicle_depots_delivery_status.items()
            if status == 1]
    @property
    def available_vehicles(self) -> List[int]:
        return self._available_vehicles
        

    def __repr__(self) -> str:
        depot_name = f"Depot Name: {self.depot_name}\n"
        demand = f"Demand: {self.demand}\n"
        earilest_time_can_be_delivered = f"Earilest Time Can Be Delivered: Starting Time after {self.earilest_time_can_be_delivered} Mins\n"
        latest_time_must_be_delivered = f"Latest Time Must Be Delivered: Starting Time after {self.latest_time_must_be_delivered} Mins\n"
        _distance_to_other_depots = f"Distance to Other Depots: {self._distance_to_other_depots}\n"
        _delivery_time_to_other_depots = f"Delivery Time to Other Depots: {self._delivery_time_to_other_depots}\n"
        _availabe_vehicles = f"Available Vehices: {self._available_vehicles}\n"
        sep = "-" * 60 + "\n"

        return "".join(
            [depot_name,
             demand,
             earilest_time_can_be_delivered,
             latest_time_must_be_delivered,
             _distance_to_other_depots,
             _delivery_time_to_other_depots,
            _availabe_vehicles,
             sep]
        )

    def get_distance_to_depot(self, depot_id: str) -> int:

        if not self._is_valid_depot(depot_id):
            raise ValueError(
                f"'depot_id' must be one of the following: {self._all_depot_names}")

        distance = self._distance_to_other_depots[depot_id]

        return distance

    def get_delivery_time_to_depot(self, depot_id: str) -> int:

        if not self._is_valid_depot(depot_id):
            raise ValueError(
                f"'depot_id' must be one of the following: {self._all_depot_names}")

        delivery_time = self._delivery_time_to_other_depots[depot_id]

        return delivery_time

    def _is_valid_depot(self, depot_id: int) -> bool:
        return depot_id in self._all_depot_names
