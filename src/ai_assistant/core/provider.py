from dataclasses import dataclass

@dataclass
class Provider:
    id: str
    url: str
    api_key: str
    model: str
