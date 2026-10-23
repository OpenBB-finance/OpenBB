"""Tests for ``openbb_econometrics.panel`` - panel-data regression commands."""

import pytest

from openbb_econometrics import panel

PANEL_COMMANDS = [
    "panel_random_effects",
    "panel_between",
    "panel_pooled",
    "panel_first_difference",
    "panel_fmac",
]


@pytest.mark.parametrize("command_name", PANEL_COMMANDS)
def test_panel_regressions(panel_data, command_name):
    """Each panel estimator returns finite coefficient rows."""
    command = getattr(panel, command_name)
    out = command(
        panel.PanelRegressionQueryParams(
            data=panel_data,
            y_column="income",
            x_columns=["age", "education"],
        )
    )
    results = out.results
    assert isinstance(results, list)
    assert len(results) > 0
    for row in results:
        dumped = row.model_dump()
        assert isinstance(dumped["variable"], str)
        assert isinstance(dumped["coefficient"], float)
        assert isinstance(dumped["standard_error"], float)
        assert isinstance(dumped["t_statistic"], float)
        assert isinstance(dumped["p_value"], float)
        assert dumped["conf_int_lower"] <= dumped["conf_int_upper"]


def test_panel_first_difference_no_constant(panel_data):
    """First-difference regression drops the constant term."""
    out = panel.panel_first_difference(
        panel.PanelRegressionQueryParams(
            data=panel_data,
            y_column="income",
            x_columns=["age", "education"],
        )
    )
    variables = {row.variable for row in out.results}
    assert "const" not in variables


def test_panel_random_effects_too_few_items_raises(small_panel_data):
    """A panel with fewer than three observations triggers a ValueError."""
    params = panel.PanelRegressionQueryParams(
        data=small_panel_data,
        y_column="portfolio_value",
        x_columns=["risk_free_rate"],
    )
    with pytest.raises(ValueError, match="at least 3 items"):
        panel.panel_random_effects(params)


def test_panel_fixed(panel_data):
    """Fixed-effects regression includes entity effects and omits the constant."""
    out = panel.panel_fixed(
        panel.PanelFixedQueryParams(
            data=panel_data, y_column="income", x_columns=["age", "education"]
        )
    )
    results = out.results
    assert len(results) > 0
    assert "const" not in {row.variable for row in results}
    for row in results:
        dumped = row.model_dump()
        assert isinstance(dumped["coefficient"], float)
        assert dumped["conf_int_lower"] <= dumped["conf_int_upper"]


def test_panel_fixed_time_effects(panel_data):
    """Fixed-effects regression accepts entity and time effects together."""
    out = panel.panel_fixed(
        panel.PanelFixedQueryParams(
            data=panel_data,
            y_column="income",
            x_columns=["age", "education"],
            time_effects=True,
        )
    )
    assert out.results


def test_panel_robust_covariance(panel_data):
    """Panel estimators accept the robust covariance estimator."""
    out = panel.panel_random_effects(
        panel.PanelRegressionQueryParams(
            data=panel_data,
            y_column="income",
            x_columns=["age", "education"],
            cov_type="robust",
        )
    )
    assert out.results
