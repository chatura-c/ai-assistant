import copy
from typing import Dict, Optional
from ai_assistant.core.assistant import AIAssistant
from ai_assistant.providers.generic import GenericProvider
from .uow import AbstractUnitOfWork

class ProviderNotFoundError(Exception):
    def __init__(self, message='Provider not found.') -> None:
        super().__init__(message)


class ProfileNotFoundError(Exception):
    def __init__(self, message='Profile not found.' ) -> None:
        super().__init__(message)


class SecretNotFoundError(Exception):
    def __init__(self, message='Secret not found.') -> None:
        super().__init__(message)

class AssistantManager:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self._sessions: Dict[str, AIAssistant] = {}
    

    def create_session(self, provider_id: str, profile_id: str) -> str:
        provider_meta = self.uow.providers.get(provider_id)
        profile_meta = self.uow.profiles.get(profile_id)
        
        print(provider_meta)
        print(profile_meta)

        if not provider_meta:
            raise ProviderNotFoundError(message=f"Provider '{provider_id}' was not found.")

        if not profile_meta:
            raise ProfileNotFoundError(message=f"Profile '{profile_id}' was not found.")

        secret = self.uow.secrets.get(provider_meta.id)
        if not secret:
            raise SecretNotFoundError(message=f"API Key for {provider_id} is missing.")

        runtime_provider = GenericProvider(provider_meta.url, secret.value, provider_meta.model)

        assistant = AIAssistant(provider=runtime_provider, profile=profile_meta)
        
        session_id = f"{profile_id}_{provider_id}"
        self._sessions[session_id] = assistant
        
        return session_id

    def get_assistant(self, session_id: str) -> Optional[AIAssistant]:
        return self._sessions.get(session_id)

    def close_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
