# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.stocks.discovery import financedatabase_view


@pytest.mark.default_cassette("test_show_equities")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "kwargs_dict, use_tab",
    [
        (
            {
                "country": ["France"],
                "sector": ["Healthcare"],
                "industry": ["Biotechnology"],
            },
            True,
        ),
        (
            {
                "country": ["France"],
                "sector": ["Healthcare"],
                "industry": ["Biotechnology"],
            },
            False,
        ),
    ],
)
def test_show_equities(kwargs_dict, mocker, use_tab):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=use_tab)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    kwargs_dict_none = {
        "country": None,
        "sector": None,
        "industry": None,
        "name": None,
        "description": None,
        "marketcap": None,
        "amount": None,
        "include_exchanges": None,
        "options": None,
    }

    kwargs_dict = {**kwargs_dict_none, **kwargs_dict}

    financedatabase_view.show_equities(**kwargs_dict)
