"""Test fixedincome API endpoints."""

import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "provider": "fmp"})],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_rates(params, headers):
    """Test the treasury rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/treasury_rates?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"date": "2023-01-01", "inflation_adjusted": True, "provider": "fred"})],
)
@pytest.mark.integration
def test_fixedincome_government_us_yield_curve(params, headers):
    """Test the US yield curve endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/us_yield_curve?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_sofr(params, headers):
    """Test the SOFR endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/sofr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_sofr(params, headers):
    """Test the SOFR endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/sofr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_estr(params, headers):
    """Test the ESTR rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/estr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_sonia(params, headers):
    """Test the SONIA rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/sonia?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_ameribor(params, headers):
    """Test the Ameribor rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/ameribor?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_effr(params, headers):
    """Test the EFFR rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/effr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({}), ({"long_run": True, "provider": "fred"})],
)
@pytest.mark.integration
def test_fixedincome_rate_effr_forecast(params, headers):
    """Test the EFFR forecast rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/effr_forecast?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06"})],
)
@pytest.mark.integration
def test_fixedincome_rate_iorb(params, headers):
    """Test the IORB rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/iorb?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_dpcredit(params, headers):
    """Test the DPCredit rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/dpcredit?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_ecb(params, headers):
    """Test the ECB rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/ecb?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_corporate_ice_bofa(params, headers):
    """Test the ICE BofA corporate yield index endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/ice_bofa?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "index_type": "aaa"})],
)
@pytest.mark.integration
def test_fixedincome_corporate_moody(params, headers):
    """Test the Moody's corporate yield index endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/moody?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_corporate_commercial_paper(params, headers):
    """Test the commercial paper endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/commercial_paper?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_corporate_spot_rates(params, headers):
    """Test the corporate spot rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/spot_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"date": "2023-01-01", "yield_curve": "spot"})],
)
@pytest.mark.integration
def test_fixedincome_corporate_hqm(params, headers):
    """Test the HQM corporate yield curve endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/hqm?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "maturity": "3m"})],
)
@pytest.mark.integration
def test_fixedincome_spreads_tcm(params, headers):
    """Test the TCM spreads endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/spreads/tcm?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_spreads_tcm_effr(params, headers):
    """Test the TCM EFFR spreads endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/spreads/tcm_effr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_spreads_treasury_effr(params, headers):
    """Test the treasury EFFR spreads endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/spreads/treasury_effr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_government_eu_yield_curve(params, headers):
    """Test the EU yield curve endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/eu_yield_curve?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_government_treasury_auctions(params, headers):
    """Test the treasury auctions endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/government/treasury_auctions?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_government_treasury_prices(params, headers):
    """Test the treasury prices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/treasury_prices?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_corporate_bond_prices(params, headers):
    """Test the corporate bond prices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/bond_prices?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_government_yield_curve(params, headers):
    """Test the treasury rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/government/yield_curve?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_bond_indices(params, headers):
    """Test the bond indices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/bond_indices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_mortgage_indices(params, headers):
    """Test the mortgage indices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/mortgage_indices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_rate_overnight_bank_funding(params, headers):
    """Test the Overnight Bank Funding Rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/overnight_bank_funding?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_fixedincome_government_tips_yields(params, headers):
    """Test the TIPS Yields endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/government/tips_yields?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
