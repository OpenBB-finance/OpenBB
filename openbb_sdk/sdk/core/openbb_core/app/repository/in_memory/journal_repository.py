from typing import Any, Dict, Optional

from openbb_core.app.model.journal import Journal
from openbb_core.app.repository.abstract.journal_repository import (
    JournalRepository as AbstractJournalRepository,
)
from openbb_core.app.repository.base.in_memory_repository import (
    Repository as BaseRepository,
)


class JournalRepository(BaseRepository[Journal], AbstractJournalRepository):
    def __init__(
        self,
        collection_name: str = "journal",
        database_name: str = "openbb_sdk",
        database_map: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            collection_name=collection_name,
            database_name=database_name,
            database_map=database_map,
        )
