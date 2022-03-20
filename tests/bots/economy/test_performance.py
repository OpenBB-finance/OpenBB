import pytest

from bots.economy.performance import performance_command


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
def test_performance_command(mocker, recorder, group):
    mocker.patch(target="bots.economy.performance.save_image", return_value=None)
    value = performance_command(group)

    recorder.capture(value)
