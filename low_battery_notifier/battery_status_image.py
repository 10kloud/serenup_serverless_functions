class BatteryStatusImage:
    def __init__(self, device_id: str, battery_status: str):
        self.device_id = device_id
        self.battery_status = battery_status

    @classmethod
    def from_dynamodb_event_image(cls, event_image: dict):
        return cls(
            device_id=event_image.get('device_id', {}).get('S', None),
            battery_status=event_image.get('battery', {}).get('S', None)
        )
