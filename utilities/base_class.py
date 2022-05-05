from .depot_file import DepotFile
from .vehicle_file import VehicleFile
from .depot_builder import DepotBuilder
from .vehicle_builder import VehicleBuilder


class BuilderFactory:
    def __init__(self, BASE_DIR: str = "./utilities/dataset/9_3cars/") -> None:
        self.depot_files = DepotFile(BASE_DIR)
        self.vehicle_files = VehicleFile(BASE_DIR)
        # self.depots = DepotBuilder(depot_files)
        # self.vehicles = VehicleBuilder(vehicle_files)

    @property
    def depots(self):
        return DepotBuilder(self.depot_files)

    @property
    def vehicles(self):
        return VehicleBuilder(self.vehicle_files)
