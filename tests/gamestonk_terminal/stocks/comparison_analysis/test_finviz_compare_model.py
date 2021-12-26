# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import finviz_compare_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "compare_list",
    [
        ["Industry"],
        ["MOCK_INVALID_COMPARE_LIST"],
    ],
)
def test_get_similar_companies(compare_list, recorder):
    result_tuple = finviz_compare_model.get_similar_companies(
        ticker="TSLA",
        compare_list=compare_list,
    )

    recorder.capture(result_tuple)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "data_type",
    [
        "overview",
        "valuation",
        "financial",
        "ownership",
        "overview",
        "performance",
        "technical",
        "MOCK_INVALID_DATA_TYPE",
    ],
)
def test_get_comparison_data(data_type, recorder):
    result_df = finviz_compare_model.get_comparison_data(
        data_type=data_type,
        similar=["TESLA", "GM"],
    )

    recorder.capture(result_df)
