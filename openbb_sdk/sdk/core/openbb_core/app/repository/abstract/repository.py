from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Tuple, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class Repository(ABC, Generic[T]):
    @property
    @abstractmethod
    def database_name(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def collection_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def create(self, model: T) -> str:
        pass

    @abstractmethod
    def read(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> Optional[T]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, model: T) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def delete(
        self,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def read_all(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> List[T]:
        raise NotImplementedError()

    @abstractmethod
    def delete_all(
        self,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> bool:
        raise NotImplementedError()
