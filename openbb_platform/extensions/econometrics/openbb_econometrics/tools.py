"""Econometrics data tools - correlation matrix and descriptive statistics."""

from typing import Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveInt

router = Router(
    prefix="", description="Econometrics correlation and descriptive tools."
)


class CorrelationMatrixQueryParams(QueryParams):
    """Query parameters for the correlation matrix endpoint."""

    __category__ = "tools"
    __output_columns__ = ("comp_to",)

    data: list[Data] = Field(description="Input dataset.")
    method: Literal["pearson", "kendall", "spearman"] = Field(
        default="pearson",
        description="Correlation method: 'pearson' (standard), 'kendall' (Kendall Tau),"
        + " or 'spearman' (rank correlation).",
    )
    min_periods: PositiveInt = Field(
        default=1,
        description="Minimum number of observations required per pair of columns"
        + " to compute a correlation.",
    )


class CorrelationMatrixData(Data):
    """One row of the correlation matrix."""

    comp_to: str = Field(
        description="The variable each correlation in the row is measured against."
    )


class SummaryStatisticsQueryParams(QueryParams):
    """Query parameters for the summary statistics endpoint."""

    __category__ = "tools"
    __output_columns__ = (
        "column",
        "count",
        "mean",
        "std",
        "min",
        "p25",
        "median",
        "p75",
        "max",
        "skew",
        "kurtosis",
    )

    data: list[Data] = Field(description="Input dataset.")


class SummaryStatisticsData(Data):
    """Descriptive statistics for a single numeric column."""

    column: str = Field(description="Name of the column.")
    count: int = Field(description="Number of non-null observations.")
    mean: float = Field(description="Arithmetic mean.")
    std: float = Field(description="Sample standard deviation.")
    min: float = Field(description="Minimum value.")
    p25: float = Field(description="25th percentile.")
    median: float = Field(description="Median (50th percentile).")
    p75: float = Field(description="75th percentile.")
    max: float = Field(description="Maximum value.")
    skew: float = Field(description="Skewness of the distribution.")
    kurtosis: float = Field(description="Excess kurtosis of the distribution.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the correlation matrix of a dataset.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.econometrics.correlation_matrix(data=stock_data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def correlation_matrix(
    params: CorrelationMatrixQueryParams,
) -> OBBject[list[CorrelationMatrixData]]:
    """Get the correlation matrix of an input dataset.

    The correlation matrix shows how strongly the variables in the dataset move in
    relation to one another. Scores range from -1 (perfect negative correlation) through
    0 (no correlation) to 1 (perfect positive correlation).
    """
    import numpy as np
    from openbb_core.app.utils import basemodel_to_df

    df = basemodel_to_df(params.data)

    if "symbol" in df.columns and len(df.symbol.unique()) > 1 and "close" in df.columns:
        df = df.pivot(columns="symbol", values="close")

    corr = df.corr(
        method=params.method, min_periods=params.min_periods, numeric_only=True
    ).replace(np.nan, None)

    results = []
    for key, series in corr.items():
        row = series.to_dict()
        row["comp_to"] = str(key)
        results.append(CorrelationMatrixData.model_validate(row))

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries")})],
)
def summary_statistics(
    params: SummaryStatisticsQueryParams,
) -> OBBject[list[SummaryStatisticsData]]:
    """Compute descriptive summary statistics for each numeric column.

    Returns per-column count, mean, standard deviation, minimum, quartiles, maximum,
    skewness, and excess kurtosis - a quick overview of each variable's distribution.
    """
    from openbb_core.app.utils import basemodel_to_df

    df = basemodel_to_df(params.data).select_dtypes(include="number")

    results = [
        SummaryStatisticsData(
            column=str(column),
            count=int(df[column].count()),
            mean=float(df[column].mean()),
            std=float(df[column].std()),
            min=float(df[column].min()),
            p25=float(df[column].quantile(0.25)),
            median=float(df[column].median()),
            p75=float(df[column].quantile(0.75)),
            max=float(df[column].max()),
            skew=float(df[column].skew()),
            kurtosis=float(df[column].kurtosis()),
        )
        for column in df.columns
    ]

    return OBBject(results=results)
