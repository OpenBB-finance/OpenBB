# IMPORTATION THIRDPARTY
from io import StringIO
import pytest
import pandas as pd

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.behavioural_analysis import cramer_view

closes = pd.read_csv(
    StringIO(
        """
Date,Adj Close
2022-01-03, 181.7783966064453
2022-01-04, 179.47134399414062
2022-01-05, 174.69741821289062
2022-01-06, 171.78114318847656
2022-01-07, 171.950927734375
2022-01-10, 171.9709014892578
2022-01-11, 174.8572235107422
2022-01-12, 175.306640625
2022-01-13, 171.9709014892578
2022-01-14, 172.84979248046875
2022-01-18, 169.5839385986328
2022-01-19, 166.0184783935547
2022-01-20, 164.3006591796875
2022-01-21, 162.20335388183594
2022-01-24, 161.41433715820312
2022-01-25, 159.57669067382812
2022-01-26, 159.48680114746094
2022-01-27, 159.0174102783203
2022-01-28, 170.11326599121094
2022-01-31, 174.55760192871094
2022-02-01, 174.3878173828125
2022-02-02, 175.6162567138672
2022-02-03, 172.67999267578125
2022-02-04, 172.38999938964844
2022-02-07, 171.66000366210938
2022-02-08, 174.8300018310547
2022-02-09, 176.27999877929688
2022-02-10, 172.1199951171875
2022-02-11, 168.63999938964844
2022-02-14, 168.8800048828125
2022-02-15, 172.7899932861328
2022-02-16, 172.5500030517578
2022-02-17, 168.8800048828125
2022-02-18, 167.3000030517578
2022-02-22, 164.32000732421875
2022-02-23, 160.07000732421875
2022-02-24, 162.74000549316406
2022-02-25, 164.85000610351562
2022-02-28, 165.1199951171875
2022-03-01, 163.1999969482422
2022-03-02, 166.55999755859375
2022-03-03, 166.22999572753906
2022-03-04, 163.1699981689453
2022-03-07, 159.3000030517578
2022-03-09, 162.01499938964844
"""
    )
).set_index("Date")
closes.index = pd.to_datetime(closes.index)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "inverse",
    [True, False],
)
def test_get_orders(inverse):
    cramer_view.display_cramer_daily(inverse=inverse)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize("raw", [True, False])
def test_cramer_ticker(mocker, raw):
    mocker.patch(
        target="gamestonk_terminal.stocks.behavioural_analysis.cramer_view.theme.visualize_output"
    )
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.behavioural_analysis.cramer_view.export_data"
    )

    mocker.patch(
        target="gamestonk_terminal.stocks.behavioural_analysis.cramer_view.yfinance.download",
        new=mocker.Mock(return_value=closes.copy()),
    )

    cramer_view.display_cramer_ticker("AAPL", raw=raw)
