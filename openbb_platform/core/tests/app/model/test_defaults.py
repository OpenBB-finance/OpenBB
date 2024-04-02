from openbb_core.app.model.defaults import Defaults


def test_defaults():
    cc = Defaults(routes={"test": {"test": "test"}})
    assert isinstance(cc, Defaults)
    assert cc.routes == {"test": {"test": "test"}}


def test_fields():
    fields = Defaults.model_fields
    fields_keys = fields.keys()

    assert "routes" in fields_keys
