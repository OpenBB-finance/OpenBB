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
    """Test the treasury rates endpoint."""
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
    """Test the US yield curve endpoint."""
    result = obb.fixedincome.government.us_yield_curve(**params)
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
                "provider": "federal_reserve",
            }
        ),
        (
            {
                "frequency": None,
                "transform": None,
                "aggregation_method": None,
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_sofr(params, obb):
    """Test the SOFR endpoint."""
    result = obb.fixedincome.sofr(**params)
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
                "provider": "federal_reserve",
            }
        ),
        (
            {
                "frequency": None,
                "transform": None,
                "aggregation_method": None,
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_sofr(params, obb):
    """Test the fixedincome rate sofr endpoint."""
    result = obb.fixedincome.rate.sofr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_estr(params, obb):
    """Test the ESTR endpoint."""
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
    """Test the SONIA endpoint."""
    result = obb.fixedincome.rate.sonia(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "maturity": "overnight",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_ameribor(params, obb):
    """Test the Ameribor endpoint."""
    result = obb.fixedincome.rate.ameribor(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "frequency": "w",
                "transform": None,
                "aggregation_method": "avg",
                "effr_only": False,
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "federal_reserve",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_effr(params, obb):
    """Test the EFFR endpoint."""
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
    """Test the EFFR forecast endpoint."""
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
    """Test the IORB endpoint."""
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
    """Test the DPCREDIT endpoint."""
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
    """Test the ECB endpoint."""
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
    """Test the ICE BofA endpoint."""
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
    """Test the Moody endpoint."""
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
                "maturity": "overnight",
                "category": "financial",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_commercial_paper(params, obb):
    """Test the commercial paper endpoint."""
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
                "category": "spot_rate",
                "provider": "fred",
            }
        ),
        (
            {
                "start_date": None,
                "end_date": None,
                "maturity": 5.5,
                "category": ["spot_rate"],
            }
        ),
        (
            {
                "start_date": None,
                "end_date": None,
                "maturity": "1,5.5,10",
                "category": "spot_rate,par_yield",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_spot_rates(params, obb):
    """Test the spot rates endpoint."""
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
    """Test the HQM endpoint."""
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
def test_fixedincome_spreads_tcm(params, obb):
    """Test the TCM endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spreads.tcm(**params)
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
def test_fixedincome_spreads_tcm_effr(params, obb):
    """Test the TCM EFFR endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spreads.tcm_effr(**params)
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
    """Test the treasury EFFR endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.spreads.treasury_effr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "rating": "aaa",
                "provider": "ecb",
                "date": "2023-01-01",
                "yield_curve_type": "spot_rate",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_eu_yield_curve(params, obb):
    """Test the EU yield curve endpoint."""
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
                "security_type": "bond",
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_auctions(params, obb):
    """Test the treasury auctions endpoint."""
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
                "date": "2023-12-28",
                "cusip": None,
                "security_type": "bill",
                "provider": "government_us",
            }
        ),
        (
            {
                "date": None,
                "provider": "tmx",
                "govt_type": "federal",
                "issue_date_min": None,
                "issue_date_max": None,
                "last_traded_min": None,
                "maturity_date_min": None,
                "maturity_date_max": None,
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_prices(params, obb):
    """Test the treasury prices endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.government.treasury_prices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "tmx",
                "issuer_name": "federal",
                "issue_date_min": None,
                "issue_date_max": None,
                "last_traded_min": None,
                "coupon_min": 3,
                "coupon_max": None,
                "currency": None,
                "issued_amount_min": None,
                "issued_amount_max": None,
                "maturity_date_min": None,
                "maturity_date_max": None,
                "isin": None,
                "lei": None,
                "country": None,
                "use_cache": False,
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_bond_prices(params, obb):
    """Test the bond prices endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.corporate.bond_prices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"date": "2023-05-01,2024-05-01", "provider": "fmp"}),
        (
            {
                "date": "2023-05-01",
                "country": "united_kingdom",
                "provider": "econdb",
                "use_cache": True,
            }
        ),
        (
            {
                "provider": "ecb",
                "yield_curve_type": "par_yield",
                "date": None,
                "rating": "aaa",
                "use_cache": True,
            }
        ),
        (
            {
                "provider": "fred",
                "yield_curve_type": "nominal",
                "date": "2023-05-01,2024-05-01",
            }
        ),
        ({"provider": "federal_reserve", "date": "2023-05-01,2024-05-01"}),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_yield_curve(params, obb):
    """Test the government yield curve endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.government.yield_curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {
            "provider": "fred",
            "category": "high_yield",
            "index": "us,europe,emerging",
            "index_type": "total_return",
            "start_date": "2023-05-31",
            "end_date": "2024-06-01",
            "transform": None,
            "frequency": None,
            "aggregation_method": "avg",
        },
    ],
)
@pytest.mark.integration
def test_fixedincome_bond_indices(params, obb):
    """Test the bond indices endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.bond_indices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {
            "provider": "fred",
            "index": "usda_30y,fha_30y",
            "start_date": "2023-05-31",
            "end_date": "2024-06-01",
            "transform": None,
            "frequency": None,
            "aggregation_method": "avg",
        },
    ],
)
@pytest.mark.integration
def test_fixedincome_mortgage_indices(params, obb):
    """Test the mortgage indices endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.fixedincome.mortgage_indices(**params)
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
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            }
        ),
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "federal_reserve",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_overnight_bank_funding(params, obb):
    """Test the Overnight Bank Funding Rate endpoint."""
    result = obb.fixedincome.rate.overnight_bank_funding(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "maturity": None,
                "start_date": None,
                "end_date": None,
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_tips_yields(params, obb):
    """Test the TIPS Yields endpoint."""
    result = obb.fixedincome.government.tips_yields(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
