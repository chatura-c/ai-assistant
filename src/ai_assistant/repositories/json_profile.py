from ai_assistant.core.host import Host
from ai_assistant.core.models import Profile
from ai_assistant.repositories.base_json import BaseJsonRepository

class JsonProfileRepository(BaseJsonRepository[Profile]):
    def __init__(self, data_path) -> None:
        super().__init__(model_class=Profile, data_path=data_path)
