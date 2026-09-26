"""Tests for the FRED survey models."""

from datetime import date
from typing import get_args

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_fred.models.manufacturing_outlook_ny import (
    NY_MANUFACTURING_OUTLOOK,
    NY_MANUFACTURING_OUTLOOK_CHOICES,
    FredManufacturingOutlookNYFetcher,
    FredManufacturingOutlookNYQueryParams,
)
from openbb_fred.models.manufacturing_outlook_texas import (
    TEXAS_MANUFACTURING_OUTLOOK,
    TEXAS_MANUFACTURING_OUTLOOK_CHOICES,
    FredManufacturingOutlookTexasFetcher,
    FredManufacturingOutlookTexasQueryParams,
)
from openbb_fred.models.senior_loan_officer_survey import (
    SLOOS_CATEGORIES,
    FredSeniorLoanOfficerSurveyFetcher,
    FredSeniorLoanOfficerSurveyQueryParams,
)
from openbb_fred.models.series import FredSeriesData, FredSeriesFetcher
from openbb_fred.models.survey_of_economic_conditions_chicago import (
    ID_TO_FIELD as CHICAGO_ID_TO_FIELD,
    FredSurveyOfEconomicConditionsChicagoData,
    FredSurveyOfEconomicConditionsChicagoFetcher,
    FredSurveyOfEconomicConditionsChicagoQueryParams,
)
from openbb_fred.models.university_of_michigan import (
    FredUofMichiganFetcher,
    FredUofMichiganQueryParams,
)

NY_NEW_ORDERS = [
    {
        "date": "2024-05-01",
        "NOFDINA066MNFRBNY": 20.0,
        "NOFINA156MNFRBNY": 45.0,
        "NOFDNA156MNFRBNY": 25.0,
        "NOFNNA156MNFRBNY": 30.0,
        "NOCDINA066MNFRBNY": 12.5,
        "NOCINA156MNFRBNY": 40.0,
        "NOCDNA156MNFRBNY": 27.5,
        "NOCNNA156MNFRBNY": 32.5,
    }
]

TEXAS_NEW_ORDERS_GROWTH = [
    {
        "date": "2024-05-01",
        "FGROSAMFRBDAL": 20.0,
        "FGROISAMFRBDAL": 45.0,
        "FGRODSAMFRBDAL": 25.0,
        "FGRONSAMFRBDAL": 30.0,
        "GROSAMFRBDAL": 12.5,
        "GROISAMFRBDAL": 40.0,
        "GRODSAMFRBDAL": 27.5,
        "GRONSAMFRBDAL": 32.5,
    }
]

CHICAGO_ACTIVITY = [
    {
        "date": "2024-05-01",
        "CFSBCACTIVITY": 1.5,
        "CFSBCOUTLOOK": -2.0,
        "CFSBCACTIVITYMFG": 3.0,
        "CFSBCACTIVITYNMFG": 4.0,
        "CFSBCCAPXEXP": 5.0,
        "CFSBCHIRINGEXP": 6.0,
        "CFSBCHIRING": 7.0,
        "CFSBCLABORCOSTS": 8.0,
        "CFSBCNONLABORCOSTS": 9.0,
    }
]

MICHIGAN_SENTIMENT = [
    {"date": "1977-01-01", "UMCSENT": None, "MICH": 6.5, "UMCSENT1": 90.6},
    {"date": "2024-05-01", "UMCSENT": 69.1, "MICH": 3.3, "UMCSENT1": None},
]

SLOOS_AUTO_METADATA = {
    "DEMAUTO": {"title": "Demand for Auto Loans"},
    "STDSAUTO": {"title": "Lending Standards for Auto Loans"},
}


def _answers(monkeypatch, rows, metadata=None, seen=None):
    """Answer every series fetch with the given rows.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        The patcher the test was handed.
    rows : list
        The observation records the series fetch returns.
    metadata : dict or None
        The metadata the series fetch returns alongside the rows.
    seen : list or None
        A list the parameters of each call are appended to.
    """

    async def answer(params, credentials=None, **kwargs):
        if seen is not None:
            seen.append(params)
        return AnnotatedResult(
            result=[FredSeriesData.model_validate(r) for r in rows],
            metadata=metadata or {},
        )

    monkeypatch.setattr(FredSeriesFetcher, "fetch_data", answer)


def _fails(monkeypatch, error):
    """Fail every series fetch with the given error.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        The patcher the test was handed.
    error : BaseException
        The error the series fetch raises.
    """

    async def answer(params, credentials=None, **kwargs):
        raise error

    monkeypatch.setattr(FredSeriesFetcher, "fetch_data", answer)


class TestNyTopicValidation:
    """The topic a New York manufacturing outlook request is narrowed to."""

    def test_no_topic_falls_back_to_new_orders(self):
        assert FredManufacturingOutlookNYQueryParams(topic=None).topic == "new_orders"

    def test_a_single_topic_is_kept(self):
        assert FredManufacturingOutlookNYQueryParams(topic="capex").topic == "capex"

    def test_a_comma_separated_string_is_kept(self):
        query = FredManufacturingOutlookNYQueryParams(topic="capex,shipments")

        assert query.topic == "capex,shipments"

    def test_a_list_is_joined_into_one_string(self):
        query = FredManufacturingOutlookNYQueryParams(topic=["capex", "shipments"])

        assert query.topic == "capex,shipments"

    def test_an_unknown_topic_is_reported_and_dropped(self):
        with pytest.warns(UserWarning, match="Invalid topic: nonsense"):
            query = FredManufacturingOutlookNYQueryParams(topic="capex,nonsense")

        assert query.topic == "capex"

    def test_only_unknown_topics_fall_back_to_new_orders(self):
        with pytest.warns(UserWarning, match="Invalid topic: nonsense"):
            query = FredManufacturingOutlookNYQueryParams(topic="nonsense")

        assert query.topic == "new_orders"

    def test_a_topic_that_is_neither_a_string_nor_a_list_falls_back(self):
        assert FredManufacturingOutlookNYQueryParams(topic=7).topic == "new_orders"


class TestNySeriesMap:
    """The series the New York survey publishes under each seasonality."""

    def test_every_seasonally_adjusted_series_is_an_adjusted_series(self):
        """The 'sa' half must never name a series FRED publishes unadjusted."""
        adjusted = [
            series
            for topic in NY_MANUFACTURING_OUTLOOK.values()
            for series in topic["sa"].values()
        ]

        assert [s for s in adjusted if not s.endswith("MSFRBNY")] == []

    def test_no_series_is_published_under_both_seasonalities(self):
        adjusted = {
            series
            for topic in NY_MANUFACTURING_OUTLOOK.values()
            for series in topic["sa"].values()
        }
        unadjusted = {
            series
            for topic in NY_MANUFACTURING_OUTLOOK.values()
            for series in topic["not_sa"].values()
        }

        assert adjusted & unadjusted == set()

    def test_every_offered_topic_names_at_least_one_half(self):
        """A topic that names neither half is refused before the request is made."""
        missing = [
            choice
            for choice in NY_MANUFACTURING_OUTLOOK_CHOICES
            if f"current_{choice}" not in NY_MANUFACTURING_OUTLOOK
            and f"future_{choice}" not in NY_MANUFACTURING_OUTLOOK
        ]

        assert missing == []


class TestNyExtract:
    """Reading the series a New York manufacturing outlook request resolves to."""

    async def test_both_halves_of_a_topic_are_requested(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, NY_NEW_ORDERS, seen=seen)
        await FredManufacturingOutlookNYFetcher.fetch_data({"topic": "new_orders"}, {})

        assert seen[0]["symbol"].split(",") == [
            "NOFDINA066MNFRBNY",
            "NOFINA156MNFRBNY",
            "NOFDNA156MNFRBNY",
            "NOFNNA156MNFRBNY",
            "NOCDINA066MNFRBNY",
            "NOCINA156MNFRBNY",
            "NOCDNA156MNFRBNY",
            "NOCNNA156MNFRBNY",
        ]

    async def test_asking_for_adjusted_data_requests_the_adjusted_series(
        self, monkeypatch
    ):
        seen: list = []
        _answers(monkeypatch, NY_NEW_ORDERS, seen=seen)
        await FredManufacturingOutlookNYFetcher.aextract_data(
            FredManufacturingOutlookNYQueryParams(
                topic="new_orders", seasonally_adjusted=True
            ),
            {},
        )

        assert seen[0]["symbol"].split(",") == [
            "NOFDISA066MSFRBNY",
            "NOFISA156MSFRBNY",
            "NOFDSA156MSFRBNY",
            "NOFNSA156MSFRBNY",
            "NOCDISA066MSFRBNY",
            "NOCISA156MSFRBNY",
            "NOCDSA156MSFRBNY",
            "NOCNSA156MSFRBNY",
        ]

    async def test_a_topic_with_no_current_half_requests_only_the_future_series(
        self, monkeypatch
    ):
        seen: list = []
        _answers(monkeypatch, NY_NEW_ORDERS, seen=seen)
        await FredManufacturingOutlookNYFetcher.aextract_data(
            FredManufacturingOutlookNYQueryParams(topic="capex"), {}
        )

        assert seen[0]["symbol"].split(",") == [
            "CEFDINA066MNFRBNY",
            "CEFINA156MNFRBNY",
            "CEFDNA156MNFRBNY",
            "CEFNNA156MNFRBNY",
        ]

    async def test_a_lower_frequency_is_sent_as_its_first_letter(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, NY_NEW_ORDERS, seen=seen)
        await FredManufacturingOutlookNYFetcher.aextract_data(
            FredManufacturingOutlookNYQueryParams(
                topic="new_orders", frequency="quarter"
            ),
            {},
        )

        assert seen[0]["frequency"] == "q"

    async def test_a_topic_that_names_no_series_is_reported(self):
        query = FredManufacturingOutlookNYQueryParams.model_construct(topic="mystery")

        with pytest.raises(OpenBBError, match="No valid topic selected"):
            await FredManufacturingOutlookNYFetcher.aextract_data(query, {})

    async def test_a_failed_request_is_reported_with_its_message(self, monkeypatch):
        _fails(monkeypatch, RuntimeError("the transport gave up"))

        with pytest.raises(OpenBBError, match="the transport gave up"):
            await FredManufacturingOutlookNYFetcher.aextract_data(
                FredManufacturingOutlookNYQueryParams(topic="new_orders"), {}
            )

    async def test_a_failed_request_with_no_message_is_named_by_its_type(
        self, monkeypatch
    ):
        _fails(monkeypatch, TimeoutError())

        with pytest.raises(OpenBBError, match=r"FRED request failed \(TimeoutError\)"):
            await FredManufacturingOutlookNYFetcher.aextract_data(
                FredManufacturingOutlookNYQueryParams(topic="new_orders"), {}
            )


class TestNyTransform:
    """Shaping the New York survey response into one row per topic and date."""

    def _query(self, **kwargs):
        """Return a New York query with the given overrides."""
        return FredManufacturingOutlookNYQueryParams(topic="new_orders", **kwargs)

    def test_an_empty_response_is_reported(self):
        with pytest.raises(EmptyDataError, match="rate limiting"):
            FredManufacturingOutlookNYFetcher.transform_data(
                self._query(), {"metadata": {}, "data": []}
            )

    def test_the_current_and_future_halves_become_their_own_rows(self):
        result = FredManufacturingOutlookNYFetcher.transform_data(
            self._query(), {"metadata": {}, "data": NY_NEW_ORDERS}
        )

        assert [r.topic for r in result.result] == [
            "current_new_orders",
            "future_new_orders",
        ]

    def test_the_published_percent_columns_are_passed_through_unscaled(self):
        result = FredManufacturingOutlookNYFetcher.transform_data(
            self._query(), {"metadata": {}, "data": NY_NEW_ORDERS}
        )
        current = result.result[0]

        assert (
            current.percent_reporting_increase,
            current.percent_reporting_decrease,
            current.percent_reporting_no_change,
        ) == (40.0, 27.5, 32.5)

    def test_the_diffusion_index_is_left_as_published(self):
        result = FredManufacturingOutlookNYFetcher.transform_data(
            self._query(), {"metadata": {}, "data": NY_NEW_ORDERS}
        )

        assert result.result[0].diffusion_index == 12.5

    def test_a_percent_change_transform_does_not_rescale_the_diffusion_index(self):
        result = FredManufacturingOutlookNYFetcher.transform_data(
            self._query(transform="pch"), {"metadata": {}, "data": NY_NEW_ORDERS}
        )

        assert [r.diffusion_index for r in result.result] == [12.5, 20.0]

    def test_a_level_change_transform_leaves_the_diffusion_index_alone(self):
        result = FredManufacturingOutlookNYFetcher.transform_data(
            self._query(transform="chg"), {"metadata": {}, "data": NY_NEW_ORDERS}
        )

        assert [r.diffusion_index for r in result.result] == [12.5, 20.0]

    def test_the_series_metadata_is_carried_through(self):
        metadata = {"NOCDINA066MNFRBNY": {"title": "Current New Orders"}}
        result = FredManufacturingOutlookNYFetcher.transform_data(
            self._query(), {"metadata": metadata, "data": NY_NEW_ORDERS}
        )

        assert result.metadata == metadata


class TestTexasTopicValidation:
    """The topic a Texas manufacturing outlook request is narrowed to."""

    def test_no_topic_falls_back_to_new_orders_growth(self):
        query = FredManufacturingOutlookTexasQueryParams(topic=None)

        assert query.topic == "new_orders_growth"

    def test_a_single_topic_is_kept(self):
        assert FredManufacturingOutlookTexasQueryParams(topic="wages").topic == "wages"

    def test_a_comma_separated_string_is_kept(self):
        query = FredManufacturingOutlookTexasQueryParams(topic="wages,shipments")

        assert query.topic == "wages,shipments"

    def test_a_list_is_joined_into_one_string(self):
        query = FredManufacturingOutlookTexasQueryParams(topic=["wages", "shipments"])

        assert query.topic == "wages,shipments"

    def test_an_unknown_topic_is_reported_and_dropped(self):
        with pytest.warns(UserWarning, match="Invalid topic: nonsense"):
            query = FredManufacturingOutlookTexasQueryParams(topic="wages,nonsense")

        assert query.topic == "wages"

    def test_only_unknown_topics_fall_back_to_new_orders_growth(self):
        with pytest.warns(UserWarning, match="Invalid topic: nonsense"):
            query = FredManufacturingOutlookTexasQueryParams(topic="nonsense")

        assert query.topic == "new_orders_growth"

    def test_a_topic_that_is_neither_a_string_nor_a_list_falls_back(self):
        query = FredManufacturingOutlookTexasQueryParams(topic=7)

        assert query.topic == "new_orders_growth"

    def test_every_offered_topic_names_a_current_and_a_future_half(self):
        """Both halves index the map directly, so a topic it lacks is a KeyError."""
        missing = [
            choice
            for choice in TEXAS_MANUFACTURING_OUTLOOK_CHOICES
            if f"current_{choice}" not in TEXAS_MANUFACTURING_OUTLOOK
            or f"future_{choice}" not in TEXAS_MANUFACTURING_OUTLOOK
        ]

        assert missing == []


class TestTexasExtract:
    """Reading the series a Texas manufacturing outlook request resolves to."""

    async def test_both_halves_of_a_topic_are_requested(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, TEXAS_NEW_ORDERS_GROWTH, seen=seen)
        await FredManufacturingOutlookTexasFetcher.fetch_data(
            {"topic": "new_orders_growth"}, {}
        )

        assert seen[0]["symbol"].split(",") == [
            "FGROSAMFRBDAL",
            "FGROISAMFRBDAL",
            "FGRODSAMFRBDAL",
            "FGRONSAMFRBDAL",
            "GROSAMFRBDAL",
            "GROISAMFRBDAL",
            "GRODSAMFRBDAL",
            "GRONSAMFRBDAL",
        ]

    async def test_a_lower_frequency_is_sent_as_its_first_letter(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, TEXAS_NEW_ORDERS_GROWTH, seen=seen)
        await FredManufacturingOutlookTexasFetcher.aextract_data(
            FredManufacturingOutlookTexasQueryParams(frequency="annual"), {}
        )

        assert seen[0]["frequency"] == "a"

    async def test_a_failed_request_is_raised_unchanged(self, monkeypatch):
        _fails(monkeypatch, RuntimeError("the transport gave up"))

        with pytest.raises(RuntimeError, match="the transport gave up"):
            await FredManufacturingOutlookTexasFetcher.aextract_data(
                FredManufacturingOutlookTexasQueryParams(), {}
            )

    async def test_a_reported_failure_keeps_its_own_type(self, monkeypatch):
        _fails(monkeypatch, OpenBBError("FRED said no"))

        with pytest.raises(OpenBBError, match="FRED said no"):
            await FredManufacturingOutlookTexasFetcher.aextract_data(
                FredManufacturingOutlookTexasQueryParams(), {}
            )


class TestTexasTransform:
    """Shaping the Texas survey response into one row per topic and date."""

    def test_an_empty_response_is_reported(self):
        with pytest.raises(EmptyDataError, match="rate limiting"):
            FredManufacturingOutlookTexasFetcher.transform_data(
                FredManufacturingOutlookTexasQueryParams(),
                {"metadata": {}, "data": []},
            )

    def test_the_current_and_future_halves_become_their_own_rows(self):
        result = FredManufacturingOutlookTexasFetcher.transform_data(
            FredManufacturingOutlookTexasQueryParams(),
            {"metadata": {}, "data": TEXAS_NEW_ORDERS_GROWTH},
        )

        assert [r.topic for r in result.result] == [
            "current_new_orders_growth",
            "future_new_orders_growth",
        ]

    def test_the_published_percent_columns_are_passed_through_unscaled(self):
        result = FredManufacturingOutlookTexasFetcher.transform_data(
            FredManufacturingOutlookTexasQueryParams(),
            {"metadata": {}, "data": TEXAS_NEW_ORDERS_GROWTH},
        )
        current = result.result[0]

        assert (
            current.percent_reporting_increase,
            current.percent_reporting_decrease,
            current.percent_reporting_no_change,
        ) == (40.0, 27.5, 32.5)

    def test_the_diffusion_index_is_left_as_published(self):
        result = FredManufacturingOutlookTexasFetcher.transform_data(
            FredManufacturingOutlookTexasQueryParams(),
            {"metadata": {}, "data": TEXAS_NEW_ORDERS_GROWTH},
        )

        assert result.result[0].diffusion_index == 12.5

    def test_a_percent_change_transform_does_not_rescale_the_diffusion_index(self):
        result = FredManufacturingOutlookTexasFetcher.transform_data(
            FredManufacturingOutlookTexasQueryParams(transform="pca"),
            {"metadata": {}, "data": TEXAS_NEW_ORDERS_GROWTH},
        )

        assert [r.diffusion_index for r in result.result] == [12.5, 20.0]

    def test_a_natural_log_transform_leaves_the_diffusion_index_alone(self):
        result = FredManufacturingOutlookTexasFetcher.transform_data(
            FredManufacturingOutlookTexasQueryParams(transform="log"),
            {"metadata": {}, "data": TEXAS_NEW_ORDERS_GROWTH},
        )

        assert [r.diffusion_index for r in result.result] == [12.5, 20.0]


class TestSeniorLoanOfficerSurveyExtract:
    """Reading the series one senior loan officer survey category resolves to."""

    async def test_the_spreads_category_is_read_when_none_is_asked_for(
        self, monkeypatch
    ):
        seen: list = []
        _answers(
            monkeypatch,
            [{"date": "2024-04-01", "DRISCFLM": 20.0}],
            {"DRISCFLM": {"title": "Spreads on Loans to Large Firms"}},
            seen=seen,
        )
        await FredSeniorLoanOfficerSurveyFetcher.fetch_data({}, {})

        assert seen[0]["symbol"] == "DRISCFLM,DRISCFS,SUBLPDCLCTSNQ"

    async def test_the_category_chooses_the_series(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, [], SLOOS_AUTO_METADATA, seen=seen)
        await FredSeniorLoanOfficerSurveyFetcher.aextract_data(
            FredSeniorLoanOfficerSurveyQueryParams(category="auto"), {}
        )

        assert seen[0]["symbol"] == "DEMAUTO,STDSAUTO"

    def test_every_offered_category_names_a_series(self):
        """The category indexes the map directly, so a choice it lacks is a KeyError."""
        offered = get_args(
            FredSeniorLoanOfficerSurveyQueryParams.model_fields["category"].annotation
        )

        assert set(offered) == set(SLOOS_CATEGORIES)

    async def test_a_failed_request_is_raised_unchanged(self, monkeypatch):
        _fails(monkeypatch, RuntimeError("the transport gave up"))

        with pytest.raises(RuntimeError, match="the transport gave up"):
            await FredSeniorLoanOfficerSurveyFetcher.aextract_data(
                FredSeniorLoanOfficerSurveyQueryParams(category="auto"), {}
            )


class TestSeniorLoanOfficerSurveyTransform:
    """Shaping the senior loan officer survey response into one row per series."""

    def _transform(self, rows, **kwargs):
        """Return the result of transforming the given wide rows."""
        return FredSeniorLoanOfficerSurveyFetcher.transform_data(
            FredSeniorLoanOfficerSurveyQueryParams(category="auto", **kwargs),
            {"metadata": SLOOS_AUTO_METADATA, "data": rows},
        )

    def test_an_empty_response_is_reported(self):
        with pytest.raises(EmptyDataError, match="returned empty"):
            self._transform([])

    def test_a_response_with_no_readings_at_all_is_reported(self):
        with pytest.raises(EmptyDataError, match="returned empty"):
            self._transform([{"date": date(2011, 4, 1), "DEMAUTO": None}])

    def test_a_date_one_series_does_not_reach_keeps_the_other_series(self):
        """A series that starts later must not truncate the one that starts earlier."""
        result = self._transform(
            [
                {"date": date(2011, 1, 1), "DEMAUTO": 10.0, "STDSAUTO": None},
                {"date": date(2011, 4, 1), "DEMAUTO": 20.0, "STDSAUTO": 5.0},
            ]
        )

        assert [(r.date, r.symbol) for r in result.result] == [
            (date(2011, 1, 1), "DEMAUTO"),
            (date(2011, 4, 1), "DEMAUTO"),
            (date(2011, 4, 1), "STDSAUTO"),
        ]

    def test_the_published_value_is_passed_through_unscaled(self):
        result = self._transform(
            [{"date": date(2011, 4, 1), "DEMAUTO": 20.0, "STDSAUTO": 5.0}]
        )

        assert [r.value for r in result.result] == [20.0, 5.0]

    def test_each_row_carries_the_title_of_its_series(self):
        result = self._transform(
            [{"date": date(2011, 4, 1), "DEMAUTO": 20.0, "STDSAUTO": 5.0}]
        )

        assert [r.title for r in result.result] == [
            "Demand for Auto Loans",
            "Lending Standards for Auto Loans",
        ]

    def test_a_series_with_no_title_is_reported_without_one(self):
        result = FredSeniorLoanOfficerSurveyFetcher.transform_data(
            FredSeniorLoanOfficerSurveyQueryParams(category="auto"),
            {
                "metadata": {"DEMAUTO": {}},
                "data": [{"date": date(2011, 4, 1), "DEMAUTO": 20.0}],
            },
        )

        assert result.result[0].title == ""


class TestChicagoSurveyFields:
    """The fields the Chicago survey reports its series under."""

    def test_every_series_is_reported_under_a_declared_field(self):
        """A field the data model does not declare is invisible to the caller."""
        declared = set(FredSurveyOfEconomicConditionsChicagoData.model_fields)

        assert set(CHICAGO_ID_TO_FIELD.values()) - declared == set()


class TestChicagoSurveyExtract:
    """Reading the series a Chicago survey request resolves to."""

    async def test_every_published_series_is_requested(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, CHICAGO_ACTIVITY, seen=seen)
        await FredSurveyOfEconomicConditionsChicagoFetcher.fetch_data({}, {})

        assert seen[0]["symbol"].split(",") == list(CHICAGO_ID_TO_FIELD)

    async def test_a_lower_frequency_is_sent_as_its_first_letter(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, CHICAGO_ACTIVITY, seen=seen)
        await FredSurveyOfEconomicConditionsChicagoFetcher.aextract_data(
            FredSurveyOfEconomicConditionsChicagoQueryParams(frequency="quarter"), {}
        )

        assert seen[0]["frequency"] == "q"

    async def test_a_failed_request_is_raised_unchanged(self, monkeypatch):
        _fails(monkeypatch, RuntimeError("the transport gave up"))

        with pytest.raises(RuntimeError, match="the transport gave up"):
            await FredSurveyOfEconomicConditionsChicagoFetcher.aextract_data(
                FredSurveyOfEconomicConditionsChicagoQueryParams(), {}
            )


class TestChicagoSurveyTransform:
    """Shaping the Chicago survey response into one row per date."""

    def _transform(self, rows, **kwargs):
        """Return the result of transforming the given wide rows."""
        return FredSurveyOfEconomicConditionsChicagoFetcher.transform_data(
            FredSurveyOfEconomicConditionsChicagoQueryParams(**kwargs),
            {"metadata": {}, "data": rows},
        )

    def test_an_empty_response_is_reported(self):
        with pytest.raises(EmptyDataError, match="returned empty"):
            self._transform([])

    def test_each_series_is_reported_under_its_field_name(self):
        row = self._transform(CHICAGO_ACTIVITY).result[0]

        assert (
            row.activity_index,
            row.one_year_outlook,
            row.manufacturing_activity,
            row.non_manufacturing_activity,
            row.capital_expenditures_expectations,
            row.hiring_expectations,
            row.current_hiring,
            row.labor_costs,
            row.non_labor_costs,
        ) == (1.5, -2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)

    def test_the_indexes_are_left_as_published(self):
        row = self._transform(CHICAGO_ACTIVITY).result[0]

        assert row.activity_index == 1.5

    def test_a_percent_change_transform_does_not_rescale_any_index(self):
        row = self._transform(CHICAGO_ACTIVITY, transform="pc1").result[0]

        assert (row.activity_index, row.one_year_outlook) == (1.5, -2.0)

    def test_a_level_change_transform_leaves_every_index_alone(self):
        row = self._transform(CHICAGO_ACTIVITY, transform="ch1").result[0]

        assert (row.activity_index, row.one_year_outlook) == (1.5, -2.0)

    def test_the_rows_are_ordered_by_date(self):
        result = self._transform(
            [
                {"date": "2024-06-01", "CFSBCACTIVITY": 2.0},
                {"date": "2024-05-01", "CFSBCACTIVITY": 1.0},
            ]
        )

        assert [r.date for r in result.result] == [date(2024, 5, 1), date(2024, 6, 1)]


class TestUniversityOfMichiganExtract:
    """Reading the series a University of Michigan request resolves to."""

    async def test_the_spliced_history_is_requested_when_no_start_date_is_given(
        self, monkeypatch
    ):
        """UMCSENT only starts in 1978, so the earlier readings come from UMCSENT1."""
        seen: list = []
        _answers(monkeypatch, MICHIGAN_SENTIMENT, seen=seen)
        await FredUofMichiganFetcher.fetch_data({}, {})

        assert seen[0]["symbol"] == "UMCSENT,MICH,UMCSENT1"

    async def test_the_spliced_history_is_requested_for_an_earlier_start_date(
        self, monkeypatch
    ):
        seen: list = []
        _answers(monkeypatch, MICHIGAN_SENTIMENT, seen=seen)
        await FredUofMichiganFetcher.aextract_data(
            FredUofMichiganQueryParams(start_date=date(1977, 12, 31)), {}
        )

        assert seen[0]["symbol"] == "UMCSENT,MICH,UMCSENT1"

    async def test_the_spliced_history_is_left_out_for_a_later_start_date(
        self, monkeypatch
    ):
        seen: list = []
        _answers(monkeypatch, MICHIGAN_SENTIMENT, seen=seen)
        await FredUofMichiganFetcher.aextract_data(
            FredUofMichiganQueryParams(start_date=date(1978, 1, 1)), {}
        )

        assert seen[0]["symbol"] == "UMCSENT,MICH"

    async def test_a_lower_frequency_is_sent_as_its_first_letter(self, monkeypatch):
        seen: list = []
        _answers(monkeypatch, MICHIGAN_SENTIMENT, seen=seen)
        await FredUofMichiganFetcher.aextract_data(
            FredUofMichiganQueryParams(frequency="annual"), {}
        )

        assert seen[0]["frequency"] == "a"

    async def test_a_failed_request_is_raised_unchanged(self, monkeypatch):
        _fails(monkeypatch, RuntimeError("the transport gave up"))

        with pytest.raises(RuntimeError, match="the transport gave up"):
            await FredUofMichiganFetcher.aextract_data(FredUofMichiganQueryParams(), {})


class TestUniversityOfMichiganTransform:
    """Shaping the University of Michigan response into one row per date."""

    def _transform(self, rows, metadata=None, **kwargs):
        """Return the result of transforming the given wide rows."""
        return FredUofMichiganFetcher.transform_data(
            FredUofMichiganQueryParams(**kwargs),
            {"metadata": {} if metadata is None else metadata, "data": rows},
        )

    def test_an_empty_response_is_reported(self):
        with pytest.raises(EmptyDataError, match="returned empty"):
            self._transform([])

    def test_the_spliced_history_fills_the_gap_in_the_headline_series(self):
        result = self._transform(MICHIGAN_SENTIMENT)

        assert [r.consumer_sentiment for r in result.result] == [90.6, 69.1]

    def test_the_spliced_history_is_not_reported_as_a_series_of_its_own(self):
        result = self._transform(
            MICHIGAN_SENTIMENT,
            {"UMCSENT": {"title": "Sentiment"}, "UMCSENT1": {"title": "Spliced"}},
        )

        assert list(result.metadata) == ["UMCSENT"]

    def test_the_spliced_history_is_not_reported_as_a_column_of_its_own(self):
        result = self._transform(MICHIGAN_SENTIMENT)

        assert "UMCSENT1" not in result.result[0].model_dump()

    def test_the_published_inflation_expectation_is_passed_through_unscaled(self):
        result = self._transform(MICHIGAN_SENTIMENT)

        assert [r.inflation_expectation for r in result.result] == [6.5, 3.3]

    def test_the_sentiment_index_is_left_as_published(self):
        result = self._transform(MICHIGAN_SENTIMENT)

        assert result.result[1].consumer_sentiment == 69.1

    def test_a_percent_change_transform_does_not_rescale_the_sentiment_index(self):
        result = self._transform(MICHIGAN_SENTIMENT, transform="pch")

        assert result.result[1].consumer_sentiment == 69.1

    def test_a_level_change_transform_leaves_the_sentiment_index_alone(self):
        result = self._transform(MICHIGAN_SENTIMENT, transform="chg")

        assert result.result[1].consumer_sentiment == 69.1

    def test_a_natural_log_transform_leaves_the_sentiment_index_alone(self):
        result = self._transform(MICHIGAN_SENTIMENT, transform="log")

        assert result.result[1].consumer_sentiment == 69.1

    def test_a_response_without_the_spliced_history_is_read_as_it_comes(self):
        result = self._transform([{"date": "2024-05-01", "UMCSENT": 69.1, "MICH": 3.3}])

        assert result.result[0].consumer_sentiment == 69.1
