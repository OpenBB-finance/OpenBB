# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import substack_model


@pytest.mark.vcr
def test_get_newsletters(recorder, mocker):
    # MOCK LEN
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.substack_model.len",
        return_value=1,
    )

    df = substack_model.get_newsletters()
    recorder.capture(df)
