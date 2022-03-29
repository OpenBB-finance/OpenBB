# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_model


@pytest.mark.vcr
def test_get_dark_pool_short_positions(recorder):
    result_df = stockgrid_model.get_dark_pool_short_positions(
        sort_field="sv",
        ascending=True,
    )

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_short_interest_days_to_cover(recorder):
    result_df = stockgrid_model.get_short_interest_days_to_cover(
        sort_field="dtc",
    )

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_short_interest_volume(recorder):
    result_df, price_list = stockgrid_model.get_short_interest_volume(
        ticker="PM",
    )

    recorder.capture(result_df)
    recorder.capture(price_list)
