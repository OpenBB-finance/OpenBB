from typing import Any, List, Optional, Tuple

from pymongo.mongo_client import MongoClient

from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.repository.abstract.user_settings_repository import (
    UserSettingsRepository as AbstractUserSettingsRepository,
)
from openbb_core.app.repository.base.mongodb_repository import (
    Repository as BaseRepository,
)


class UserSettingsRepository(
    BaseRepository[UserSettings],
    AbstractUserSettingsRepository,
):
    def __init__(
        self,
        client: MongoClient,
        collection_name: str = "user_settings",
        database_name: str = "openbb_sdk",
    ):
        super().__init__(
            client=client,
            collection_name=collection_name,
            database_name=database_name,
        )

    def read_by_profile(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> Optional[UserSettings]:
        model_type = self._model_type
        collection = self._collection
        filter_list = filter_list or []
        pattern = dict(filter_list)
        pattern = {f"profile.{k}": v for k, v in pattern.items()}
        if "id" in pattern:
            pattern["_id"] = pattern.pop("id")
        projection = {field: 1 for field in field_list} if field_list else {}
        document = collection.find_one(pattern, projection)

        model = model_type.parse_obj(document) if isinstance(document, dict) else None

        return model
