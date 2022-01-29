# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import terraengineer_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_anchor_yield_reserve(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terraengineer_view.export_data"
    )

    # MOCK GTFF
    mocker.patch.object(target=terraengineer_view.gtff, attribute="USE_ION", new=True)

    # MOCK ION + SHOW
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terraengineer_view.plt.ion"
    )
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terraengineer_view.plt.show"
    )

    terraengineer_view.display_anchor_yield_reserve()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_terra_asset_history(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terraengineer_view.export_data"
    )

    # MOCK GTFF
    mocker.patch.object(target=terraengineer_view.gtff, attribute="USE_ION", new=True)

    # MOCK ION + SHOW
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terraengineer_view.plt.ion"
    )
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.terraengineer_view.plt.show"
    )

    terraengineer_view.display_terra_asset_history(
        asset="ust", address="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"
    )
