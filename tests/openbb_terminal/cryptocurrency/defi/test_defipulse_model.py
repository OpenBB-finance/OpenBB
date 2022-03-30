# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import defipulse_model


@pytest.mark.vcr
def test_get_defipulse_index(recorder):
    df = defipulse_model.get_defipulse_index()
    recorder.capture(df)
