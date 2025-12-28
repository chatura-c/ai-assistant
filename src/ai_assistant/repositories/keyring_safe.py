from ai_assistant.core.models import SafeKey
from ai_assistant.core.repository import Repository
import keyring
from typing import Optional, List

class KeyringSafeRepository(Repository[SafeKey]):
    def __init__(self, service_name: str):
        self.service_name = service_name

    def create(self, entity: SafeKey) -> SafeKey:
        keyring.set_password(self.service_name, entity.key, entity.value)
        return entity

    def get(self, id: str) -> Optional[SafeKey]:
        value = keyring.get_password(self.service_name, id)
        if value is None:
            return None
        return SafeKey(key=id, value=value)

    def update(self, id: str, entity: SafeKey) -> None:
        if id != entity.key:
            self.remove(id)
        keyring.set_password(self.service_name, entity.key, entity.value)

    def remove(self, id: str) -> None:
        try:
            keyring.delete_password(self.service_name, id)
        except keyring.errors.PasswordDeleteError:
            pass

    def get_all(self) -> List[SafeKey]:
        raise NotImplementedError("Cannot list all keys.")
