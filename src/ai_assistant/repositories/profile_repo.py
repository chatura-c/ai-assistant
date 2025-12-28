from  ai_assistant.core.profile import Profile
from ai_assistant.repositories.json_base_repo import BaseJsonRepository

class ProfileRepository(BaseJsonRepository[Profile]):
    def __init__(self) -> None:
        super().__init__(model_class=Profile, data_path="assets/profiles.json")
