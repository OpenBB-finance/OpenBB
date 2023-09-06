from typing import Any, Dict, List, Optional, Tuple, TypeVar

from pydantic import BaseModel

from openbb_core.app.repository.abstract.repository import (
    Repository as AbstractRepository,
)

T = TypeVar("T", bound=BaseModel)


class Repository(AbstractRepository[T]):
    @staticmethod
    def build_database_map(
        collection_name: str,
        database_name: str,
        existing_database_map: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        database_map = existing_database_map or {}
        if database_name not in database_map:
            database_map[database_name] = {}

        if collection_name not in database_map[database_name]:
            database_map[database_name][collection_name] = {}

        return database_map

    def __init__(
        self,
        collection_name: str,
        database_name: str = "openbb_sdk",
        database_map: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()

        database_map = self.build_database_map(
            collection_name=collection_name,
            database_name=database_name,
            existing_database_map=database_map,
        )

        self._collection = database_map[database_name][collection_name]
        self._database = database_map[database_name]
        self._collection_name = collection_name
        self._database_map = database_map
        self._database_name = database_name

    @property
    def collection(self) -> Dict[str, Any]:
        return self._collection

    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def collection_name(self) -> str:
        return self._collection_name

    @property
    def database(self) -> Dict[str, Any]:
        return self._database

    @property
    def database_map(self) -> Dict[str, Any]:
        return self._database_map

    def create(self, model: T) -> str:
        collection = self._collection
        if not hasattr(model, "id"):
            raise AttributeError(
                f"The following model should have an `id`, model={type(model)}"
            )
        model_id = getattr(model, "id")
        collection[model_id] = model
        return model_id

    def read(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> Optional[T]:
        collection = self._collection
        filter_list = filter_list or []

        selected_model = None
        for model in collection.values():
            valid_model = True
            for name, value in filter_list:
                if not hasattr(model, name) or getattr(model, name) != value:
                    valid_model = False
                    break

            if valid_model:
                selected_model = model
                break

        return selected_model

    def update(self, model: T) -> bool:
        collection = self._collection
        if not hasattr(model, "id"):
            raise AttributeError(
                f"The following model should have an `id`, model={type(model)}"
            )
        model_id = getattr(model, "id")
        collection[model_id] = model
        return True

    def delete(
        self,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> bool:
        collection = self._collection
        filter_list = filter_list or []

        selected_model_key = None
        for key, model in collection.items():
            valid_model = True
            for name, value in filter_list:
                if not hasattr(model, name) or getattr(model, name) != value:
                    valid_model = False
                    break

            if valid_model:
                selected_model_key = key
                break

        if selected_model_key:
            del collection[selected_model_key]
            return True

        return False

    def read_all(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> List[T]:
        collection = self._collection
        filter_list = filter_list or []

        selected_model_list = []
        for model in collection.values():
            valid_model = True
            for name, value in filter_list:
                if not hasattr(model, name) or getattr(model, name) != value:
                    valid_model = False
                    break

            if valid_model:
                selected_model_list.append(model)

        return selected_model_list

    def delete_all(
        self,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> bool:
        collection = self._collection
        collection.clear()

        return True
