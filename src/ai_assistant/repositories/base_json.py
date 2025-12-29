import os
import json
from typing import Optional, TypeVar, Type
from dataclasses import asdict
from ai_assistant.core.repository import Repository

T = TypeVar("T")

class BaseJsonRepository(Repository[T]):
    def __init__(self, model_class: Type[T], data_path: str) -> None:
        self.model_class = model_class
        self.data_path = data_path
        self.data: dict[str, T] = {}
        self._load()

    def _load(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        if not os.path.exists(self.data_path):
            self._save()
            return

        with open(self.data_path, "r") as f:
            try:
                raw_data = json.load(f)
                self.data = {k: self.model_class(**v) for k, v in raw_data.items()}
            except json.JSONDecodeError:
                self.data = {}

    def _save(self):
        with open(self.data_path, "w") as f:
            serialized = {
                k: asdict(v) for k, v in self.data.items()
            }
            json.dump(serialized, f, indent=4)

    def get(self, id: str) -> Optional[T]:
        return self.data.get(id)

    def get_all(self) -> list[T]:
        return list(self.data.values())

    def create(self, id: str, entity: T) -> T:
        self.data[id] = entity
        self._save()
        return entity

    def remove(self, id: str) -> None:
        if id in self.data:
            del self.data[id]
            self._save()
    
    def update(self, id: str, entity: T) -> None:
        if id in self.data:
            self.data[id] = entity
            self._save()
        else:
            raise KeyError(f"Entity with id {id} not found.")
