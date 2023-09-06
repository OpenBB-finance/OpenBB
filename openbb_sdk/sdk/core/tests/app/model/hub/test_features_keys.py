from openbb_core.app.model.hub.features_keys import FeaturesKeys

# ruff: noqa: S105 S106


def test_features_keys():
    fk = FeaturesKeys(API_BITQUERY_KEY="test", API_BIZTOC_TOKEN="test2")

    assert fk.API_BITQUERY_KEY == "test"
    assert fk.API_BIZTOC_TOKEN == "test2"
