from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Profile:
    name: str
    system_prompt: str


@dataclass
class Provider(ABC):
    id: str
    url: str
    api_key: str
    model: str

    @abstractmethod
    def ask(self, messages: list[str]) -> str:
        pass


@dataclass
class SafeKey:
    key: str
    value: str
