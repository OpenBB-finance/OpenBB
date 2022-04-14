# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.tools import tools_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_il(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.tools.tools_view.export_data")

    tools_view.display_il(
        price_changeA=100,
        price_changeB=200,
        proportion=50,
        initial_pool_value=1000,
        narrative=False,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_apy(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.tools.tools_view.export_data")

    tools_view.display_apy(
        apr=100,
        compounding_times=12,
        narrative=False,
        export="",
    )
