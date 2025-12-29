from dataclasses import dataclass

@dataclass
class Profile:
    id: str
    name: str
    system_prompt: str
    picture : str

@dataclass
class Provider:
    id: str
    name: str
    url: str
    api_key: str
    model: str

    def ask(self, messages: list[str]) -> str:
        pass


@dataclass
class AssistantConfig:
    id: str
    name: str
    profile_id: str
    provider_id: str


@dataclass
class SafeKey:
    key: str
    value: str
