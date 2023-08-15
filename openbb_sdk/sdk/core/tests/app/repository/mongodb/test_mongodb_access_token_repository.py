from unittest.mock import patch

from openbb_core.app.repository.mongodb.access_token_repository import (
    AccessTokenRepository,
)


@patch("openbb_core.app.repository.mongodb.access_token_repository.MongoClient")
def test_access_token_repository(mock_mongo_client):
    atr = AccessTokenRepository(
        client=mock_mongo_client,
        collection_name="collection_name",
        database_name="database_name",
    )

    assert isinstance(atr, AccessTokenRepository)
    assert atr.client == mock_mongo_client
    assert atr.collection_name == "collection_name"
    assert atr.database_name == "database_name"
