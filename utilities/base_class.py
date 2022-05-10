from typing import List
from .depot_file import DepotFile
from .vehicle_file import VehicleFile
from .depot_builder import DepotBuilder
from .vehicle_builder import VehicleBuilder


class BuilderFactory:
    def __init__(self, BASE_DIR: str = "./utilities/dataset/9_3cars/") -> None:
        self.depot_files = DepotFile(BASE_DIR)
        self.vehicle_files = VehicleFile(BASE_DIR)
        self.depot_builder = DepotBuilder(self.depot_files)
        self.vehicle_builder = VehicleBuilder(self.vehicle_files)

    @property
    def depots(self) -> DepotBuilder:
        return DepotBuilder(self.depot_files)

    @property
    def vehicles(self) -> VehicleBuilder:
        return VehicleBuilder(self.vehicle_files)

    

    
