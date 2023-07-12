from pymongo.mongo_client import MongoClient

from openbb_core.api.model.access_token import AccessToken
from openbb_core.app.repository.abstract.access_token_repository import (
    AccessTokenRepository as AbstractAccessTokenRepository,
)
from openbb_core.app.repository.base.mongodb_repository import (
    Repository as BaseRepository,
)


class AccessTokenRepository(BaseRepository[AccessToken], AbstractAccessTokenRepository):
    def __init__(
        self,
        client: MongoClient,
        collection_name: str = "token",
        database_name: str = "openbb_sdk",
    ):
        super().__init__(
            client=client,
            collection_name=collection_name,
            database_name=database_name,
        )
