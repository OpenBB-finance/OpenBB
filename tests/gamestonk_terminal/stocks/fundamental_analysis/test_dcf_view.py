# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import dcf_view, dcf_static


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
def test_create_xls():
    for ticker in ["AEIS"]:
        excel = dcf_view.CreateExcelFA(ticker, False)
        df_is = excel.get_data("IS", 1, True)
        items_is = dcf_static.non_gaap_is + dcf_static.gaap_is
        for item in df_is.index:
            assert item in items_is
        df_bs = excel.get_data("BS", 1, True)
        items_bs = dcf_static.non_gaap_bs + dcf_static.gaap_bs
        for item in df_bs.index:
            assert item in items_bs
        df_cf = excel.get_data("CF", 1, True)
        items_cf = dcf_static.non_gaap_cf + dcf_static.gaap_cf
        for item in df_cf.index:
            assert item in items_cf


@pytest.mark.skip
@pytest.mark.vcr
def test_create_workbook(mocker):
    excel = dcf_view.CreateExcelFA(ticker="AEIS", audit=False)
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.dcf_view.random.shuffle"
    )
    mocker.patch.object(excel.wb, "save")
    excel.create_workbook()
