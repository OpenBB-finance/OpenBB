# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import dcf_static, dcf_view

# TODO: Make this unit test testable by adding start and end date constraints
# Currently, the size of the data returned is too large to be recorded and pushed.


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.vcr
def test_create_xls():
    for ticker in ["MSFT"]:
        excel = dcf_view.CreateExcelFA(ticker, False, 1)
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


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_create_workbook(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1)

    # MOCK GENERATE_PATH
    attrs = {
        "is_file.return_value": False,
    }
    mock_path = mocker.Mock(**attrs)
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.dcf_model.generate_path",
        return_value=mock_path,
    )

    # MOCK SAVE
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.Workbook.save"
    )

    excel.create_workbook()


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_add_estimates(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1)

    # MOCK ADD ESTIMATES
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.add_estimates"
    )

    excel.add_estimates()


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_create_dcf(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1)

    # MOCK ADD DCF
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.create_dcf"
    )

    excel.create_dcf()


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_run_audit(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=True, beta=1)

    # MOCK ADD DCF
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.run_audit"
    )

    excel.run_audit()


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_get_growth(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1)

    # MOCK GET GROWTH
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.get_growth"
    )

    excel.get_growth(x_ind=1, y_ind=1)


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_get_sum(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1, len_pred=1)

    # MOCK GET SUM
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.get_sum"
    )

    excel.get_sum("Gross Profit", "Revenue", [], ["Cost of Revenue"])


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_custom_exp(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1)

    # MOCK CUSTOM EXP
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.custom_exp"
    )

    excel.custom_exp(
        "Preferred Dividends",
        "Preferred Dividends are not important in a DCF so we do not attempt to predict them.",
    )


@pytest.mark.skip(reason="Too long to run")
@pytest.mark.record_http
def test_add_ratios(mocker):
    excel = dcf_view.CreateExcelFA(symbol="AAPL", audit=False, beta=1)

    # MOCK ADD RATIOS
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.dcf_view.CreateExcelFA.add_ratios"
    )

    excel.add_ratios()
