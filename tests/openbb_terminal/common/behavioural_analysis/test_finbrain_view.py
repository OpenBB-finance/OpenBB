# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.behavioural_analysis import finbrain_view
from openbb_terminal import helper_funcs


@pytest.mark.default_cassette("test_display_sentiment_analysis")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize("color", [True, False])
def test_display_sentiment_analysis(color, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.common.behavioural_analysis.finbrain_view.export_data"
    )

    # MOCK OBBFF
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_ION", new=True)
    mocker.patch.object(
        target=finbrain_view.rich_config, attribute="USE_COLOR", new=color
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    finbrain_view.display_sentiment_analysis(
        ticker="AAPL",
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_display_sentiment_analysis_empty_df(mocker):
    view = "openbb_terminal.common.behavioural_analysis.finbrain_view"

    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.common.behavioural_analysis.finbrain_view.export_data"
    )

    # MOCK OBBFF
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_ION", new=True)

    # MOCK GET_SENTIMENT
    mocker.patch(
        target=f"{view}.finbrain_model.get_sentiment",
        return_value=pd.DataFrame(),
    )

    finbrain_view.display_sentiment_analysis(
        ticker="AAPL",
        export="",
    )
