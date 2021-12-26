# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import financedatabase_view


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
    mocker.patch.object(
        target=financedatabase_view.gtff, attribute="USE_TABULATE_DF", new=use_tab
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
