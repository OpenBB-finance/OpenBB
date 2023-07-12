from pymongo.mongo_client import MongoClient

from openbb_core.app.model.journal_entry import JournalEntry
from openbb_core.app.repository.abstract.journal_entry_repository import (
    JournalEntryRepository as AbstractJournalEntryRepository,
)
from openbb_core.app.repository.base.mongodb_repository import (
    Repository as BaseRepository,
)


class JournalEntryRepository(
    BaseRepository[JournalEntry], AbstractJournalEntryRepository
):
    def __init__(
        self,
        client: MongoClient,
        collection_name: str = "journal_entry",
        database_name: str = "openbb_sdk",
    ):
        super().__init__(
            client=client,
            collection_name=collection_name,
            database_name=database_name,
        )
