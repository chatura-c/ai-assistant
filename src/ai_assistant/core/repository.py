from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, List

T = TypeVar("T")

class Repository(ABC, Generic[T]):
    @abstractmethod
    def get(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    def update(self, id: str, entity: T) -> None:
        pass

    @abstractmethod
    def remove(self, id: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[T]:  
        pass
    
    @abstractmethod
    def create(self, id:str, entity: T) -> T: 
        pass
