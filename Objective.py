from typing import Callable, List
from Vehicle import Vehicle
from Depot import Depot

class Objective:
    def __init__(self, vehicles:List[Vehicle], depots:List[Depot]) -> None:
        '''
        FCk: 車輛k的固定成本(單位：元)。
        Ykl:
        Cij: 配送路徑(i, j)的距離(單位：公里)。
        αk: 車輛k的燃油效率(單位：公升/公里)。
        β: 燃油費(單位：元/公升)
        Xijkr: 車輛k第r趟次是否有行駛路段(i, j)
        Γ: 車輛司機員的單位時間薪資成本(單位：元/分鐘)。
        TRkr: 車輛k第r趟次的花費時間(單位：分鐘)。

        總配送車數最小化為主要目標，
        降低總配送距離與減少每趟次的花費時間為次要目標，
        以求取最佳的配送路線。
        所以目標函數(1)為最小化車輛的固定成本、
        車輛行駛的距離成本、每趟次花費的司機員薪資成本。
        '''
        self.vehicles = vehicles
        self.depots = depots


def objective_func() -> Callable:
    pass

    