from typing import List, Dict


class Vehicle:
    def __init__(self,
                 capacity: int,
                 fuel_fee: int,
                 fuel_efficiency: float,
                 fixed_cost: float,
                 depots_delivery_status: List[int],
                 vehicle_name: str = None,
                 shipement_discharging_time: int = 20,
                 maximum_available_time: int = 480
                 ) -> None:
        '''
        Data Source:
        capacity:Q_k.csv
        fuel_fee: B.csv
        fuel_efficiency: a_k.csv
        fixed_cost: f_ck.csv
        depot_can_be_delivered: a_ik.csv
        '''
        self._MAXIXMUM_CAPACITY = capacity

        self.capacity = capacity
        self.fuel_fee = fuel_fee
        self.fuel_efficiency = fuel_efficiency
        self.fixed_cost = fixed_cost
        self.depots_delivery_status = {depot_name: is_can_be_delivered
                                       for depot_name, is_can_be_delivered in enumerate(depots_delivery_status)}
        self._available_depot = [unavailable
                                 for unavailable in self.depots_delivery_status
                                 if self.depots_delivery_status[unavailable] == 1]
        self._all_depot_names = [
            name for name in self.depots_delivery_status]
        self.vehicle_name = vehicle_name
        # 固定服務時間(卸貨)為20分鐘
        self.shipement_discharging_time = shipement_discharging_time
        # 車輛使用時間限制480分鐘
        self.maximum_available_time = maximum_available_time

    def __repr__(self) -> str:
        capacity = f"Capacity: {self.capacity}\n"
        fuel_fee = f"Fuel Fee: ${self.fuel_fee}\n"
        fuel_efficiency = f"Fuel Efficiency: {self.fuel_efficiency} l/km\n"
        fixed_cost = f"Fixed Cost: ${self.fixed_cost}\n"
        depots_delivery_status = f"Depots Delivery Status: {self.depots_delivery_status}\n"
        sep = "-" * 60 + "\n"

        return "".join(
            [capacity,
             fuel_fee,
             fuel_efficiency,
             fixed_cost,
             depots_delivery_status,
             sep]
        )

    def discharge(self, demand: Dict[str, int]) -> None:
        for product, demand_quantity in demand.items():
            if product not in self.capacity:
                raise TypeError(
                    f"Product mismath, Vechicle doesn't have '{product}'")
            self.capacity[product] -= demand_quantity

    def replenish(self):
        self.capacity = self._MAXIXMUM_CAPACITY

    def is_out_of_stock(self) -> bool:
        for product in self.capacity:
            if self.capacity[product] < 0:
                return True
        return False

    def is_depot_can_be_delivered(self, depot_id: int) -> bool:
        '''
        P.S. depot_id is 1 based
        '''
        if not self._is_valid_depot(depot_id):
            raise ValueError(
                f"'depot_id' must be one of the following: {self._all_depot_names}")

        # return self.depots_delivery_status[depot_id] == 1
        return depot_id in self._available_depot

    def _is_valid_depot(self, depot_id: int) -> bool:
        return depot_id in self._all_depot_names


if __name__ == "__main__":
    vehicle1 = Vehicle(capacity=150,
                       fuel_fee=24,
                       fuel_efficiency=0.1,
                       fixed_cost=1000,
                       depots_delivery_status=[0, 1, 1, 1, 1, 1, 1, 1, 1])

    print(vehicle1.is_depot_can_be_delivered())
