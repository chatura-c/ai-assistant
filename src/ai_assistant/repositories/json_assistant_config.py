from ai_assistant.core.models import AssistantConfig 
from ai_assistant.repositories.base_json import BaseJsonRepository


class JsonAssistantConfigRepository(BaseJsonRepository[AssistantConfig]):
    def __init__(self) -> None:
        super().__init__(model_class=AssistantConfig, data_path="assets/assistants.json")

