from abc import ABC, abstractmethod


class BaseUI(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def start(self):
        pass
