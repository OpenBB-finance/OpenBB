from openbb_core.app.model.defaults import Defaults


def test_defaultst():
    cc = Defaults(routes={"test": {"test": "test"}})
    assert isinstance(cc, Defaults)
    assert cc.routes == {"test": {"test": "test"}}


def test_fields():
    fields = Defaults.__fields__
    fields_keys = fields.keys()

    assert "routes" in fields_keys
