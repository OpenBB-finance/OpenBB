"""Test fixed income extension."""
import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name
# pylint: disable=inconsistent-return-statements


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
    ],
)
@pytest.mark.integration
def test_fixedincome_treasury(params, obb):
    result = obb.fixedincome.treasury(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"date": "2023-01-01", "inflation_adjusted": True}),
    ],
)
@pytest.mark.integration
def test_fixedincome_yield_curve(params, obb):
    result = obb.fixedincome.yield_curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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
def test_fixedincome_dwpcr(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.dwpcr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_fixedincome_ecb_interest_rates(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.ecb_interest_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_fixedincome_ice_bofa(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.ice_bofa(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "index_type": "aaa"})],
)
@pytest.mark.integration
def test_fixedincome_moody(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.moody(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "30d",
                "category": "financial",
                "grade": "aa",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_cp(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.cp(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": [10.0],
                "category": ["spot_rate"],
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_spot(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"date": "2023-01-01", "yield_curve": ["spot"]})],
)
@pytest.mark.integration
def test_fixedincome_hqm(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.hqm(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "maturity": "3m"})],
)
@pytest.mark.integration
def test_fixedincome_tmc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.tmc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "maturity": "10y"})],
)
@pytest.mark.integration
def test_fixedincome_ffrmc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.ffrmc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "maturity": "3m"})],
)
@pytest.mark.integration
def test_fixedincome_tbffr(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.tbffr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_fixedincome_eu_yield_curve(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.eu_yield_curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
