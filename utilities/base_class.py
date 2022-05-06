from .depot_file import DepotFile
from .vehicle_file import VehicleFile
from .depot_builder import DepotBuilder
from .vehicle_builder import VehicleBuilder


class BuilderFactory:
    def __init__(self, BASE_DIR: str = "./utilities/dataset/65_22cars/") -> None:
        self.depot_files = DepotFile(BASE_DIR)
        self.vehicle_files = VehicleFile(BASE_DIR)
        self.depot_builder = DepotBuilder(self.depot_files)
        self.vehicle_builder = VehicleBuilder(self.vehicle_files)

    @property
    def depots(self):
        return DepotBuilder(self.depot_files)

    @property
    def sorted_depots(self):
        '''
        This property gets all depots sorted by latest time must be delivred.
        '''
        sorted_depots_to_be_assigned = sorted([depot
                                               for depot in self.depot_builder._build_depots().values()
                                               if depot.depot_name != 0])  # 0 is warehouse
        return sorted_depots_to_be_assigned

    @property
    def vehicles(self):
        return VehicleBuilder(self.vehicle_files)
