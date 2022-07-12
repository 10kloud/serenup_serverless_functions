class BalanceState:
    def __init__(self, device_id: str, balance_status: str):
        self.device_id = device_id
        self.balance_status = balance_status

    @classmethod
    def from_dynamodb_event_image(cls, event_image: dict):
        return cls(
            device_id=event_image.get('device_id', {}).get('S', None),
            balance_status=event_image.get('balance', {}).get('S', None)
        )
