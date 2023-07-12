from typing import Any, Dict, Optional

from openbb_core.app.model.journal_entry import JournalEntry
from openbb_core.app.repository.abstract.journal_entry_repository import (
    JournalEntryRepository as AbstractJournalEntryRepository,
)
from openbb_core.app.repository.base.in_memory_repository import (
    Repository as BaseRepository,
)


class JournalEntryRepository(
    BaseRepository[JournalEntry], AbstractJournalEntryRepository
):
    def __init__(
        self,
        collection_name: str = "journal_entry",
        database_name: str = "openbb_sdk",
        database_map: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            collection_name=collection_name,
            database_name=database_name,
            database_map=database_map,
        )
