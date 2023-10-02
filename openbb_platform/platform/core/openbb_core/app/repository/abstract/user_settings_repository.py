from abc import abstractmethod
from typing import Any, List, Optional, Tuple

from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.repository.abstract.repository import Repository


class UserSettingsRepository(Repository[UserSettings]):
    @abstractmethod
    def read_by_profile(
        self,
        field_list: Optional[List[str]] = None,
        filter_list: Optional[List[Tuple[str, Any]]] = None,
    ) -> Optional[UserSettings]:
        raise NotImplementedError()
