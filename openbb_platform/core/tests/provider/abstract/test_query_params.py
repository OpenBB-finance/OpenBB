"""Test QueryParams."""

from openbb_core.provider.abstract.query_params import QueryParams


def test_query_params_repr():
    """Test the __repr__ method of QueryParams."""
    params = QueryParams(param1="value1", param2="value2")
    assert "param1='value1'" in str(params)
    assert "param2='value2'" in str(params)


def test_query_params_no_alias():
    """Test model_dump without aliases."""
    params = QueryParams(param1="value1", param2="value2")
    dumped_params = params.model_dump()

    assert dumped_params == {"param1": "value1", "param2": "value2"}


def test_query_params_with_alias():
    """Test model_dump with aliases."""

    class AliasedQueryParams(QueryParams):
        __alias_dict__ = {"param1": "alias1"}

    params = AliasedQueryParams(param1="value1", param2="value2")
    dumped_params = params.model_dump()

    assert dumped_params == {"alias1": "value1", "param2": "value2"}
