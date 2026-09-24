"""Tests for the shared FRED query parameters and date normalization."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_fred.utils.query import UseCacheQueryParams, join_dates

DATE_MODELS = (
    "openbb_fred.models.high_quality_market.FredHighQualityMarketCorporateBondQueryParams",
    "openbb_fred.models.non_farm_payrolls.FredNonFarmPayrollsQueryParams",
    "openbb_fred.models.personal_consumption_expenditures.FredPersonalConsumptionExpendituresQueryParams",
)


def _load(path: str):
    """Return the class one dotted path names."""
    from importlib import import_module

    module, name = path.rsplit(".", 1)

    return getattr(import_module(module), name)


class TestJoinDates:
    """Normalizing the date parameter to comma-separated ISO dates."""

    def test_nothing_reads_as_nothing(self):
        assert join_dates(None) is None

    def test_a_date_is_written_out(self):
        assert join_dates(date(2024, 3, 17)) == "2024-03-17"

    def test_a_single_string_is_kept(self):
        assert join_dates("2024-03-17") == "2024-03-17"

    def test_a_comma_separated_string_is_kept(self):
        assert join_dates("2024-03-17,2024-04-30") == "2024-03-17,2024-04-30"

    def test_a_list_of_dates_is_joined(self):
        assert join_dates([date(2024, 3, 17), date(2024, 4, 30)]) == (
            "2024-03-17,2024-04-30"
        )

    def test_a_list_of_strings_is_joined(self):
        assert join_dates(["2024-03-17", "2024-04-30"]) == "2024-03-17,2024-04-30"

    def test_a_mixed_list_is_joined(self):
        assert join_dates([date(2024, 3, 17), "2024-04-30"]) == (
            "2024-03-17,2024-04-30"
        )

    def test_a_loosely_written_date_is_read(self):
        assert join_dates("17 March 2024") == "2024-03-17"

    def test_a_comma_always_separates(self):
        """A date written with a comma in it is two entries, not one."""
        assert join_dates("March 17, 2024") != "2024-03-17"

    def test_padding_is_ignored(self):
        assert join_dates(" 2024-03-17 , 2024-04-30 ") == "2024-03-17,2024-04-30"

    def test_an_empty_entry_is_dropped(self):
        assert join_dates("2024-03-17,,") == "2024-03-17"

    def test_nothing_but_separators_reads_as_nothing(self):
        assert join_dates(",,") is None

    def test_an_unreadable_date_is_reported(self):
        with pytest.raises(OpenBBError, match="Invalid date: not-a-date"):
            join_dates("not-a-date")


class TestUseCacheQueryParams:
    """The cache switch every FRED query carries."""

    def test_the_cache_is_used_by_default(self):
        assert UseCacheQueryParams().use_cache is True

    def test_the_cache_can_be_refused(self):
        assert UseCacheQueryParams(use_cache=False).use_cache is False

    def test_every_fetcher_offers_the_switch(self):
        from openbb_fred import fred_provider

        without = [
            name
            for name, fetcher in fred_provider.fetcher_dict.items()
            if "use_cache" not in fetcher.query_params_type.model_fields
        ]

        assert without == []

    def test_the_standard_parameters_still_lead(self):
        from openbb_fred.models.series import FredSeriesQueryParams

        fields = list(FredSeriesQueryParams.model_fields)

        assert fields.index("symbol") < fields.index("use_cache")


class TestDateParameters:
    """The ``date`` parameter of the models that read a published release."""

    @pytest.mark.parametrize("path", DATE_MODELS)
    def test_nothing_reads_as_nothing(self, path):
        assert _load(path)(date=None).date is None

    @pytest.mark.parametrize("path", DATE_MODELS)
    def test_a_date_becomes_a_written_date(self, path):
        assert _load(path)(date=date(2024, 3, 17)).date == "2024-03-17"

    @pytest.mark.parametrize("path", DATE_MODELS)
    def test_a_list_is_accepted(self, path):
        """``multiple_items_allowed`` promises a list is read."""
        assert _load(path)(date=[date(2024, 3, 17), date(2024, 4, 30)]).date == (
            "2024-03-17,2024-04-30"
        )

    @pytest.mark.parametrize("path", DATE_MODELS)
    def test_a_comma_separated_string_is_accepted(self, path):
        assert _load(path)(date="2024-03-17,2024-04-30").date == (
            "2024-03-17,2024-04-30"
        )

    def test_the_release_table_normalizes_through_the_standard_model(self):
        from openbb_fred.models.release_table import FredReleaseTableQueryParams

        query = FredReleaseTableQueryParams(release_id="50", date="2024-03-17")

        assert query.date == "2024-03-17"
