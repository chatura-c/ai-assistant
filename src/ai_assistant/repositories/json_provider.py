from ai_assistant.core.host import Host
from ai_assistant.core.models import Provider
from ai_assistant.repositories.base_json import BaseJsonRepository


class JsonProviderRepository(BaseJsonRepository[Provider]):
    def __init__(self, data_path) -> None:
        super().__init__(model_class=Provider, data_path=data_path)
