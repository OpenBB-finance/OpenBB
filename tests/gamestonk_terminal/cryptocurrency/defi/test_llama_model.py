import pytest

from gamestonk_terminal.cryptocurrency.defi import llama_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "protocol",
    [
        "sushiswap",
        "anchor",
    ],
)
def test_get_defi_protocol(protocol, recorder):
    df = llama_model.get_defi_protocol(protocol)
    recorder.capture(df)


@pytest.mark.skip
@pytest.mark.vcr
def test_get_defi_protocols(recorder):
    df = llama_model.get_defi_protocols()
    recorder.capture(df)


@pytest.mark.skip
@pytest.mark.vcr
def test_get_defi_tvl(recorder):
    df = llama_model.get_defi_tvl()
    recorder.capture(df)
