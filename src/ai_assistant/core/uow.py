
from abc import ABC
from .repository import Repository
from .models import AssistantConfig, Profile, Provider, SafeKey

class AbstractUnitOfWork(ABC):
    profiles: Repository[Profile]
    providers: Repository[Provider]
    secrets: Repository[SafeKey]
    assistants: Repository[AssistantConfig]
