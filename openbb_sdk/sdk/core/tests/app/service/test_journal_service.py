"""Test the journal_service.py module."""
# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest
from openbb_core.app.service.journal_service import (
    AbstractJournalEntryRepository,
    InMemoryJournalEntryRepository,
    JournalService,
    MongoClient,
    MongoDBJournalEntryRepository,
)


@pytest.fixture
def journal_service():
    """Fixture for journal service."""
    return JournalService()


def test_journal_service_init(journal_service):
    """Test journal service init."""
    assert journal_service


def test_invalid_client(journal_service):
    """Test valid client."""
    assert not journal_service.valid_client()


def test_build_journal_entry_repository_with_given_repository():
    """Test build with repository."""
    mock_repository = MagicMock(spec=AbstractJournalEntryRepository)
    result = JournalService.build_journal_entry_repository(
        valid_client=True, journal_entry_repository=mock_repository
    )

    assert result == mock_repository


def test_build_journal_entry_repository_with_mongodb_client():
    """Test build with mongodb client."""
    mock_client = MagicMock(spec=MongoClient)
    result = JournalService.build_journal_entry_repository(
        valid_client=True, mongodb_client=mock_client
    )

    assert isinstance(result, MongoDBJournalEntryRepository)


def test_build_journal_entry_repository_memory():
    """Test build with in-memory access."""
    result = JournalService.build_journal_entry_repository(valid_client=True)

    assert isinstance(result, InMemoryJournalEntryRepository)


def test_build_journal_repository_with_given_repository():
    """Test build with repository."""
    mock_repository = MagicMock(spec=AbstractJournalEntryRepository)
    result = JournalService.build_journal_entry_repository(
        valid_client=True, journal_entry_repository=mock_repository
    )

    assert result == mock_repository


def test_build_journal_repository_with_mongodb_client():
    """Test build with mongodb client."""
    mock_client = MagicMock(spec=MongoClient)
    result = JournalService.build_journal_entry_repository(
        valid_client=True, mongodb_client=mock_client
    )

    assert isinstance(result, MongoDBJournalEntryRepository)


def test_build_journal_repository_memory():
    """Test build with in-memory access."""
    result = JournalService.build_journal_entry_repository(valid_client=True)

    assert isinstance(result, InMemoryJournalEntryRepository)


def test_journal_service_mongodb_client(journal_service):
    """Test mongodb client."""
    assert journal_service.mongodb_client is None


def test_journal_service_journal_entry_repository(journal_service):
    """Test journal entry repository."""
    assert isinstance(
        journal_service.journal_entry_repository, InMemoryJournalEntryRepository
    )


def test_journal_service_journal_repository(journal_service):
    """Test journal repository."""
    assert journal_service.journal_repository
    assert isinstance(
        type(journal_service.journal_repository), type(InMemoryJournalEntryRepository)
    )
