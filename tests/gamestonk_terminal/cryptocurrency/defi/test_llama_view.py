import pytest

from gamestonk_terminal.cryptocurrency.defi import llama_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_protocols():
    llama_view.display_defi_protocols(20, "tvl", False, False)


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_tvl():
    llama_view.display_defi_tvl(20)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_grouped_defi_protocols():
    llama_view.display_grouped_defi_protocols(20)


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical_tvl():
    llama_view.display_historical_tvl("sushiswap,uniswap")
