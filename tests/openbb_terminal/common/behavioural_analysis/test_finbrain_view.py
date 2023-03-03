# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

from openbb_terminal.common.behavioural_analysis import finbrain_view

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user


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
    current_user = get_current_user()
    preference = PreferencesModel(USE_ION=True)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
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
    current_user = get_current_user()
    preference = PreferencesModel(USE_ION=True)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
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
