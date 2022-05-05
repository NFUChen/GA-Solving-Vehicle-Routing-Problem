from typing import Dict, List
import pandas as pd
from .depot_file import DepotFile
from .depot import Depot


class DepotBuilder:
    def __init__(self, file_name: DepotFile) -> None:
        self.depot_distance = pd.read_csv(
            file_name.distance_to_other_depots, index_col=0).applymap(lambda distance: distance / 1000)
        self.depot_time = pd.read_csv(
            file_name.time_to_other_depots, index_col=0).applymap(lambda time: time / 100)
        self.depot_demand = pd.read_csv(
            file_name.demand, index_col=0).applymap(lambda demand: int(demand))
        self.depot_earilest_time_can_be_delivered = pd.read_csv(
            file_name.earilest_time_can_be_delivered)
        self.depot_latest_time_must_be_delivered = pd.read_csv(
            file_name.latest_time_must_be_delivered)

        self.vehicle_depots_delivery_status = pd.read_csv(
            file_name.depots_delivery_status, index_col=0).transpose()

        self._number_of_depots = len(self.depot_demand)

        self._depots = self._build_depots()

    def _build_depots(self) -> Dict[int, Depot]:
        '''
        depot key is 0-based.
        '''
        depots = {}
        for idx in range(self._number_of_depots):
            depot_name = idx
            depot_demand = dict(self.depot_demand.iloc[idx, :])
            depot_earilest_time_can_be_delivered = self.depot_earilest_time_can_be_delivered[
                "earilest_time_can_be_delivered"][idx]
            depot_latest_time_must_be_delivered = self.depot_latest_time_must_be_delivered[
                "latest_time_must_be_delivered"][idx]
            depot_distance = list(self.depot_distance.iloc[idx, :])
            depot_time = list(self.depot_time.iloc[idx, :])
            vehicle_depots_delivery_status = list(
                self.vehicle_depots_delivery_status.iloc[idx, :]
            )

            created_depot = Depot(depot_demand,
                                  depot_earilest_time_can_be_delivered,
                                  depot_latest_time_must_be_delivered,
                                  depot_distance,
                                  depot_time,
                                  vehicle_depots_delivery_status,
                                  depot_name)
            depots[depot_name] = created_depot

        return depots

    @property
    def all_depot_names(self) -> List[int]:
        return [name for name in self._depots.keys()]

    def __getitem__(self, depot_idx: int) -> Depot:
        '''
        __getitem__ method is served as accessor of all depots by specifying certain key of self._depots 
        '''
        if depot_idx not in self._depots:
            raise ValueError(
                f"'depot_idx' must be one of the following: {list(self._depots.keys())}")

        return self._depots[depot_idx]

    def __repr__(self) -> str:
        return "".join([repr(depot)
                        for depot in
                        self._depots.values()])
