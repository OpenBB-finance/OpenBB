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
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = performance_command(group)
    value["view"] = value["view"].__name__
    value["embed"] = None
    value["choices"] = None
    recorder.capture(value)
