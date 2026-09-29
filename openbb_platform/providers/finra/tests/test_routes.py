"""Tests for the FINRA commands served by the REST API."""

import pytest

PREFIX = "/api/v1/finra"


@pytest.fixture(scope="module")
def api():
    """Return a client for the OpenBB REST API."""
    from fastapi.testclient import TestClient
    from openbb_core.api.rest_api import app

    return TestClient(app)


class TestRoutes:
    """Every command answers through the API with the OBBject envelope."""

    @pytest.mark.parametrize(
        "case",
        [
            ("/equity/search", {"query": "apple"}, "equity_search", 30),
            (
                "/equity/profile",
                {"symbol": "AAPL,SPY,VFIAX,BRK-B"},
                "equity_info",
                4,
            ),
            (
                "/equity/darkpool/otc",
                {"symbol": "AAPL,BRK-B"},
                "otc_aggregate_symbol",
                496,
            ),
            (
                "/equity/shorts/short_interest",
                {"symbol": "AAPL,BRK.B"},
                "short_interest",
                418,
            ),
            (
                "/fixedincome/bond_prices",
                {"cusip": "037833EH9,912810UG1,AAPL5231623"},
                "bond_prices_lookup",
                2,
            ),
            (
                "/fixedincome/bond_historical",
                {
                    "cusip": "037833EH9,91282CRK9",
                    "start_date": "2026-09-01",
                    "end_date": "2026-09-23",
                },
                "bond_historical",
                30,
            ),
        ],
    )
    def test_command(self, api, fake_session, case):
        """The command returns every row from the provider."""
        path, params, cassette, rows = case
        fake_session(cassette)
        response = api.get(f"{PREFIX}{path}", params=params)
        body = response.json()

        assert response.status_code == 200, body
        assert body["provider"] == "finra"
        assert len(body["results"]) == rows

    @pytest.mark.freeze_time("2026-09-23")
    def test_bond_list(self, api, fake_session):
        """Every bond of one product is listed."""
        fake_session("bond_list_treasury")
        response = api.get(f"{PREFIX}/fixedincome/bonds", params={"bond_type": "TS"})

        assert response.status_code == 200, response.text
        assert len(response.json()["results"]) == 150

    def test_security_list(self, api, monkeypatch):
        """Every security of one type is listed."""

        async def _list():
            return [
                {"symbol": "PDI", "security_type": "FC", "tier": "T2"},
                {"symbol": "SPY", "security_type": "FE", "tier": "T1"},
            ]

        monkeypatch.setattr("openbb_finra.utils.directory.list_securities", _list)
        response = api.get(
            f"{PREFIX}/equity/securities", params={"security_type": "closed_end_fund"}
        )

        assert response.status_code == 200, response.text
        assert [row["symbol"] for row in response.json()["results"]] == ["PDI"]

    def test_unsupported_parameter(self, api):
        """A parameter TRACE does not publish is a client error."""
        response = api.get(f"{PREFIX}/fixedincome/bond_prices", params={"isin": "X"})

        assert response.status_code == 400
        assert "does not publish isin" in response.json()["detail"]

    def test_apps(self, api):
        """The dashboard template is served."""
        response = api.get(f"{PREFIX}/apps.json")

        assert response.status_code == 200
        assert response.json()[0]["name"] == "FINRA"
