from DepotFile import DepotFile
from VehicleFile import VehicleFile
from DepotBuilder import DepotBuilder
from VehicleBuilder import  VehicleBuilder

class BuilderFactory:
    def __init__(self, BASE_DIR:str="dataset/9_3cars/") -> None:
        depot_files = DepotFile(BASE_DIR)
        vehicle_files = VehicleFile(BASE_DIR)
        
        self.depots = DepotBuilder(depot_files)
        self.vehicles = VehicleBuilder(vehicle_files)