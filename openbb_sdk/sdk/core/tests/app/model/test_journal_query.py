from openbb_core.app.model.journal_query import JournalQuery


def test_journal_query():
    journal_query = JournalQuery(
        journal_entry_id="mock_journal_entry_id",
        ignore_error_output=True,
    )
    assert isinstance(journal_query, JournalQuery)
    assert journal_query.journal_entry_id == "mock_journal_entry_id"
    assert journal_query.ignore_error_output is True


def test_fields():
    fields = JournalQuery.__fields__
    fields_keys = fields.keys()

    assert "journal_entry_id" in fields_keys
    assert "ignore_error_output" in fields_keys
