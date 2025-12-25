from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def ask(self, system_prompt: str ,query: str) -> str:
        pass

