from typing import Dict, List
import pandas as pd
from .vehicle_file import VehicleFile
from .vehicle import Vehicle


class VehicleBuilder:
    def __init__(self, file_name: VehicleFile) -> None:
        self.vehicle_fuel_fee = pd.read_csv(
            file_name.fuel_fee)
        self.vehicle_fuel_efficiency = pd.read_csv(
            file_name.fuel_efficiency)
        self.vehicle_total_fixed_cost = pd.read_csv(
            file_name.fixed_cost)
        self.vehicle_capacity = pd.read_csv(
            file_name.capacity, index_col=0)
        self.vehicle_depots_delivery_status = pd.read_csv(
            file_name.depots_delivery_status, index_col=0)

        self._number_of_vehicles = len(self.vehicle_capacity)

        self._vehicles = self.build_vehicles()

    def build_vehicles(self) -> Dict[int, Vehicle]:
        '''
        car key is 0-based.
        '''
        vehicles = {}
        for idx in range(self._number_of_vehicles):
            vehicle_name = idx
            vehicle_capacity = dict(self.vehicle_capacity.iloc[idx, :])
            vehicle_fuel_fee = self.vehicle_fuel_fee["fuel_fee"][idx]
            vehicle_fuel_efficiency = self.vehicle_fuel_efficiency["fuel_efficiency"][idx]
            vehicle_total_fixed_cost = self.vehicle_total_fixed_cost["fixed_cost"][idx]
            vehicle_depots_delivery_status = list(self.vehicle_depots_delivery_status.iloc[idx, :])

            created_vehicle = Vehicle(vehicle_capacity,
                                      vehicle_fuel_fee,
                                      vehicle_fuel_efficiency,
                                      vehicle_total_fixed_cost,
                                      vehicle_depots_delivery_status,
                                      vehicle_name)

            vehicles[vehicle_name] = created_vehicle

        return vehicles

    @property
    def all_vehicle_names(self) -> List[int]:
        return [name for name in self._vehicles.keys()]

    @property
    def sorted_vehicles(self) -> List[int]:
    
        sorted_vehicles_can_be_assigned = sorted([depot
                                               for depot in self.build_vehicles().values()]) 
        return sorted_vehicles_can_be_assigned

    def __getitem__(self, vehicle_idx: int) -> Vehicle:
        '''
        __getitem__ method is served as accessor of all depots by specifying certain key of self._depots 
        '''
        if vehicle_idx not in self._vehicles:
            raise ValueError(f"'vehicle_idx' must be one of the following: {list(self._vehicles.keys())}")

        return self._vehicles[vehicle_idx]

    def __repr__(self) -> str:
        return "".join([repr(vehicle)
                        for vehicle in
                        self._vehicles.values()])
