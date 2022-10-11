# IMPORTATION STANDARD
from typing import Callable
import pytest
from pandas._typing import Axis
from pandas.testing import assert_frame_equal
import pandas as pd

# IMPORTATION INTERNAL

from openbb_terminal.helpers_denomination import (
    DENOMINATION,
    transform as transform_by_denomination,
    get_denomination,
    get_denominations,
)

df = pd.DataFrame(
    data={"Revenue": [1000000, 2000000, 3000000], "EPS": [3, 4, 5]},
    index=["ttm", "2022-01-01", "2021-01-01"],
)
dftr = df.transpose()


@pytest.mark.parametrize(
    "source, target, maxValue, axis, skipPredicate",
    [
        ("Units", None, None, 0, None),
        ("Units", None, 100, 0, None),
        ("Millions", "Thousands", None, 1, lambda s: s.name == "EPS"),
    ],
)
def test_given_arguments_then_it_transforms_as_expected(
    source: DENOMINATION,
    target: DENOMINATION,
    maxValue: float,
    axis: Axis,
    skipPredicate: Callable[[pd.Series], bool],
):
    target_df = dftr if axis == 1 else df
    expectedMax = maxValue if maxValue is not None else target_df.max().max()
    expectedTargetDenomination = (
        target if target is not None else get_denomination(expectedMax)[0]
    )

    expected_df = target_df.apply(
        lambda series: series
        if skipPredicate is not None and skipPredicate(series)
        else series
        * (
            get_denominations()[source]
            / get_denominations()[expectedTargetDenomination]
        ),
        axis,
    )

    (dft, denomination) = transform_by_denomination(
        target_df, source, target, maxValue, axis, skipPredicate
    )

    assert denomination == expectedTargetDenomination
    assert_frame_equal(dft, expected_df)
