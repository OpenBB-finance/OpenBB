import datetime

from openbb_core.app.model.journal_entry import JournalEntry


def test_journal_entry():
    journal = JournalEntry(
        journal_id="mock_journal_id",
        arguments={"mock_key": "mock_value"},
        duration=19,
        output={},
        route="mock_route",
        timestamp=datetime.datetime(2021, 1, 1),
        alias_list=["mock_alias"],
    )
    assert isinstance(journal, JournalEntry)


def test_fields():
    fields = JournalEntry.__fields__
    fields_keys = fields.keys()

    assert "id" in fields_keys
    assert "journal_id" in fields_keys
    assert "arguments" in fields_keys
    assert "duration" in fields_keys
    assert "output" in fields_keys
    assert "route" in fields_keys
    assert "timestamp" in fields_keys
    assert "alias_list" in fields_keys
