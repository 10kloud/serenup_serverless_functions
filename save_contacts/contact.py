class Contact:
    def __init__(self, endpoint: str, protocol: str, category: str):
        self.endpoint = endpoint
        self.protocol = protocol
        self.category = category

    @classmethod
    def from_json(cls, d: dict):
        return cls(
            endpoint=d['endpoint'],
            protocol=d['protocol'],
            category=d['category']
        )
