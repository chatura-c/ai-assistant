from enum import Enum
import platform
import os
from dataclasses import dataclass

from ai_assistant.core.profile import Profile
from ai_assistant.providers.base import LLMProvider

class SystemOs(Enum):
    Linux = 'linux'
    Windows = 'win32' # I think ?


class DesktopEnv(Enum):
    Hyprland = 'hyprland'

class Compositor(Enum):
    Wayland = 'wayland'

@dataclass
class Host:
    system: SystemOs
    desktop: DesktopEnv
    compositor: Compositor

class AIAssistant:
    provider: LLMProvider
    messages = []
    
    def __init__(self) -> None:
        self.env = self._detect_host_env()
        # self.config = ConfigManager().load()
        # self.engine = AssistantEngine(self.config)
        # self.adapter = self._initialize_adapter()

    def _detect_host_env(self) -> Host:
        system = platform.system().lower()
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        compositor = os.environ.get("XDG_SESSION_TYPE", "")
        # signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")

        return Host(system, desktop, compositor)


    def set_system_prompt(self, prompt:str):
        message = {
            "role": "system",
            "content" : prompt
        } 

        if len(self.messages) > 0 and self.messages[0].role == "system":
            self.messages[0] = message
            return

        self.messages.insert(0, message)

    def ask(self, query):
        for m in query:
            self.messages.append({
                "role": "user",
                "content": m
            })
        response = self.provider.ask(self.messages) 
        self.messages.append({"role": "assistant", "content": response})

        return response
        
