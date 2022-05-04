class DepotFile:
    def __init__(self, BASE_DIR) -> None:
        self.distance_to_other_depots = f"{BASE_DIR}/c_ij.csv" # Matrix
        self.time_to_other_depots = f"{BASE_DIR}/t_ij.csv" # Matrix
        self.demand = f"{BASE_DIR}/d_i.csv"
        self.earilest_time_can_be_delivered = f"{BASE_DIR}/e_i.csv"
        self.latest_time_must_be_delivered = f"{BASE_DIR}/l_i.csv"
        
