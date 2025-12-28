from ai_assistant.core.models import Profile
from ai_assistant.core.models import Provider
from typing import Union


class AIAssistant:
    def __init__(self, provider: Provider, profile: Profile) -> None:
        self.provider = provider
        self.profile = profile
        self.messages: list[dict[str, str]] = []
        
        if hasattr(self.profile, 'system_prompt') and self.profile.system_prompt:
            self.set_system_prompt(self.profile.system_prompt)

    def set_system_prompt(self, prompt: str):
        message = {"role": "system", "content": prompt}
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0] = message
        else:
            self.messages.insert(0, message)

    def ask(self, query: Union[str, list[str], list[dict[str, str]]]) -> str:
        new_messages = []
        
        if isinstance(query, str):
            new_messages.append({"role": "user", "content": query})
        
        elif isinstance(query, list):
            for item in query:
                if isinstance(item, str):
                    new_messages.append({"role": "user", "content": item})
                elif isinstance(item, dict):
                    new_messages.append(item)

        self.messages.extend(new_messages)
        response = self.provider.ask(self.messages) 
        
        self.messages.append({"role": "assistant", "content": response})
        
        return response
