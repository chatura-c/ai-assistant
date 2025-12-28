import copy
from typing import Dict, Optional
from ai_assistant.core.assistant import AIAssistant
from .uow import AbstractUnitOfWork

class AssistantManager:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self._sessions: Dict[str, AIAssistant] = {}

    def create_assistant(self, provider_id: str, profile_id: str) -> str:
        provider_meta = self.uow.providers.get(provider_id)
        profile_meta = self.uow.profiles.get(profile_id)

        if not provider_meta or not profile_meta:
            raise ValueError(f"Could not find Provider({provider_id}) or Profile({profile_id})")

        secret = self.uow.secrets.get(provider_meta.api_key)
        if not secret:
            raise ValueError(f"Secret key '{provider_meta.api_key}' missing from OS Keyring")

        runtime_provider = copy.deepcopy(provider_meta)
        runtime_provider.api_key = secret.value

        assistant = AIAssistant(provider=runtime_provider, profile=profile_meta)
        
        session_id = f"{profile_id}_{provider_id}"
        self._sessions[session_id] = assistant
        
        return session_id

    def get_assistant(self, session_id: str) -> Optional[AIAssistant]:
        return self._sessions.get(session_id)

    def close_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
