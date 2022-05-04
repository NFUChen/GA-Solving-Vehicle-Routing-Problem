class VehicleFile:
    def __init__(self, BASE_DIR) -> None:
        self.capacity = f"{BASE_DIR}/Q_k.csv"
        self.fuel_fee = f"{BASE_DIR}/B.csv"
        self.fuel_efficiency = f"{BASE_DIR}/a_k.csv"
        self.fixed_cost = f"{BASE_DIR}/fc_k.csv"
        self.depots_delivery_status = f"{BASE_DIR}/a_ik.csv" # Matrix