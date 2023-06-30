from typing import Any, List, Optional, Tuple, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from openbb_sdk_core.app.repository.abstract.repository import (
    Repository as AbstractRepository,
)

T = TypeVar("T", bound=BaseModel)


class Repository(AbstractRepository[T]):
    def __init__(
        self,
        client: MongoClient,
        collection_name: str,
        database_name: str = "openbb_sdk",
    ):
        super().__init__()

        self.__client = client
        self._collection = client[database_name][collection_name]
        self._collection_name = collection_name
        self._database = client[database_name]
        self._database_name = database_name
        self._model_type = self.__retrieve_model_type()

    @property
    def client(self) -> MongoClient:
        return self.__client

    @property
    def collection(self) -> Collection:
        return self._collection

    @property
    def database(self) -> Database:
        return self._database

    @property
    def collection_name(self) -> str:
        return self._collection_name

    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def model_type(self) -> Type[T]:
        return self._model_type

    def __retrieve_model_type(self) -> Type[T]:
        if hasattr(self, "__orig_bases__"):
            model_type = self.__orig_bases__[0].__args__[0]  # type: ignore
        else:
            raise AttributeError("Cannot find the model type.")

        return model_type

    def create(self, model: T) -> str:
        collection = self._collection
        model_dict = jsonable_encoder(model, by_alias=True)
        insert_one_result = collection.insert_one(model_dict)
        inserted_id = str(insert_one_result.inserted_id)
        return inserted_id

    def read(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> Optional[T]:
        model_type = self._model_type
        collection = self._collection
        filter_list = filter_list or []
        pattern = dict(filter_list)
        if "id" in pattern:
            pattern["_id"] = pattern.pop("id")
        projection = {field: 1 for field in field_list} if field_list else {}
        document = collection.find_one(pattern, projection)

        model = model_type.parse_obj(document) if isinstance(document, dict) else None

        return model

    def update(self, model: T) -> bool:
        collection = self._collection
        if not hasattr(model, "id"):
            raise AttributeError(
                f"The following model should have an `id`, model={type(model)}"
            )
        model_id = getattr(model, "id")
        model_dict = model.dict()
        result = collection.update_one({"_id": model_id}, {"$set": model_dict})
        return result.modified_count > 0

    def delete(
        self,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> bool:
        filter_list = filter_list or []
        pattern = dict(filter_list)
        if "id" in pattern:
            pattern["_id"] = pattern.pop("id")
        result = self._collection.delete_one(pattern)
        return result.deleted_count > 0

    def read_all(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> List[T]:
        collection = self._collection
        model_type = self._model_type
        filter_list = filter_list or []
        pattern = dict(filter_list)
        if "id" in pattern:
            pattern["_id"] = pattern.pop("id")
        projection = {field: 1 for field in field_list} if field_list else {}
        model_list = []

        for document in collection.find(pattern, projection):
            model = model_type.parse_obj(document)
            model_list.append(model)

        return model_list

    def delete_all(
        self,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> bool:
        collection = self._collection
        filter_list = filter_list or []
        pattern = dict(filter_list)
        if "id" in pattern:
            pattern["_id"] = pattern.pop("id")
        raw_result = collection.delete_many(pattern).raw_result

        return raw_result["ok"] == 1.0
