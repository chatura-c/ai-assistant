from ai_assistant.core.provider import Provider
from ai_assistant.repositories.json_base_repo import BaseJsonRepository


class ProviderRepository(BaseJsonRepository[Provider]):
    def __init__(self) -> None:
        super().__init__(model_class=Provider, data_path="assets/provider.json")
