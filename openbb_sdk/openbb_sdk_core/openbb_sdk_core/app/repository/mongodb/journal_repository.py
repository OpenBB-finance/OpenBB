from pymongo.mongo_client import MongoClient

from openbb_sdk_core.app.model.journal import Journal
from openbb_sdk_core.app.repository.abstract.journal_repository import (
    JournalRepository as AbstractJournalRepository,
)
from openbb_sdk_core.app.repository.base.mongodb_repository import (
    Repository as BaseRepository,
)


class JournalRepository(BaseRepository[Journal], AbstractJournalRepository):
    def __init__(
        self,
        client: MongoClient,
        collection_name: str = "journal",
        database_name: str = "openbb_sdk",
    ):
        super().__init__(
            client=client,
            collection_name=collection_name,
            database_name=database_name,
        )
