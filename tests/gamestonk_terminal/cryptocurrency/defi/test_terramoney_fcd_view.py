# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import terramoney_fcd_view


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (
            "display_account_staking_info",
            dict(address="terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg"),
        ),
        ("display_validators", dict()),
        ("display_gov_proposals", dict()),
        ("display_account_growth", dict()),
        ("display_staking_ratio_history", dict()),
        ("display_staking_returns_history", dict()),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terramoney_fcd_view.export_data"
    )

    # MOCK GTFF
    mocker.patch.object(target=terramoney_fcd_view.gtff, attribute="USE_ION", new=True)

    # MOCK ION + SHOW
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terramoney_fcd_view.plt.ion"
    )
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terramoney_fcd_view.plt.show"
    )

    getattr(terramoney_fcd_view, func)(**kwargs)
