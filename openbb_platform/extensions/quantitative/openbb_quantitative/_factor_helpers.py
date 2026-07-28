"""Internal helpers shared by the factor-regression endpoints."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame, Series, Timestamp


_DEFAULT_PERIODS: tuple[str, ...] = (
    "1 Month",
    "3 Month",
    "YTD",
    "1 Year",
    "3 Year",
    "Max",
)


def period_start(max_date: "Timestamp", period: str):
    """Return the inclusive start date for a named look-back period."""
    from pandas import DateOffset, Timestamp

    if period == "1 Month":
        return max_date - DateOffset(months=1)
    if period == "3 Month":
        return max_date - DateOffset(months=3)
    if period == "YTD":
        return Timestamp(f"{max_date.year}-01-01")
    if period == "1 Year":
        return max_date - DateOffset(years=1)
    if period == "3 Year":
        return max_date - DateOffset(years=3)
    if period == "Max":
        return None
    raise ValueError(
        f"Unsupported period '{period}'. Expected one of: {list(_DEFAULT_PERIODS)}."
    )


def align_inputs(
    data,
    factors_data,
    target: str,
    index: str,
    risk_free_column: str | None,
) -> tuple["DataFrame", "Series", list[str]]:
    """Align the target series and factor matrix on their shared index.

    Returns a tuple of `(factor_matrix, target_series, factor_cols)`:
    - `factor_matrix` is indexed by the common dates, holds only the factor columns
      (risk-free column excluded), and is float-typed.
    - `target_series` is the (optionally excess) target, aligned to `factor_matrix`.
    - `factor_cols` is the ordered list of factor column names.
    Raises `ValueError` if the inputs cannot produce a non-empty aligned frame.
    """
    from openbb_core.app.utils import basemodel_to_df
    from pandas import to_datetime

    target_df = basemodel_to_df(data, index=index)
    factor_df = basemodel_to_df(factors_data, index=index)

    if target not in target_df.columns:
        raise ValueError(
            f"Target column '{target}' not found in `data`. Available columns:"
            f" {list(target_df.columns)}."
        )

    target_df.index = to_datetime(target_df.index)
    factor_df.index = to_datetime(factor_df.index)
    target_df = target_df.sort_index()
    factor_df = factor_df.sort_index().astype(float, errors="ignore")

    common_index = target_df.index.intersection(factor_df.index)
    if len(common_index) == 0:
        raise ValueError(
            "No overlapping dates between `data` and `factors_data` after alignment."
        )

    target_series = target_df.loc[common_index, target].astype(float)
    factor_matrix = factor_df.loc[common_index].copy()

    if risk_free_column is not None:
        if risk_free_column not in factor_matrix.columns:
            raise ValueError(
                f"`risk_free_column='{risk_free_column}'` not found in"
                f" `factors_data`. Available columns: {list(factor_matrix.columns)}."
            )
        target_series = target_series - factor_matrix[risk_free_column].astype(float)
        factor_matrix = factor_matrix.drop(columns=[risk_free_column])

    factor_cols = [c for c in factor_matrix.columns if c != target]
    if not factor_cols:
        raise ValueError(
            "No factor columns remain after dropping the target and risk-free columns."
        )

    aligned = factor_matrix[factor_cols].astype(float)
    aligned = aligned.assign(**{target: target_series}).dropna()
    if aligned.empty:
        raise ValueError(
            "No observations remain after dropping NaNs across the aligned"
            " target and factor matrix."
        )

    return aligned[factor_cols], aligned[target], factor_cols
