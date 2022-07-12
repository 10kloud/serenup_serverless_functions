import base64
import json


class BraceletMetric:
    def __init__(self, device_id: str, customer_id: str, serendipity: float, battery_level: float,
                 measured_at: str, balance: float):
        self.device_id = device_id
        self.customer_id = customer_id
        self.serendipity = serendipity
        self.battery_level = battery_level
        self.measured_at = measured_at
        self.balance = balance

    @property
    def battery_status(self) -> str:
        return "CHARGE" if self.battery_level > 20 else "LOW_BATTERY"

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

    @classmethod
    def from_kinesis_record(cls, record: dict[str, dict]):
        return cls.from_dict(
            json.loads(
                base64.b64decode(
                    record['kinesis']['data']
                )
            )
        )
