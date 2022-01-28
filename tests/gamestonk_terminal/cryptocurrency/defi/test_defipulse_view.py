# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import defipulse_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_vaults(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.defipulse_view.export_data"
    )

    defipulse_view.display_defipulse(
        top=5,
        sortby="Rank",
        descend=False,
        export="",
    )
