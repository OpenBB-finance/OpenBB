from openbb_core.app.model.abstract.tagged import Tagged


def test_tagged_model():
    tagged = Tagged()

    assert hasattr(tagged, "id")


def test_fields():
    fields = Tagged.model_fields
    fields_keys = fields.keys()

    assert "id" in fields_keys
