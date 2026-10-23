"""FINRA through the REST API, against the live services."""

import pytest

from .cases import COMMANDS, case_id, path

pytestmark = pytest.mark.integration


def _get(api: dict, route: str, params: dict):
    """Call one route and return the response."""
    import requests

    written = {
        key: str(value).lower() if isinstance(value, bool) else value
        for key, value in params.items()
    }

    return requests.get(
        f"{api['base']}{route}", params=written, headers=api["headers"], timeout=180
    )


class TestCommands:
    """Every command answers with rows."""

    @pytest.mark.parametrize("case", COMMANDS, ids=case_id)
    def test_returns_rows(self, api, case):
        """The route answers with an OBBject body holding at least one row."""
        command, owner, params = case
        response = _get(
            api, "/" + "/".join(path(command, owner)), {"provider": "finra", **params}
        )
        body = response.json()

        assert response.status_code == 200, f"{command} {params}: {response.text}"
        assert body["provider"] == "finra"
        assert body["results"]


class TestRefusals:
    """Queries FINRA cannot serve are refused with a client error."""

    def test_unpublished_parameter(self, api):
        """TRACE does not publish ISINs."""
        response = _get(
            api,
            "/" + "/".join(path("fixedincome.bond_prices", "FIXEDINCOME_INSTALLED")),
            {"provider": "finra", "isin": "US037833EH90"},
        )

        assert response.status_code == 400
        assert "does not publish isin" in response.text

    def test_unfiltered_mortgages(self, api):
        """The whole mortgage-backed universe is refused."""
        response = _get(
            api,
            "/" + "/".join(path("fixedincome.bond_prices", "FIXEDINCOME_INSTALLED")),
            {"provider": "finra", "bond_type": "MBS"},
        )

        assert response.status_code == 400

    def test_unknown_bond(self, api):
        """A bond TRACE does not know answers 204."""
        response = _get(
            api,
            "/finra/fixedincome/bond_historical",
            {"provider": "finra", "cusip": "ZZZZZZZZZ"},
        )

        assert response.status_code == 204


class TestApps:
    """The dashboard template is served."""

    def test_apps(self, api):
        """The FINRA app lists its tabs."""
        response = _get(api, "/finra/apps.json", {})

        assert response.status_code == 200
        assert set(response.json()[0]["tabs"]) == {"equities", "bonds"}
