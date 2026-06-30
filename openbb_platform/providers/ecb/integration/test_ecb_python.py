"""ECB extension integration tests (Python interface)."""

import pytest
from openbb_core.app.model.obbject import OBBject

# When sibling extensions (economy / currency / fixedincome) are absent, ECB
# self-registers every command under ``obb.ecb.*`` — which is what these tests
# exercise.
_BSI_TABLE = "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    pytest.skip("Integration tests are not enabled.")


# ---------------------------------------------------------------------------
# Catalogue / utility commands (return a plain list).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_list_dataflows(params, obb):
    """Test ecb list_dataflows endpoint."""
    result = obb.ecb.list_dataflows(**params)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{"query": "interest rate"}])
@pytest.mark.integration
def test_ecb_search_dataflows(params, obb):
    """Test ecb search_dataflows endpoint."""
    result = obb.ecb.search_dataflows(**params)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_list_topics(params, obb):
    """Test ecb list_topics endpoint."""
    result = obb.ecb.list_topics(**params)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{"topic_id": "07"}])
@pytest.mark.integration
def test_ecb_topic_dataflows(params, obb):
    """Test ecb topic_dataflows endpoint (renderable dataflow rows)."""
    result = obb.ecb.topic_dataflows(**params)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(r, dict) and "value" in r for r in result)


@pytest.mark.parametrize("params", [{"dataflow": "EXR"}])
@pytest.mark.integration
def test_ecb_get_dataflow_dimensions(params, obb):
    """Test ecb get_dataflow_dimensions endpoint."""
    result = obb.ecb.get_dataflow_dimensions(**params)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{"dataflow_id": "EXR", "dimension_id": "CURRENCY"}])
@pytest.mark.integration
def test_ecb_dimension_choices(params, obb):
    """Test ecb dimension_choices endpoint."""
    result = obb.ecb.dimension_choices(**params)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_list_tables(params, obb):
    """Test ecb list_tables endpoint."""
    result = obb.ecb.list_tables(**params)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"table_id": _BSI_TABLE, "frequency": "M", "reference_area": "U2", "limit": 4}],
)
@pytest.mark.integration
def test_ecb_presentation_table(params, obb):
    """Test ecb presentation_table — indented title rows with period columns."""
    result = obb.ecb.presentation_table(**params)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all("title" in r for r in result)
    assert any(v is not None for r in result for k, v in r.items() if k != "title"), (
        "no cell values resolved"
    )


# ---------------------------------------------------------------------------
# Data commands (return an OBBject).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "params",
    [{"dataflow": "EXR", "frequency": "A", "reference_area": "USD", "limit": 5}],
)
@pytest.mark.integration
def test_ecb_available_indicators(params, obb):
    """Test ecb available_indicators endpoint."""
    result = obb.ecb.available_indicators(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"symbol": "EXR::A.USD.EUR.SP00.A"}])
@pytest.mark.integration
def test_ecb_indicators(params, obb):
    """Test ecb indicators endpoint."""
    result = obb.ecb.indicators(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"symbol": "EURUSD"}])
@pytest.mark.integration
def test_ecb_exchange_rates(params, obb):
    """Test ecb exchange_rates endpoint."""
    result = obb.ecb.exchange_rates(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_reference_rates(params, obb):
    """Test ecb reference_rates endpoint."""
    result = obb.ecb.reference_rates(**params)
    assert isinstance(result, OBBject)
    assert result.results  # a single record of all reference rates


@pytest.mark.parametrize("params", [{"interest_rate_type": "deposit"}])
@pytest.mark.integration
def test_ecb_key_interest_rates(params, obb):
    """Test ecb key_interest_rates endpoint."""
    result = obb.ecb.key_interest_rates(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params", [{"start_date": "2024-06-01", "end_date": "2024-06-30"}]
)
@pytest.mark.integration
def test_ecb_euro_short_term_rate(params, obb):
    """Test ecb euro_short_term_rate endpoint."""
    result = obb.ecb.euro_short_term_rate(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"symbol": "household_loans_for_house_purchase"}])
@pytest.mark.integration
def test_ecb_mfi_interest_rates(params, obb):
    """Test ecb mfi_interest_rates endpoint."""
    result = obb.ecb.mfi_interest_rates(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_yield_curve(params, obb):
    """Test ecb yield_curve endpoint."""
    result = obb.ecb.yield_curve(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"report_type": "main"}])
@pytest.mark.integration
def test_ecb_balance_of_payments(params, obb):
    """Test ecb balance_of_payments endpoint."""
    result = obb.ecb.balance_of_payments(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"category": "blog", "limit": 3}])
@pytest.mark.integration
def test_ecb_releases(params, obb):
    """Test ecb releases endpoint — each row carries a full markdown body."""
    result = obb.ecb.releases(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert any(r.body for r in result.results)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_calendar(params, obb):
    """Test ecb calendar endpoint (best-effort scrape)."""
    result = obb.ecb.calendar(**params)
    assert isinstance(result, OBBject)


@pytest.mark.parametrize("params", [{"currency": "EUR", "limit": 25}])
@pytest.mark.integration
def test_ecb_eligible_assets(params, obb):
    """Test ecb eligible_assets endpoint."""
    result = obb.ecb.eligible_assets(**params)
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
