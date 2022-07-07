class BraceletMetric:
    def __init__(self, device_id: str, customer_id: str, serendipity: float, battery_level: float,
                 measured_at: str, balance: float):
        self.device_id = device_id
        self.customer_id = customer_id
        self.serendipity = serendipity
        self.battery_level = battery_level
        self.measured_at = measured_at
        self.balance = balance

    @classmethod
    def from_dict(cls, bracelet_data: dict):
        return cls(
            device_id=bracelet_data.get("device_id", None),
            customer_id=bracelet_data.get("customer_id", None),
            serendipity=bracelet_data.get("serendipity", None),
            battery_level=bracelet_data.get("battery_level", None),
            measured_at=bracelet_data.get("measured_at", None),
            balance=bracelet_data.get("balance", None)
        )
