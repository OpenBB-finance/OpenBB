import pytest

from openbb_terminal.cryptocurrency.overview import loanscan_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "rate_type",
    ["borrow", "supply"],
)
def test_get_rates(rate_type, recorder):
    df = loanscan_model.get_rates(rate_type=rate_type)
    recorder.capture(df)
