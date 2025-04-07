"""Unit Tests For Database Operations."""

import asyncio
import json

import pytest
from openbb_core.provider.utils.websockets.database import Database, DatabaseWriter
from openbb_core.provider.utils.websockets.message_queue import MessageQueue

MOCK_MESSAGES = [
    {"type": "trade", "symbol": "test1", "price": 100},
    {"type": "quote", "symbol": "test2", "price": 200},
    {"type": "trade", "symbol": "test3", "price": 300},
]


@pytest.fixture(scope="module")
def database():
    """Return a MessageQueue instance."""
    return Database(table_name="test")


@pytest.fixture
def database_writer():
    """Return a MessageQueue instance."""
    writer = DatabaseWriter(database=Database(table_name="test"), queue=MessageQueue())
    yield writer


@pytest.fixture
def message_queue():
    """Return a MessageQueue instance."""
    return MessageQueue()


def test_setup_database(database):
    """Test if the database was setup."""
    assert database
    assert database.fetch_all() == []


def test_write_to_db(database):
    """Test if the database was setup."""
    assert database
    database.write_to_db(MOCK_MESSAGES[0])
    assert database.fetch_all()[0] == MOCK_MESSAGES[0]
    database.write_to_db(MOCK_MESSAGES[1])
    assert database.fetch_all()[0] == MOCK_MESSAGES[1]
    database.write_to_db(MOCK_MESSAGES[2])
    assert database.fetch_all(limit=1)[0] == MOCK_MESSAGES[2]
    database.write_to_db(MOCK_MESSAGES[0])
    assert len(database.fetch_all()) == 4


def test_fetch_all(database):
    """Test if the database was setup."""
    assert database
    assert len(database.fetch_all()) == len(MOCK_MESSAGES) + 1


def test_clear_results(database):
    """Test if the database was setup."""
    assert database
    assert len(database.fetch_all()) == 4
    database.clear_results()
    assert database.fetch_all() == []


def test_multiple_connections(database):
    """Test interacting with the database from multiple connections."""
    assert database
    assert len(database.fetch_all()) == 0
    database.write_to_db(MOCK_MESSAGES[0])
    assert database.fetch_all()[0] == MOCK_MESSAGES[0]
    new_db = Database(
        results_file=database.results_file,
        table_name=database.table_name,
    )
    another_db = Database(
        results_file=database.results_file,
        table_name="other_test",
    )
    assert new_db.fetch_all()[0] == MOCK_MESSAGES[0]
    database.write_to_db(MOCK_MESSAGES[1])
    another_db.write_to_db(MOCK_MESSAGES[2])
    assert new_db.fetch_all(limit=1)[0] == MOCK_MESSAGES[1]
    assert another_db.fetch_all(limit=1)[0] != new_db.fetch_all(limit=1)[0]
    new_db.write_to_db(MOCK_MESSAGES[2])
    assert len(new_db.fetch_all()) == 3
    new_db.clear_results()
    assert new_db.fetch_all() == []
    assert database.fetch_all() == []
    assert another_db.fetch_all() == [MOCK_MESSAGES[2]]


def test_query_db(database):
    """Test querying the database."""
    assert database
    assert len(database.fetch_all()) == 0
    for message in MOCK_MESSAGES:
        database.write_to_db(message)
    assert len(database.fetch_all()) == 3
    query = "json_extract (message, '$.price') > 100"
    assert len(database.query(query)) == 2
    query = "json_extract (message, '$.type') == 'quote'"
    assert len(database.query(query)) == 1
    query = "SELECT message FROM test WHERE json_extract (message, '$.type') = 'trade'"
    assert len(database.query(query)) == 2
    query = "SELECT json_extract (message, '$.symbol') FROM test WHERE json_extract (message, '$.type') = 'trade'"
    assert database.query(query) == ["test1", "test3"]


def test_limit():
    """Test if the limit parameter is working and that the auto increment index doesn't reset when cleared."""
    database = Database(
        table_name="test_limit",
        limit=2,
    )
    assert database
    assert len(database.fetch_all()) == 0
    database.write_to_db(MOCK_MESSAGES[0])
    assert len(database.fetch_all()) == 1
    database.write_to_db(MOCK_MESSAGES[1])
    assert len(database.fetch_all()) == 2
    database.write_to_db(MOCK_MESSAGES[2])
    assert len(database.fetch_all()) == 2
    assert database.fetch_all()[1] == MOCK_MESSAGES[1]
    assert database.fetch_all()[0] == MOCK_MESSAGES[2]
    database.clear_results()
    assert database.fetch_all() == []
    database.write_to_db(MOCK_MESSAGES[0])
    query = "SELECT id FROM test_limit"
    assert database.query(query)[0] > 3


def test_batch_process_thread(database_writer):
    """Test if the batch process thread starts and stops."""
    database_writer.batch_processor.start()
    assert database_writer.batch_processor.is_alive()
    database_writer.batch_processor.stop()
    database_writer.batch_processor.join(timeout=1)
    assert not database_writer.batch_processor.is_alive()


@pytest.mark.asyncio
async def test_database_writer(database_writer):
    """Test if the database writer is working."""
    assert database_writer
    writer = database_writer
    assert isinstance(writer, DatabaseWriter)
    assert len(writer.database.fetch_all()) == 0
    await writer.start_writer()
    assert not writer._export_running
    assert not writer._prune_running

    for message in MOCK_MESSAGES:
        await writer.queue.enqueue(json.dumps(message))

    await asyncio.sleep(0.5)

    await writer.stop_writer()

    messages = writer.database.fetch_all()
    assert len(messages) == 3

    assert not writer.batch_processor.is_alive()
