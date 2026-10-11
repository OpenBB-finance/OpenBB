"""Native frame results must honor public conversion options."""

import pandas as pd
from pandas.testing import assert_frame_equal

from openbb_core.app.model.obbject import OBBject


def test_frame_results_apply_index_and_sort_without_mutation():
    source = pd.DataFrame({"symbol": ["B", "A"], "price": [1, 2]})
    original = source.copy(deep=True)
    result = OBBject(results=source).to_dataframe(
        index="symbol", sort_by="price", ascending=False
    )
    assert result.index.tolist() == ["A", "B"]
    assert result["price"].tolist() == [2, 1]
    assert_frame_equal(source, original)


def test_sort_only_and_alias():
    source = pd.DataFrame({"price": [2, 1]})
    assert OBBject(results=source).to_df(index=None, sort_by="price")[
        "price"
    ].tolist() == [1, 2]


def test_no_transform_preserves_existing_identity():
    source = pd.DataFrame({"price": [2, 1]})
    assert OBBject(results=source).to_dataframe() is source
