# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.screener import finviz_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "data_type",
    [
        "MOCK_DATA_TYPE",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
    ],
)
def test_get_screener_data(data_type, recorder):
    result_df = finviz_model.get_screener_data(
        preset_loaded="top_gainers",
        data_type=data_type,
        limit=2,
        ascend=True,
    )

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_screener_data_no_preset_loaded(mocker, recorder):
    # MOCK D_SIGNALS
    mocker.patch.object(
        target=finviz_model,
        attribute="d_signals",
        new=[],
    )

    result_df = finviz_model.get_screener_data(
        preset_loaded="oversold",
        data_type="overview",
        limit=2,
        ascend=True,
    )

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_screener_data_no_limit(recorder):
    result_df = finviz_model.get_screener_data(
        preset_loaded="oversold",
        data_type="overview",
        limit=-1,
        ascend=True,
    )

    recorder.capture(result_df)
