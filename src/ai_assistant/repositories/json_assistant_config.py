from ai_assistant.core.host import Host
from ai_assistant.core.models import AssistantConfig 
from ai_assistant.repositories.base_json import BaseJsonRepository


class JsonAssistantConfigRepository(BaseJsonRepository[AssistantConfig]):
    def __init__(self, data_path) -> None:
        super().__init__(model_class=AssistantConfig, data_path=data_path)

