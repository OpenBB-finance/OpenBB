from openbb_core.app.model.journal import Journal


def test_journal_query():
    journal_query = Journal(
        name="mock_name",
        journal_entry_id_list=["id_1", "id_2"],
    )
    assert isinstance(journal_query, Journal)
    assert journal_query.name == "mock_name"
    assert journal_query.journal_entry_id_list == ["id_1", "id_2"]


def test_fields():
    fields = Journal.__fields__
    fields_keys = fields.keys()

    assert "name" in fields_keys
    assert "journal_entry_id_list" in fields_keys
