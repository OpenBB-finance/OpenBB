import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from openbb_cftc import cftc_router as router

MODEL_COMMANDS = [
    router.cds_index_trades,
    router.cot,
    router.cot_search,
    router.cot_index,
    router.cot_movers,
    router.cot_positioning,
    router.swap_trades,
    router.swap_valuation,
    router.swap_summary,
    router.ois_curve,
    router.ois_curve_history,
    router.ois_forward_curve,
    router.ois_policy_path,
    router.fx_forward_points,
    router.fx_forward_curve,
    router.fx_implied_vol,
    router.fx_option_trades,
    router.fx_forward_trades,
    router.historical_fixings,
]


@pytest.mark.parametrize("command", MODEL_COMMANDS)
def test_model_backed_commands(command):
    sentinel = object()

    with (
        patch.object(router, "OBBject") as mock_obbject,
        patch.object(router, "OpenBBQuery") as mock_query,
    ):
        mock_obbject.from_query = AsyncMock(return_value=sentinel)
        result = asyncio.run(
            command(
                cc=None,
                provider_choices=None,
                standard_params=None,
                extra_params=None,
            )
        )

    assert result is sentinel
    assert mock_query.called
    mock_obbject.from_query.assert_awaited_once()


def test_registered_routes():
    paths = {r.path for r in router.router.api_router.routes}

    assert paths == {
        "/cds_index_trades",
        "/cot",
        "/cot_search",
        "/cot_index",
        "/cot_movers",
        "/cot_positioning",
        "/swap_trades",
        "/swap_valuation",
        "/swap_summary",
        "/ois_curve",
        "/ois_curve_history",
        "/ois_forward_curve",
        "/ois_policy_path",
        "/fx_forward_points",
        "/fx_forward_curve",
        "/fx_forward_trades",
        "/fx_implied_vol",
        "/fx_option_trades",
        "/historical_fixings",
        "/cot_choices",
        "/ppd_date_choices",
        "/apps.json",
    }


def test_cot_choices_endpoint():
    choices = [{"label": "GOLD", "value": "088691"}]

    with patch(
        "openbb_cftc.utils.helpers.get_cot_choices",
        new=AsyncMock(return_value=choices),
    ) as mock_helper:
        result = asyncio.run(router.cot_choices())

    assert result == choices
    mock_helper.assert_awaited_once()


def test_ppd_date_choices_endpoint():
    with patch(
        "openbb_cftc.utils.helpers.get_ppd_date_choices",
        new=AsyncMock(return_value=[{"label": "2026-07-15", "value": "2026-07-15"}]),
    ) as mock_helper:
        result = asyncio.run(router.ppd_date_choices(asset_class="credits"))

    assert result[0]["value"] == "2026-07-15"
    mock_helper.assert_awaited_once_with(asset_class="credits")


def test_apps_json_wraps_a_single_app(monkeypatch):
    import pathlib

    monkeypatch.setattr(
        pathlib.Path, "read_text", lambda self, *args, **kwargs: '{"name": "CFTC"}'
    )

    assert asyncio.run(router.cftc_apps()) == [{"name": "CFTC"}]


def test_apps_json_is_served():
    result = asyncio.run(router.cftc_apps())

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "CFTC"

    commands = {command.__name__ for command in MODEL_COMMANDS}
    widget_ids = {
        widget["i"]
        for app in result
        for tab in app["tabs"].values()
        for widget in tab["layout"]
    }

    for widget_id in widget_ids:
        assert widget_id.startswith("cftc_") and widget_id.endswith("_cftc_obb")
        assert widget_id[len("cftc_") : -len("_cftc_obb")] in commands

    assert widget_ids == {f"cftc_{command}_cftc_obb" for command in commands}
