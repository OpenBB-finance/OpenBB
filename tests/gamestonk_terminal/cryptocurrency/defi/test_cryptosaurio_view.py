# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import cryptosaurio_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_anchor_data(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.defi.cryptosaurio_view.export_data"
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    cryptosaurio_view.display_anchor_data(
        address="terra13kc0x8kr3sq8226myf4nmanmn2mrk9s5s9wsnz"
    )
