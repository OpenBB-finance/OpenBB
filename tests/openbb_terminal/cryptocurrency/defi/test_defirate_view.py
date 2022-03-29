# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import defirate_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_funding_rates(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.defi.defirate_view.export_data")

    defirate_view.display_funding_rates(
        top=5,
        current=True,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_lending_rates(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.defi.defirate_view.export_data")

    defirate_view.display_lending_rates(
        top=5,
        current=True,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_borrow_rates(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.defi.defirate_view.export_data")

    defirate_view.display_borrow_rates(
        top=5,
        current=True,
        export="",
    )
