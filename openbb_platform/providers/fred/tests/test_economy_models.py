"""Tests for the FRED economy models."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_fred.models.balance_of_payments import (
    FredBalanceOfPaymentsData,
    FredBalanceOfPaymentsFetcher,
    FredBalanceOfPaymentsQueryParams,
    _series,
)
from openbb_fred.models.commodity_spot_prices import (
    SERIES_MAP,
    FredCommoditySpotPricesFetcher,
    FredCommoditySpotPricesQueryParams,
)
from openbb_fred.models.consumer_price_index import (
    FREDConsumerPriceIndexFetcher,
    FREDConsumerPriceIndexQueryParams,
)
from openbb_fred.models.non_farm_payrolls import (
    FredNonFarmPayrollsFetcher,
    FredNonFarmPayrollsQueryParams,
)
from openbb_fred.models.personal_consumption_expenditures import (
    FredPersonalConsumptionExpendituresFetcher,
    FredPersonalConsumptionExpendituresQueryParams,
)
from openbb_fred.models.retail_prices import (
    FredRetailPricesFetcher,
    FredRetailPricesQueryParams,
)
from openbb_fred.models.series import FredSeriesData

GASOLINE_REGULAR = "APU000074714"
GASOLINE_ALL = "APU00007471A"


def _rows(records: list[dict]) -> list[FredSeriesData]:
    """Return the records as the rows a series fetch hands back."""
    return [FredSeriesData.model_validate(record) for record in records]


def _answer_series(records: list[dict], metadata: dict | None = None):
    """Return a stand-in for ``FredSeriesFetcher.fetch_data``."""

    async def answer(params, credentials, **kwargs):
        return AnnotatedResult(result=_rows(records), metadata=metadata or {})

    return answer


def _element(line: int, **overrides) -> dict:
    """Return one element of a release table."""
    element = {
        "element_id": 10000 + line,
        "parent_id": 10001,
        "line": str(line),
        "type": "series",
        "level": 1,
        "series_id": f"SERIES{line}",
        "name": f"Line {line}",
        "observation_date": "May 2024",
        "observation_value": "1,234.5",
    }
    element.update(overrides)

    return element


def _table(elements: list[dict]) -> dict:
    """Return the payload the release tables endpoint returns."""
    return {"elements": {str(n): e for n, e in enumerate(elements)}}


def _answer_table(payload: dict):
    """Return a stand-in for ``fred_get``."""

    async def answer(url, **kwargs):
        return payload

    return answer


def _answer_units(units: dict):
    """Return a stand-in for ``get_units``."""

    async def answer(release_id, credentials):
        return units

    return answer


class TestConsumerPriceIndexQuery:
    """The country and transform a consumer price index request names."""

    def test_an_unpublished_country_is_reported(self):
        with pytest.raises(ValidationError, match="Invalid country: atlantis"):
            FREDConsumerPriceIndexQueryParams(country="atlantis")

    def test_the_report_names_the_published_countries(self):
        with pytest.raises(ValidationError, match="australia"):
            FREDConsumerPriceIndexQueryParams(country="atlantis")

    def test_one_unpublished_country_among_published_ones_is_reported(self):
        with pytest.raises(ValidationError, match="Invalid country: atlantis"):
            FREDConsumerPriceIndexQueryParams(country="spain,atlantis")

    def test_a_country_is_read_case_insensitively(self):
        assert FREDConsumerPriceIndexQueryParams(country="Portugal").country == (
            "portugal"
        )

    def test_a_spaced_country_name_is_read(self):
        assert FREDConsumerPriceIndexQueryParams(country="United States").country == (
            "united_states"
        )

    def test_several_countries_are_kept_in_order(self):
        assert FREDConsumerPriceIndexQueryParams(country="portugal,spain").country == (
            "portugal,spain"
        )

    def test_an_unpublished_transform_is_reported(self):
        with pytest.raises(ValidationError, match="Invalid transform: monthly"):
            FREDConsumerPriceIndexQueryParams(transform="monthly")

    def test_the_report_names_the_published_transforms(self):
        with pytest.raises(ValidationError, match="index, yoy, period"):
            FREDConsumerPriceIndexQueryParams(transform="monthly")

    def test_a_transform_is_read_case_insensitively(self):
        assert FREDConsumerPriceIndexQueryParams(transform="YoY").transform == "yoy"

    def test_each_published_transform_is_accepted(self):
        accepted = [
            FREDConsumerPriceIndexQueryParams(transform=t).transform
            for t in ("index", "yoy", "period")
        ]

        assert accepted == ["index", "yoy", "period"]


class TestTransformQuery:
    """Turning a raw request into the query its fetcher reads."""

    def test_a_consumer_price_index_country_is_normalized(self):
        assert FREDConsumerPriceIndexFetcher.transform_query(
            {"country": "Portugal", "transform": "YoY"}
        ).country == ("portugal")

    def test_a_balance_of_payments_request_defaults_to_the_united_states(self):
        assert FredBalanceOfPaymentsFetcher.transform_query({}).country == (
            "united_states"
        )

    def test_a_commodity_spot_request_defaults_to_every_commodity(self):
        assert FredCommoditySpotPricesFetcher.transform_query({}).commodity == "all"

    def test_a_retail_prices_request_without_an_item_reads_as_fuel(self):
        assert FredRetailPricesFetcher.transform_query({"item": None}).item == "fuel"

    def test_a_personal_consumption_request_defaults_to_personal_income(self):
        assert FredPersonalConsumptionExpendituresFetcher.transform_query(
            {}
        ).category == ("personal_income")

    def test_a_non_farm_payrolls_date_is_normalized(self):
        from datetime import date

        assert FredNonFarmPayrollsFetcher.transform_query(
            {"date": [date(2024, 5, 1), date(2024, 6, 1)]}
        ).date == ("2024-05-01,2024-06-01")


class TestConsumerPriceIndexExtract:
    """Reading the series the requested countries are published as."""

    async def test_every_column_is_named_for_its_country(self, monkeypatch):
        async def answer(params, credentials, **kwargs):
            asked = params["symbol"].split(",")

            return AnnotatedResult(
                result=_rows([{"date": "2024-01-01"} | {s: 3.5 for s in asked}]),
                metadata={s: {"title": f"CPI {s}"} for s in asked},
            )

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
        )
        extracted = await FREDConsumerPriceIndexFetcher.aextract_data(
            FREDConsumerPriceIndexQueryParams(country="portugal,spain"), {}
        )

        assert set(extracted["data"][0]) == {"date", "portugal", "spain"}
        assert set(extracted["metadata"]) == {"portugal", "spain"}


class TestConsumerPriceIndexData:
    """Shaping the observations the requested countries publish."""

    def test_a_response_with_no_observations_is_reported(self):
        with pytest.raises(EmptyDataError, match="No data found for the given query"):
            FREDConsumerPriceIndexFetcher.transform_data(
                FREDConsumerPriceIndexQueryParams(country="spain"),
                {"data": [], "metadata": {}},
            )

    def test_each_row_names_one_country(self):
        result = FREDConsumerPriceIndexFetcher.transform_data(
            FREDConsumerPriceIndexQueryParams(country="portugal,spain"),
            {
                "data": [{"date": "2024-01-01", "portugal": 3.5, "spain": 2.0}],
                "metadata": {},
            },
        )

        assert [r.country for r in result.result] == ["portugal", "spain"]

    def test_a_country_with_no_value_is_dropped(self):
        result = FREDConsumerPriceIndexFetcher.transform_data(
            FREDConsumerPriceIndexQueryParams(country="portugal,spain"),
            {
                "data": [{"date": "2024-01-01", "portugal": 3.5, "spain": None}],
                "metadata": {},
            },
        )

        assert [r.country for r in result.result] == ["portugal"]

    def test_a_yearly_change_is_passed_through_unscaled(self):
        result = FREDConsumerPriceIndexFetcher.transform_data(
            FREDConsumerPriceIndexQueryParams(country="spain", transform="yoy"),
            {"data": [{"date": "2024-01-01", "spain": 3.5}], "metadata": {}},
        )

        assert result.result[0].value == 3.5

    def test_a_period_change_is_passed_through_unscaled(self):
        result = FREDConsumerPriceIndexFetcher.transform_data(
            FREDConsumerPriceIndexQueryParams(country="spain", transform="period"),
            {"data": [{"date": "2024-01-01", "spain": 0.4}], "metadata": {}},
        )

        assert result.result[0].value == 0.4

    def test_an_index_level_is_left_as_published(self):
        result = FREDConsumerPriceIndexFetcher.transform_data(
            FREDConsumerPriceIndexQueryParams(country="spain", transform="index"),
            {"data": [{"date": "2024-01-01", "spain": 118.2}], "metadata": {}},
        )

        assert result.result[0].value == 118.2

    def test_the_series_metadata_is_carried_through(self):
        result = FREDConsumerPriceIndexFetcher.transform_data(
            FREDConsumerPriceIndexQueryParams(country="spain"),
            {
                "data": [{"date": "2024-01-01", "spain": 3.5}],
                "metadata": {"spain": {"title": "CPI Spain"}},
            },
        )

        assert result.metadata == {"spain": {"title": "CPI Spain"}}


class TestBalanceOfPaymentsSeries:
    """The series a country's report is built from."""

    def test_the_series_are_named_for_the_country(self):
        assert _series(FredBalanceOfPaymentsQueryParams(country="japan"))[
            "balance_total"
        ] == ("JAPB6BLTT01CXCUSAQ")

    def test_the_united_states_is_the_default(self):
        assert _series(FredBalanceOfPaymentsQueryParams())["balance_total"] == (
            "USAB6BLTT01CXCUSAQ"
        )


class TestBalanceOfPaymentsPercent:
    """The percent columns a balance of payments report carries."""

    def test_a_percent_of_gdp_is_passed_through_unscaled(self):
        assert (
            FredBalanceOfPaymentsData.model_validate(
                {"date": "2024-03-31", "balance_percent_of_gdp": -3.2}
            ).balance_percent_of_gdp
            == -3.2
        )

    def test_a_balanced_account_is_kept(self):
        assert (
            FredBalanceOfPaymentsData.model_validate(
                {"date": "2024-03-31", "balance_percent_of_gdp": 0.0}
            ).balance_percent_of_gdp
            == 0.0
        )

    def test_a_missing_percent_reads_as_nothing(self):
        assert (
            FredBalanceOfPaymentsData.model_validate(
                {"date": "2024-03-31", "balance_percent_of_gdp": None}
            ).balance_percent_of_gdp
            is None
        )

    def test_a_dollar_column_is_left_as_published(self):
        assert (
            FredBalanceOfPaymentsData.model_validate(
                {"date": "2024-03-31", "balance_total": -221000.0}
            ).balance_total
            == -221000.0
        )


class TestBalanceOfPaymentsExtract:
    """Reading the series a country's report is built from."""

    async def test_every_series_of_the_report_is_read(self, monkeypatch):
        query = FredBalanceOfPaymentsQueryParams(country="japan")
        asked: list = []

        async def answer(series_query, credentials, **kwargs):
            asked.append(series_query.symbol)

            return []

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.aextract_data",
            staticmethod(answer),
        )
        await FredBalanceOfPaymentsFetcher.aextract_data(query, {})

        assert asked == [",".join(_series(query).values())]

    async def test_the_requested_window_reaches_the_series_query(self, monkeypatch):
        from datetime import date

        asked: list = []

        async def answer(series_query, credentials, **kwargs):
            asked.append((series_query.start_date, series_query.end_date))

            return []

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.aextract_data",
            staticmethod(answer),
        )
        await FredBalanceOfPaymentsFetcher.aextract_data(
            FredBalanceOfPaymentsQueryParams(
                start_date=date(2020, 1, 1), end_date=date(2024, 3, 31)
            ),
            {},
        )

        assert asked == [(date(2020, 1, 1), date(2024, 3, 31))]


class TestBalanceOfPaymentsData:
    """Shaping the series a balance of payments report is built from."""

    def test_a_country_with_no_observations_is_reported(self):
        with pytest.raises(EmptyDataError, match="No data was found for, japan."):
            FredBalanceOfPaymentsFetcher.transform_data(
                FredBalanceOfPaymentsQueryParams(country="japan"), []
            )

    def test_each_series_becomes_the_column_it_reports(self):
        query = FredBalanceOfPaymentsQueryParams(country="japan")
        series = _series(query)
        result = FredBalanceOfPaymentsFetcher.transform_data(
            query,
            [
                {
                    series["balance_total"]: {
                        "title": "Balance",
                        "data": {"2024-03-31": -221000.0},
                    }
                },
                {
                    series["balance_percent_of_gdp"]: {
                        "title": "Balance, percent of GDP",
                        "data": {"2024-03-31": -3.2},
                    }
                },
            ],
        )

        assert result.result[0].balance_total == -221000.0
        assert result.result[0].balance_percent_of_gdp == -3.2

    def test_the_newest_period_leads(self):
        query = FredBalanceOfPaymentsQueryParams(country="japan")
        series = _series(query)
        result = FredBalanceOfPaymentsFetcher.transform_data(
            query,
            [
                {
                    series["balance_total"]: {
                        "title": "Balance",
                        "data": {"2023-12-31": -1.0, "2024-03-31": -2.0},
                    }
                }
            ],
        )

        assert [str(r.period) for r in result.result] == [
            "2024-03-31",
            "2023-12-31",
        ]


class TestCommoditySpotPricesExtract:
    """Reading the series a commodity request resolves to."""

    async def test_the_named_commodity_resolves_to_its_series(self, monkeypatch):
        asked: dict = {}

        async def answer(params, credentials, **kwargs):
            asked.update(params)

            return AnnotatedResult(result=[], metadata={})

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
        )
        await FredCommoditySpotPricesFetcher.aextract_data(
            FredCommoditySpotPricesQueryParams(commodity="natural_gas"), {}
        )

        assert asked["symbol"] == SERIES_MAP["natural_gas"]

    async def test_every_spot_series_is_read_by_default(self, monkeypatch):
        asked: dict = {}

        async def answer(params, credentials, **kwargs):
            asked.update(params)

            return AnnotatedResult(result=[], metadata={})

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
        )
        await FredCommoditySpotPricesFetcher.aextract_data(
            FredCommoditySpotPricesQueryParams(), {}
        )

        assert asked["symbol"].split(",") == SERIES_MAP["all"].split(",")

    async def test_an_upstream_failure_is_reported(self, monkeypatch):
        async def answer(params, credentials, **kwargs):
            raise RuntimeError("the transport gave up")

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
        )

        with pytest.raises(
            OpenBBError,
            match="Failed to fetch data from FRED API: the transport gave up",
        ):
            await FredCommoditySpotPricesFetcher.aextract_data(
                FredCommoditySpotPricesQueryParams(commodity="wti"), {}
            )


class TestCommoditySpotPricesData:
    """Shaping the observations a commodity request returns."""

    def test_a_response_with_no_observations_is_reported(self):
        with pytest.raises(
            EmptyDataError, match="The request was returned with no data."
        ):
            FredCommoditySpotPricesFetcher.transform_data(
                FredCommoditySpotPricesQueryParams(commodity="wti"),
                {"result": [], "metadata": {}},
            )

    def test_each_row_is_named_and_measured_by_its_series(self):
        result = FredCommoditySpotPricesFetcher.transform_data(
            FredCommoditySpotPricesQueryParams(commodity="wti"),
            {
                "result": _rows([{"date": "2024-07-01", "DCOILWTICO": 83.38}]),
                "metadata": {
                    "DCOILWTICO": {
                        "title": "Crude Oil Prices: West Texas Intermediate",
                        "units": "Dollars per Barrel",
                    }
                },
            },
        )

        assert result.result[0].commodity == (
            "Crude Oil Prices: West Texas Intermediate"
        )
        assert result.result[0].unit == "Dollars per Barrel"
        assert result.result[0].price == 83.38

    def test_a_day_a_series_did_not_publish_is_dropped(self):
        result = FredCommoditySpotPricesFetcher.transform_data(
            FredCommoditySpotPricesQueryParams(),
            {
                "result": _rows(
                    [
                        {"date": "2024-07-01", "DCOILWTICO": 83.38, "DHHNGSP": None},
                        {"date": "2024-07-02", "DCOILWTICO": 82.81, "DHHNGSP": 2.4},
                    ]
                ),
                "metadata": {
                    "DCOILWTICO": {"title": "WTI", "units": "Dollars per Barrel"},
                    "DHHNGSP": {"title": "Henry Hub", "units": "Dollars per MMBTU"},
                },
            },
        )

        assert [(str(r.date), r.symbol) for r in result.result] == [
            ("2024-07-01", "DCOILWTICO"),
            ("2024-07-02", "DCOILWTICO"),
            ("2024-07-02", "DHHNGSP"),
        ]


class TestRetailPricesQuery:
    """The item a retail prices request names."""

    def test_no_item_reads_as_fuel(self):
        assert FredRetailPricesQueryParams(item=None).item == "fuel"

    def test_a_named_item_is_kept(self):
        assert FredRetailPricesQueryParams(item="eggs").item == "eggs"


class TestRetailPricesExtract:
    """Reading the series an item and region resolve to."""

    async def test_an_item_resolves_to_every_series_that_describes_it(
        self, monkeypatch
    ):
        asked: dict = {}

        async def answer(params, credentials, **kwargs):
            asked.update(params)

            return AnnotatedResult(
                result=_rows([{"date": "2024-01-01", GASOLINE_REGULAR: 3.5}]),
                metadata={},
            )

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
        )
        await FredRetailPricesFetcher.aextract_data(
            FredRetailPricesQueryParams(item="gasoline"), {}
        )

        assert GASOLINE_REGULAR in asked["symbol"].split(",")
        assert GASOLINE_ALL in asked["symbol"].split(",")

    async def test_the_frequency_is_sent_as_its_fred_code(self, monkeypatch):
        asked: dict = {}

        async def answer(params, credentials, **kwargs):
            asked.update(params)

            return AnnotatedResult(
                result=_rows([{"date": "2024-01-01", GASOLINE_REGULAR: 3.5}]),
                metadata={},
            )

        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
        )
        await FredRetailPricesFetcher.aextract_data(
            FredRetailPricesQueryParams(item="gasoline", frequency="annual"), {}
        )

        assert asked["frequency"] == "a"

    async def test_a_combination_with_no_observations_is_reported(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.models.series.FredSeriesFetcher.fetch_data",
            _answer_series([]),
        )

        with pytest.raises(
            EmptyDataError,
            match="No data found for the item and region combination.",
        ):
            await FredRetailPricesFetcher.aextract_data(
                FredRetailPricesQueryParams(item="gasoline"), {}
            )


class TestRetailPricesData:
    """Shaping the observations an item and region publish."""

    def test_each_row_is_described_by_the_reference_table(self):
        result = FredRetailPricesFetcher.transform_data(
            FredRetailPricesQueryParams(item="gasoline"),
            {
                "data": [{"date": "2024-01-01", GASOLINE_REGULAR: 3.5}],
                "metadata": {},
            },
        )

        assert result.result[0].symbol == GASOLINE_REGULAR
        assert result.result[0].description == (
            "Gasoline: Unleaded Regular (Cost per Gallon - 3.785 Liters)"
        )
        assert result.result[0].country == "united_states"

    def test_a_price_is_left_as_published(self):
        result = FredRetailPricesFetcher.transform_data(
            FredRetailPricesQueryParams(item="gasoline"),
            {
                "data": [{"date": "2024-01-01", GASOLINE_REGULAR: 3.5}],
                "metadata": {},
            },
        )

        assert result.result[0].value == 3.5

    @pytest.mark.parametrize("transform", ["pch", "pc1", "pca", "cch", "cca"])
    def test_a_percent_change_is_passed_through_unscaled(self, transform):
        result = FredRetailPricesFetcher.transform_data(
            FredRetailPricesQueryParams(item="gasoline", transform=transform),
            {
                "data": [{"date": "2024-01-01", GASOLINE_REGULAR: 2.5}],
                "metadata": {},
            },
        )

        assert result.result[0].value == 2.5

    @pytest.mark.parametrize("transform", ["chg", "ch1", "log"])
    def test_a_change_that_is_not_a_percent_is_left_as_published(self, transform):
        result = FredRetailPricesFetcher.transform_data(
            FredRetailPricesQueryParams(item="gasoline", transform=transform),
            {
                "data": [{"date": "2024-01-01", GASOLINE_REGULAR: 2.5}],
                "metadata": {},
            },
        )

        assert result.result[0].value == 2.5

    def test_a_month_a_series_did_not_publish_is_dropped(self):
        result = FredRetailPricesFetcher.transform_data(
            FredRetailPricesQueryParams(item="gasoline"),
            {
                "data": [
                    {
                        "date": "2024-01-01",
                        GASOLINE_REGULAR: 3.5,
                        GASOLINE_ALL: None,
                    }
                ],
                "metadata": {},
            },
        )

        assert [r.symbol for r in result.result] == [GASOLINE_REGULAR]


class TestPersonalConsumptionExpendituresUnits:
    """The unit of measure each category of the release is published in."""

    @pytest.mark.parametrize(
        ("category", "units"),
        [
            ("wages_by_industry", "Bil. of $"),
            ("pce_dollars", "Bil. of $"),
            ("real_pce_percent_change", "%"),
            ("pce_price_percent_change", "%"),
            ("real_pce_quantity_index", "Index 2017=100"),
            ("pce_price_index", "Index 2017=100"),
            ("real_pce_chained_dollars", "Bil. of Chn. 2017 $"),
        ],
    )
    async def test_a_category_measures_every_line_the_same_way(
        self, monkeypatch, category, units
    ):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1), _element(2)])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category=category), {}
        )

        assert {row["units"] for row in extracted} == {units}

    async def test_personal_income_measures_each_line_for_what_it_reports(
        self, monkeypatch
    ):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(n) for n in range(1, 41)])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="personal_income"),
            {},
        )
        measured = {row["line"]: row["units"] for row in extracted}

        assert measured[1] == "Bil. of $"
        assert measured[34] == "Bil. of $"
        assert measured[35] == "%"
        assert measured[36] == "Bil. of Chn. 2017 $"
        assert measured[37] == "Bil. of Chn. 2017 $"
        assert measured[38] == "$"
        assert measured[39] == "Chn. 2017"
        assert measured[40] == "Thous."

    @pytest.mark.parametrize(
        "omitted",
        [(), (35,), (38, 39, 40), (35, 36, 37, 38, 39, 40)],
        ids=["every-line", "one-line-omitted", "the-tail-omitted", "the-memoranda"],
    )
    async def test_measuring_personal_income_reports_only_published_lines(
        self, monkeypatch, omitted
    ):
        published = [n for n in range(1, 41) if n not in omitted]
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(n) for n in published])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="personal_income"),
            {},
        )

        assert len(extracted) == len(published)
        assert [row["line"] for row in extracted] == published
        assert [row["series_id"] for row in extracted] == [
            f"SERIES{n}" for n in published
        ]
        assert [row["name"] for row in extracted] == [f"Line {n}" for n in published]
        assert [row["observation_value"] for row in extracted] == [1234.5] * len(
            published
        )

    async def test_a_line_the_table_omits_is_not_invented(self, monkeypatch):
        published = [n for n in range(1, 41) if n not in (35, 39)]
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(n) for n in published])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="personal_income"),
            {},
        )
        measured = {row["line"]: row["units"] for row in extracted}

        assert sorted(measured) == published
        assert 35 not in measured
        assert 39 not in measured
        assert measured[38] == "$"
        assert measured[40] == "Thous."

    async def test_the_published_unit_wins_over_the_table_default(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1)])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({"SERIES1": "Percent Change from Preceding Period"}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="pce_dollars"), {}
        )

        assert extracted[0]["units"] == "Percent Change from Preceding Period"


class TestPersonalConsumptionExpendituresExtract:
    """Reading one period of the personal income and outlays release."""

    async def test_a_header_row_is_dropped(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(
                _table([_element(1), _element(2, type="header", series_id="")])
            ),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="pce_dollars"), {}
        )

        assert [row["series_id"] for row in extracted] == ["SERIES1"]

    async def test_a_suppressed_observation_is_dropped(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1), _element(2, observation_value=".")])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="pce_dollars"), {}
        )

        assert [row["series_id"] for row in extracted] == ["SERIES1"]

    async def test_a_period_with_nothing_to_report_yields_nothing(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", _answer_table({"elements": {}})
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="pce_dollars"), {}
        )

        assert extracted == []

    async def test_every_requested_period_is_read_from_its_own_table(self, monkeypatch):
        from datetime import date

        asked: list = []

        async def answer(url, **kwargs):
            asked.append(url)

            return _table([_element(1)])

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(
                category="pce_dollars", date=[date(2024, 4, 15), date(2024, 5, 1)]
            ),
            {},
        )

        assert len(asked) == 2
        assert "observation_date=2024-04-01" in "".join(asked)
        assert "observation_date=2024-05-01" in "".join(asked)
        assert len(extracted) == 2

    async def test_a_thousands_separator_is_read_as_a_number(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1, observation_value="21,345.6")])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="pce_dollars"), {}
        )

        assert extracted[0]["observation_value"] == 21345.6

    async def test_each_parent_lists_the_lines_below_it(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(
                _table(
                    [
                        _element(1, element_id=10001, parent_id=0),
                        _element(2, parent_id=10001),
                        _element(3, parent_id=10001),
                    ]
                )
            ),
        )
        monkeypatch.setattr(
            "openbb_fred.models.personal_consumption_expenditures.get_units",
            _answer_units({}),
        )
        extracted = await FredPersonalConsumptionExpendituresFetcher.aextract_data(
            FredPersonalConsumptionExpendituresQueryParams(category="pce_dollars"), {}
        )
        children = {row["element_id"]: row["children"] for row in extracted}

        assert children["10001"] == "10002,10003"
        assert children["10002"] is None


class TestPersonalConsumptionExpendituresData:
    """Ordering and validating the release once it is read."""

    def test_nothing_read_is_reported(self):
        with pytest.raises(EmptyDataError, match="The request was returned empty."):
            FredPersonalConsumptionExpendituresFetcher.transform_data(
                FredPersonalConsumptionExpendituresQueryParams(), []
            )

    def test_the_lines_of_a_period_are_reported_in_table_order(self):
        from datetime import date

        result = FredPersonalConsumptionExpendituresFetcher.transform_data(
            FredPersonalConsumptionExpendituresQueryParams(),
            [
                {
                    "observation_date": date(2024, 5, 1),
                    "line": 3,
                    "element_id": "3",
                    "parent_id": "1",
                    "level": 1,
                    "series_id": "C",
                    "name": "Third",
                    "observation_value": 3.0,
                    "units": "Bil. of $",
                },
                {
                    "observation_date": date(2024, 4, 1),
                    "line": 2,
                    "element_id": "2",
                    "parent_id": "1",
                    "level": 1,
                    "series_id": "B",
                    "name": "Second",
                    "observation_value": 2.0,
                    "units": "Bil. of $",
                },
                {
                    "observation_date": date(2024, 5, 1),
                    "line": 1,
                    "element_id": "1",
                    "parent_id": "0",
                    "level": 0,
                    "series_id": "A",
                    "name": "First",
                    "observation_value": 1.0,
                    "units": "Bil. of $",
                },
            ],
        )

        assert [r.symbol for r in result] == ["B", "A", "C"]


class TestNonFarmPayrollsExtract:
    """Reading one period of the employment situation release."""

    async def test_a_head_count_is_reported_in_people(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1, observation_value="159,432.0")])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.non_farm_payrolls.get_units", _answer_units({})
        )
        extracted = await FredNonFarmPayrollsFetcher.aextract_data(
            FredNonFarmPayrollsQueryParams(category="employees_nsa"), {}
        )

        assert extracted[0]["observation_value"] == 159432000.0

    async def test_a_share_of_employees_is_passed_through_unscaled(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1, observation_value="29.8")])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.non_farm_payrolls.get_units", _answer_units({})
        )
        extracted = await FredNonFarmPayrollsFetcher.aextract_data(
            FredNonFarmPayrollsQueryParams(category="employees_women_percent"), {}
        )

        assert extracted[0]["observation_value"] == 29.8

    async def test_a_wage_is_left_as_published(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1, observation_value="1,234.5")])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.non_farm_payrolls.get_units", _answer_units({})
        )
        extracted = await FredNonFarmPayrollsFetcher.aextract_data(
            FredNonFarmPayrollsQueryParams(category="avg_earnings_weekly"), {}
        )

        assert extracted[0]["observation_value"] == 1234.5

    async def test_the_published_unit_is_carried_through(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _answer_table(_table([_element(1)])),
        )
        monkeypatch.setattr(
            "openbb_fred.models.non_farm_payrolls.get_units",
            _answer_units({"SERIES1": "Dollars per Week"}),
        )
        extracted = await FredNonFarmPayrollsFetcher.aextract_data(
            FredNonFarmPayrollsQueryParams(category="avg_earnings_weekly"), {}
        )

        assert extracted[0]["units"] == "Dollars per Week"

    async def test_a_period_with_nothing_to_report_yields_nothing(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", _answer_table({"elements": {}})
        )
        monkeypatch.setattr(
            "openbb_fred.models.non_farm_payrolls.get_units", _answer_units({})
        )
        extracted = await FredNonFarmPayrollsFetcher.aextract_data(
            FredNonFarmPayrollsQueryParams(), {}
        )

        assert extracted == []


class TestNonFarmPayrollsData:
    """Ordering and validating the release once it is read."""

    def test_nothing_read_is_reported(self):
        with pytest.raises(EmptyDataError, match="The request was returned empty."):
            FredNonFarmPayrollsFetcher.transform_data(
                FredNonFarmPayrollsQueryParams(), []
            )

    def test_the_sectors_of_a_period_follow_the_published_order(self):
        from datetime import date

        result = FredNonFarmPayrollsFetcher.transform_data(
            FredNonFarmPayrollsQueryParams(),
            [
                {
                    "observation_date": date(2024, 6, 1),
                    "name": "Manufacturing",
                    "element_id": "3",
                    "parent_id": "1",
                    "level": 2,
                    "series_id": "C",
                    "observation_value": 3.0,
                },
                {
                    "observation_date": date(2024, 6, 1),
                    "name": "Total nonfarm",
                    "element_id": "1",
                    "parent_id": "0",
                    "level": 0,
                    "series_id": "A",
                    "observation_value": 1.0,
                },
                {
                    "observation_date": date(2024, 5, 1),
                    "name": "Total private",
                    "element_id": "2",
                    "parent_id": "1",
                    "level": 1,
                    "series_id": "B",
                    "observation_value": 2.0,
                },
            ],
        )

        assert [r.symbol for r in result] == ["B", "A", "C"]

    def test_a_sector_the_published_order_omits_comes_last(self):
        from datetime import date

        result = FredNonFarmPayrollsFetcher.transform_data(
            FredNonFarmPayrollsQueryParams(),
            [
                {
                    "observation_date": date(2024, 6, 1),
                    "name": "A sector that is not listed",
                    "element_id": "2",
                    "parent_id": "1",
                    "level": 1,
                    "series_id": "B",
                    "observation_value": 2.0,
                },
                {
                    "observation_date": date(2024, 6, 1),
                    "name": "Local government, excluding education",
                    "element_id": "1",
                    "parent_id": "0",
                    "level": 1,
                    "series_id": "A",
                    "observation_value": 1.0,
                },
            ],
        )

        assert [r.symbol for r in result] == ["A", "B"]
