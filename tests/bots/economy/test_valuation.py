import pytest

from bots.economy.valuation import valuation_command


@pytest.mark.parametrize(
    "group",
    [
        "sector",
        "industry",
        "basic_materials",
        "communication_services",
        "consumer_cyclical",
        "consumer_defensive",
        "energy",
        "financial",
        "healthcare",
        "industrials",
        "real_estate",
        "technology",
        "utilities",
        "country",
        "capitalization",
    ],
)
@pytest.mark.vcr
def test_valuation_command(mocker, recorder, group):
    mocker.patch(target="bots.economy.valuation.save_image", return_value=None)
    value = valuation_command(group)

    recorder.capture(value)
