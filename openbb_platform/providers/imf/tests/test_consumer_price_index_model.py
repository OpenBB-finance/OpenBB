"""Unit tests for the IMF Consumer Price Index model and fetcher."""

# ruff: noqa: I001

from datetime import date
from typing import Any

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_imf.models.consumer_price_index import (
    ImfConsumerPriceIndexData,
    ImfConsumerPriceIndexFetcher,
    ImfConsumerPriceIndexQueryParams,
)


class _StubQueryBuilder:
    """Stand-in for ``ImfQueryBuilder`` that captures call args."""

    instances: list = []

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self._payload: dict[str, Any] | None = None
        self._raise: Exception | None = None
        _StubQueryBuilder.instances.append(self)

    def fetch_data(self, **kwargs: Any) -> dict[str, Any]:
        """Record args and return preconfigured payload or raise."""
        self.calls.append(kwargs)
        if self._raise is not None:
            raise self._raise
        return self._payload or {"data": [], "metadata": {}}


@pytest.fixture
def patched_query_builder(monkeypatch: pytest.MonkeyPatch):
    """Replace ``ImfQueryBuilder`` with the recording stub."""
    _StubQueryBuilder.instances = []
    monkeypatch.setattr(
        "openbb_imf.models.consumer_price_index.ImfQueryBuilder",
        _StubQueryBuilder,
    )
    return _StubQueryBuilder


class TestImfConsumerPriceIndexQueryParams:
    """Tests for ``ImfConsumerPriceIndexQueryParams`` field validators."""

    def test_country_accepts_iso3_code(self):
        """ISO3 codes round-trip through the validator unchanged."""
        q = ImfConsumerPriceIndexQueryParams(country="USA")
        assert q.country == "USA"

    def test_country_accepts_country_label(self):
        """A spelled-out label is resolved to its ISO3 code (covers line 344)."""
        q = ImfConsumerPriceIndexQueryParams(country="united_states")
        assert q.country == "USA"

    def test_country_rejects_unknown(self):
        """Unknown country tokens raise ``ValueError`` (covers lines 346-348)."""
        with pytest.raises(ValueError, match="not a valid IMF country code"):
            ImfConsumerPriceIndexQueryParams(country="atlantis")

    def test_expenditure_accepts_friendly_name(self):
        """A friendly expenditure name passes validation."""
        q = ImfConsumerPriceIndexQueryParams(
            country="USA", expenditure="food_non_alcoholic_beverages"
        )
        assert q.expenditure == "food_non_alcoholic_beverages"

    def test_expenditure_accepts_api_code(self):
        """An IMF expenditure code passes validation."""
        q = ImfConsumerPriceIndexQueryParams(country="USA", expenditure="CP01")
        assert q.expenditure == "cp01"

    def test_expenditure_rejects_unknown(self):
        """Unknown expenditure raises ``ValueError`` (covers line 363)."""
        with pytest.raises(ValueError, match="not a valid choice"):
            ImfConsumerPriceIndexQueryParams(country="USA", expenditure="bogus")


class TestImfConsumerPriceIndexFetcherTransformQuery:
    """Tests for ``transform_query``."""

    def test_transform_query_builds_params(self):
        """``transform_query`` returns a model with the right defaults."""
        q = ImfConsumerPriceIndexFetcher.transform_query({"country": "USA"})
        assert isinstance(q, ImfConsumerPriceIndexQueryParams)
        assert q.country == "USA"


class TestImfConsumerPriceIndexFetcherAextractData:
    """Tests for ``aextract_data`` branches."""

    @pytest.mark.asyncio
    async def test_aextract_uses_limit_and_default_params(self, patched_query_builder):
        """``limit`` flows through as ``lastNObservations`` (covers line 456)."""
        q = ImfConsumerPriceIndexFetcher.transform_query(
            {
                "country": "USA",
                "frequency": "monthly",
                "transform": "index",
                "expenditure": "total",
                "limit": 5,
            }
        )
        out = await ImfConsumerPriceIndexFetcher.aextract_data(q, None)
        assert out == {"data": [], "metadata": {}}
        captured = patched_query_builder.instances[0].calls[0]
        assert captured["dataflow"] == "CPI"
        assert captured["lastNObservations"] == 5
        assert captured["COUNTRY"] == "USA"
        assert captured["INDEX_TYPE"] == "CPI"
        assert captured["FREQUENCY"] == "M"

    @pytest.mark.asyncio
    async def test_aextract_all_countries_and_all_expenditures(
        self, patched_query_builder
    ):
        """``all``/``*`` wildcard usage expands to ``*`` in the request."""
        q = ImfConsumerPriceIndexFetcher.transform_query(
            {
                "country": "USA,*",
                "expenditure": "all,total",
                "harmonized": True,
                "frequency": "annual",
                "transform": "index",
            }
        )
        await ImfConsumerPriceIndexFetcher.aextract_data(q, None)
        captured = patched_query_builder.instances[0].calls[0]
        assert captured["COUNTRY"] == "*"
        assert captured["COICOP_1999"] == "*"
        assert captured["INDEX_TYPE"] == "HICP"

    @pytest.mark.asyncio
    async def test_aextract_translates_value_error_via_dim_param_maps(
        self, patched_query_builder, monkeypatch
    ):
        """``ValueError`` messages are rewritten using dim/transform/freq/expenditure/country/index_type maps."""

        def boom(self, **kwargs):
            raise ValueError(
                "Bad dim 'COUNTRY' and 'FREQUENCY' "
                "and \"COUNTRY\" with code 'M' and 'IX' "
                "and exp 'CP01' index 'CPI' or 'HICP' and country 'USA'"
            )

        monkeypatch.setattr(_StubQueryBuilder, "fetch_data", boom)
        q = ImfConsumerPriceIndexFetcher.transform_query(
            {"country": "USA", "frequency": "monthly", "transform": "index"}
        )
        with pytest.raises(OpenBBError) as exc:
            await ImfConsumerPriceIndexFetcher.aextract_data(q, None)
        msg = str(exc.value)
        assert "'country'" in msg
        assert "'frequency'" in msg
        assert "'monthly'" in msg
        assert "'index'" in msg
        assert "'food_non_alcoholic_beverages'" in msg
        assert "'False'" in msg
        assert "'True'" in msg
        assert "'united_states'" in msg

    @pytest.mark.asyncio
    async def test_aextract_wraps_openbb_error(
        self, patched_query_builder, monkeypatch
    ):
        """An ``OpenBBError`` from the builder is re-raised wrapped (covers lines 485-486)."""

        def boom(self, **kwargs):
            raise OpenBBError("inner")

        monkeypatch.setattr(_StubQueryBuilder, "fetch_data", boom)
        q = ImfConsumerPriceIndexFetcher.transform_query(
            {"country": "USA", "frequency": "monthly", "transform": "index"}
        )
        with pytest.raises(OpenBBError):
            await ImfConsumerPriceIndexFetcher.aextract_data(q, None)


class TestImfConsumerPriceIndexFetcherTransformData:
    """Tests for ``transform_data``."""

    def _query(self, **overrides: Any) -> ImfConsumerPriceIndexQueryParams:
        """Build a minimal query with overrides."""
        params: dict[str, Any] = {"country": "USA"}
        params.update(overrides)
        return ImfConsumerPriceIndexFetcher.transform_query(params)

    def test_transform_data_no_rows_raises(self):
        """Empty ``data`` payload raises ``OpenBBError`` (covers line 510)."""
        q = self._query()
        with pytest.raises(OpenBBError, match="No data returned"):
            ImfConsumerPriceIndexFetcher.transform_data(q, {"data": [], "metadata": {}})

    def test_transform_data_filters_by_start_date(self):
        """A row before ``start_date`` is skipped (covers line 519)."""
        q = self._query(start_date=date(2024, 1, 1))
        rows = [
            {
                "TIME_PERIOD": "2023-01-01",
                "OBS_VALUE": 100.0,
                "COUNTRY": "United States",
                "country_code": "USA",
                "INDEX_TYPE": "CPI",
                "COICOP_1999": "_T",
                "COICOP_1999_code": "_T",
                "TYPE_OF_TRANSFORMATION": "Index",
                "FREQUENCY": "M",
                "UNIT_MULT": 1,
                "series_id": "IMF_STA_CPI_USA_T",
            },
            {
                "TIME_PERIOD": "2024-06-01",
                "OBS_VALUE": 110.0,
                "COUNTRY": "United States",
                "country_code": "USA",
                "INDEX_TYPE": "CPI",
                "COICOP_1999": "_T",
                "COICOP_1999_code": "_T",
                "TYPE_OF_TRANSFORMATION": "Year-over-year, Percent",
                "FREQUENCY": "M",
                "UNIT_MULT": 1,
                "series_id": "IMF_STA_CPI_USA_T",
            },
        ]
        result = ImfConsumerPriceIndexFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        assert len(result.result) == 1
        assert isinstance(result.result[0], ImfConsumerPriceIndexData)
        assert result.result[0].value == pytest.approx(1.1)
        assert result.result[0].unit_multiplier == 100

    def test_transform_data_filters_by_end_date(self):
        """A row after ``end_date`` is skipped (covers line 525)."""
        q = self._query(end_date=date(2024, 1, 31))
        rows = [
            {
                "TIME_PERIOD": "2024-06-01",
                "OBS_VALUE": 110.0,
                "COUNTRY": "United States",
                "country_code": "USA",
                "INDEX_TYPE": "CPI",
                "COICOP_1999": "_T",
                "COICOP_1999_code": "_T",
                "TYPE_OF_TRANSFORMATION": "Index",
                "FREQUENCY": "M",
                "UNIT_MULT": 1,
                "series_id": "IMF_STA_CPI_USA_T",
            },
            {
                "TIME_PERIOD": "2024-01-01",
                "OBS_VALUE": 100.0,
                "COUNTRY": "United States",
                "country_code": "USA",
                "INDEX_TYPE": "CPI",
                "COICOP_1999": "_T",
                "COICOP_1999_code": "_T",
                "TYPE_OF_TRANSFORMATION": "Index",
                "FREQUENCY": "M",
                "UNIT_MULT": 1,
                "series_id": "IMF_STA_CPI_USA_T",
            },
        ]
        result = ImfConsumerPriceIndexFetcher.transform_data(
            q, {"data": rows, "metadata": {}}
        )
        assert len(result.result) == 1
        assert result.result[0].date.isoformat().startswith("2024-01")

    def test_transform_data_promotes_hicp_metadata_block(self):
        """When ``IMF_STA_CPI_CPI`` is missing the HICP block is used."""
        q = self._query()
        metadata = {
            "dataset": {"foo": "bar"},
            "IMF_STA_CPI_HICP": {"indicator": "HICP", "description": "HICP desc"},
        }
        rows = [
            {
                "TIME_PERIOD": "2024-01-01",
                "OBS_VALUE": 100.0,
                "COUNTRY": "United States",
                "country_code": "USA",
                "INDEX_TYPE": "HICP",
                "COICOP_1999": "_T",
                "COICOP_1999_code": "_T",
                "TYPE_OF_TRANSFORMATION": "Index",
                "FREQUENCY": "M",
                "UNIT_MULT": 1,
                "series_id": "IMF_STA_CPI_USA_T",
            }
        ]
        result = ImfConsumerPriceIndexFetcher.transform_data(
            q, {"data": rows, "metadata": metadata}
        )
        assert result.metadata["dataset"]["index_type"] == "HICP"
        assert result.metadata["dataset"]["index_description"] == "HICP desc"
