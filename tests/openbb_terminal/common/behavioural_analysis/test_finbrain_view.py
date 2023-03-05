# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

from openbb_terminal.common.behavioural_analysis import finbrain_view

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)


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
    preferences = PreferencesModel(USE_ION=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch.object(
        target=finbrain_view.rich_config, attribute="USE_COLOR", new=color
    )

    finbrain_view.display_sentiment_analysis(
        symbol="AAPL",
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
    preferences = PreferencesModel(USE_ION=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    # MOCK GET_SENTIMENT
    mocker.patch(
        target=f"{view}.finbrain_model.get_sentiment",
        return_value=pd.DataFrame(),
    )

    finbrain_view.display_sentiment_analysis(
        symbol="AAPL",
        export="",
    )
