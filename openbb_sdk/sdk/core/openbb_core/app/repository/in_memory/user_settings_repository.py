from typing import Any, Dict, List, Optional, Tuple

from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.repository.abstract.user_settings_repository import (
    UserSettingsRepository as AbstractUserSettingsRepository,
)
from openbb_core.app.repository.base.in_memory_repository import (
    Repository as BaseRepository,
)


class UserSettingsRepository(
    BaseRepository[UserSettings],
    AbstractUserSettingsRepository,
):
    def __init__(
        self,
        collection_name: str = "user_settings",
        database_name: str = "openbb_sdk",
        database_map: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            collection_name=collection_name,
            database_name=database_name,
            database_map=database_map,
        )

    def read_by_profile(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> Optional[UserSettings]:
        collection = self._collection
        filter_list = filter_list or []

        selected_model = None
        for user_settings in collection.values():
            valid_model = True
            for name, value in filter_list:
                if (
                    user_settings.profile is None
                    or not hasattr(user_settings.profile, name)
                    or getattr(user_settings.profile, name) != value
                ):
                    valid_model = False
                    break

            if valid_model:
                selected_model = user_settings
                break

        return selected_model
