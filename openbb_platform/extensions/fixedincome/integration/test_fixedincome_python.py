"""Test fixed income extension."""
import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name
# pylint: disable=inconsistent-return-statements


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_rates(params, obb):
    result = obb.fixedincome.government.treasury_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"date": "2023-01-01", "inflation_adjusted": True, "provider": "fred"}),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_us_yield_curve(params, obb):
    result = obb.fixedincome.government.us_yield_curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "period": "overnight",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_sofr(params, obb):
    result = obb.fixedincome.sofr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "volume_weighted_trimmed_mean_rate",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_estr(params, obb):
    result = obb.fixedincome.rate.estr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "rate",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_sonia(params, obb):
    result = obb.fixedincome.rate.sonia(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "overnight",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_ameribor(params, obb):
    result = obb.fixedincome.rate.ameribor(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "weekly",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_effr(params, obb):
    result = obb.fixedincome.rate.effr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({}),
        ({"long_run": True, "provider": "fred"}),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_effr_forecast(params, obb):
    result = obb.fixedincome.rate.effr_forecast(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_iorb(params, obb):
    result = obb.fixedincome.rate.iorb(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "daily_excl_weekend",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_dpcredit(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.rate.dpcredit(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interest_rate_type": "lending",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_ecb(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.rate.ecb(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06", "index_type": "yield"}),
        (
            {
                "category": "all",
                "area": "us",
                "grade": "non_sovereign",
                "options": True,
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "index_type": "yield",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_ice_bofa(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.corporate.ice_bofa(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "index_type": "aaa"})],
)
@pytest.mark.integration
def test_fixedincome_corporate_moody(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.corporate.moody(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "30d",
                "category": "financial",
                "grade": "aa",
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_commercial_paper(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.corporate.commercial_paper(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": [10.0],
                "category": ["spot_rate"],
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_spot_rates(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.corporate.spot_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"date": "2023-01-01", "yield_curve": "spot"})],
)
@pytest.mark.integration
def test_fixedincome_corporate_hqm(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.corporate.hqm(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "maturity": "3m"})],
)
@pytest.mark.integration
def test_fixedincome_spreads_tmc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spreads.tmc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "10y",
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_spreads_tmc_effr(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spreads.tmc_effr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "3m",
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_spreads_treasury_effr(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spreads.treasury_effr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"date": "2023-01-01", "yield_curve_type": "spot_rate"}),
        (
            {
                "rating": "A",
                "provider": "ecb",
                "date": "2023-01-01",
                "yield_curve_type": "spot_rate",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_eu_yield_curve(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.government.eu_yield_curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-09-01",
                "end_date": "2023-11-16",
                "cusip": None,
                "page_size": None,
                "page_num": None,
                "security_type": None,
                "provider": "government_us",
            }
        ),
        (
            {
                "start_date": "2023-09-01",
                "end_date": "2023-11-16",
                "cusip": None,
                "page_size": None,
                "page_num": None,
                "security_type": "Bond",
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_auctions(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.government.treasury_auctions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "date": "2023-11-16",
                "cusip": None,
                "security_type": "bond",
                "provider": "government_us",
            }
        ),
        (
            {
                "date": None,
                "cusip": None,
                "security_type": "bill",
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_prices(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.government.treasury_prices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
