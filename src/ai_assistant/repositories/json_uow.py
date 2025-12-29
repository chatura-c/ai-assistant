from ai_assistant.core.models import AssistantConfig
from ai_assistant.core.uow import AbstractUnitOfWork
from ai_assistant.repositories.json_assistant_config import JsonAssistantConfigRepository
from ai_assistant.repositories.json_profile import JsonProfileRepository
from ai_assistant.repositories.json_provider import JsonProviderRepository
from ai_assistant.repositories.keyring_safe import KeyringSafeRepository

class JsonUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.profiles = JsonProfileRepository()
        self.providers = JsonProviderRepository()
        self.secrets = KeyringSafeRepository("ai-assistant")
        self.assistants = JsonAssistantConfigRepository()

