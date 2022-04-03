# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import defipulse_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defipulse(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.defi.defipulse_view.export_data"
    )

    defipulse_view.display_defipulse(
        top=5,
        sortby="Rank",
        descend=False,
        export="",
    )
