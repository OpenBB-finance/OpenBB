"""Tests for the chart view functions and the ``QuantitativeViews`` dispatcher."""

import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_quantitative import (
    attribution as att_module,
    factors as factors_module,
    risk_decomposition as rd_module,
    rolling,
)
from openbb_quantitative.quantitative_views import QuantitativeViews
from openbb_quantitative.views.attribution_bar import attribution_bar
from openbb_quantitative.views.factors_heatmap import factors_heatmap
from openbb_quantitative.views.risk_decomposition_bar import risk_decomposition_bar
from openbb_quantitative.views.rolling_factors_line import rolling_factors_line

# ---------------------------------------------------------------------------
# Helpers — run the matching endpoint once per session and reuse the rows.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def factors_results(target_returns_data, factor_matrix_data):
    out = factors_module.factors(
        factors_module.FactorRegressionQueryParams(
            data=target_returns_data,
            factors_data=factor_matrix_data,
            target="close",
            risk_free_column="rf",
        )
    )
    return out.results


@pytest.fixture(scope="module")
def rd_results(target_returns_data, factor_matrix_data):
    out = rd_module.risk_decomposition(
        rd_module.RiskDecompositionQueryParams(
            data=target_returns_data,
            factors_data=factor_matrix_data,
            target="close",
            risk_free_column="rf",
        )
    )
    return out.results


@pytest.fixture(scope="module")
def attribution_results(target_returns_data, factor_matrix_data):
    out = att_module.attribution(
        att_module.ReturnAttributionQueryParams(
            data=target_returns_data,
            factors_data=factor_matrix_data,
            target="close",
            risk_free_column="rf",
        )
    )
    return out.results


@pytest.fixture(scope="module")
def rolling_results(target_returns_data, factor_matrix_data):
    out = rolling.factors(
        rolling.RollingFactorsQueryParams(
            data=target_returns_data,
            factors_data=factor_matrix_data,
            target="close",
            window=252,
            step=63,
            risk_free_column="rf",
        )
    )
    return out.results


# ---------------------------------------------------------------------------
# factors_heatmap
# ---------------------------------------------------------------------------


def test_factors_heatmap_via_obbject(factors_results):
    fig, content = factors_heatmap(obbject_item=factors_results)
    trace = content["data"][0]
    assert trace["type"] == "heatmap"
    assert set(trace["x"]) >= {"f1", "f2", "Constant"}
    assert (
        content["layout"]["title"]["text"]
        == "Factor Regression Coefficients & P-Values"
    )


def test_factors_heatmap_via_data_list(factors_results):
    payload = [r.model_dump() for r in factors_results]
    fig, content = factors_heatmap(data=df_to_basemodel(pd.DataFrame(payload)))
    assert content["data"][0]["type"] == "heatmap"


def test_factors_heatmap_via_dataframe(factors_results):
    df = pd.DataFrame([r.model_dump() for r in factors_results])
    fig, content = factors_heatmap(
        data=df, title="Custom Title", layout_kwargs={"height": 700}
    )
    assert content["layout"]["title"]["text"] == "Custom Title"
    assert content["layout"]["height"] == 700


def test_factors_heatmap_missing_columns():
    bad = pd.DataFrame({"period": ["Max"], "factor": ["f1"]})
    with pytest.raises(ValueError, match="factors_heatmap requires"):
        factors_heatmap(data=bad)


# ---------------------------------------------------------------------------
# risk_decomposition_bar
# ---------------------------------------------------------------------------


def test_risk_decomposition_bar_via_obbject(rd_results):
    fig, content = risk_decomposition_bar(obbject_item=rd_results)
    assert content["layout"]["barmode"] == "stack"
    trace_names = [t["name"] for t in content["data"]]
    assert trace_names[-1] == "Residual"


def test_risk_decomposition_bar_via_data_list(rd_results):
    payload = df_to_basemodel(pd.DataFrame([r.model_dump() for r in rd_results]))
    fig, content = risk_decomposition_bar(data=payload, layout_kwargs={"width": 800})
    assert content["layout"]["width"] == 800


def test_risk_decomposition_bar_via_dataframe(rd_results):
    df = pd.DataFrame([r.model_dump() for r in rd_results])
    fig, content = risk_decomposition_bar(data=df, title="Risk Shares")
    assert content["layout"]["title"]["text"] == "Risk Shares"


def test_risk_decomposition_bar_missing_columns():
    bad = pd.DataFrame({"period": ["Max"], "factor": ["f1"]})
    with pytest.raises(ValueError, match="risk_decomposition_bar requires"):
        risk_decomposition_bar(data=bad)


# ---------------------------------------------------------------------------
# attribution_bar
# ---------------------------------------------------------------------------


def test_attribution_bar_via_obbject(attribution_results):
    fig, content = attribution_bar(obbject_item=attribution_results)
    trace_names = [t["name"] for t in content["data"]]
    assert "Alpha" in trace_names
    assert "Residual" in trace_names
    # Alpha and Residual are last in the legend ordering.
    assert trace_names[-2:] == ["Alpha", "Residual"]


def test_attribution_bar_via_data_list(attribution_results):
    payload = df_to_basemodel(
        pd.DataFrame([r.model_dump() for r in attribution_results])
    )
    fig, content = attribution_bar(data=payload)
    assert content["layout"]["barmode"] == "relative"


def test_attribution_bar_via_dataframe(attribution_results):
    df = pd.DataFrame([r.model_dump() for r in attribution_results])
    fig, content = attribution_bar(
        data=df, title="Return Attribution", layout_kwargs={"height": 650}
    )
    assert content["layout"]["title"]["text"] == "Return Attribution"
    assert content["layout"]["height"] == 650


def test_attribution_bar_missing_columns():
    bad = pd.DataFrame({"period": ["Max"], "factor": ["f1"]})
    with pytest.raises(ValueError, match="attribution_bar requires"):
        attribution_bar(data=bad)


# ---------------------------------------------------------------------------
# rolling_factors_line
# ---------------------------------------------------------------------------


def test_rolling_factors_line_via_obbject(rolling_results):
    """By default the intercept is dropped from the stack."""
    fig, content = rolling_factors_line(obbject_item=rolling_results)
    trace_names = [t["name"] for t in content["data"]]
    assert "Intercept" not in trace_names
    assert "f1" in trace_names
    assert "f2" in trace_names
    assert all(t.get("stackgroup") == "one" for t in content["data"])
    # No separate legend — every band labeled inline via annotations.
    assert content["layout"]["showlegend"] is False
    labels = {a["text"] for a in content["layout"]["annotations"]}
    assert any("f1" in lbl for lbl in labels)


def test_rolling_factors_line_include_intercept(rolling_results):
    """``include_intercept=True`` adds the intercept as another stacked band."""
    fig, content = rolling_factors_line(
        obbject_item=rolling_results, include_intercept=True
    )
    trace_names = [t["name"] for t in content["data"]]
    assert "Intercept" in trace_names


def test_rolling_factors_line_via_data_list(rolling_results):
    payload = df_to_basemodel(pd.DataFrame([r.model_dump() for r in rolling_results]))
    fig, content = rolling_factors_line(data=payload)
    assert all(t["type"] == "scatter" for t in content["data"])


def test_rolling_factors_line_via_dataframe(rolling_results):
    df = pd.DataFrame([r.model_dump() for r in rolling_results])
    fig, content = rolling_factors_line(
        data=df, title="Rolling Betas", layout_kwargs={"width": 900}
    )
    assert content["layout"]["title"]["text"] == "Rolling Betas"
    assert content["layout"]["width"] == 900


def test_rolling_factors_line_missing_columns():
    bad = pd.DataFrame({"date": ["2020-01-01"], "factor": ["f1"]})
    with pytest.raises(ValueError, match="rolling_factors_line requires"):
        rolling_factors_line(data=bad)


# ---------------------------------------------------------------------------
# QuantitativeViews dispatcher
# ---------------------------------------------------------------------------


def test_views_quantitative_factors(factors_results):
    fig, content = QuantitativeViews.quantitative_factors(obbject_item=factors_results)
    assert content["data"][0]["type"] == "heatmap"


def test_views_quantitative_risk_decomposition(rd_results):
    fig, content = QuantitativeViews.quantitative_risk_decomposition(
        obbject_item=rd_results
    )
    assert content["layout"]["barmode"] == "stack"


def test_views_quantitative_attribution(attribution_results):
    fig, content = QuantitativeViews.quantitative_attribution(
        obbject_item=attribution_results
    )
    assert content["layout"]["barmode"] == "relative"


def test_views_quantitative_rolling_factors(rolling_results):
    fig, content = QuantitativeViews.quantitative_rolling_factors(
        obbject_item=rolling_results
    )
    assert all(t["type"] == "scatter" for t in content["data"])
