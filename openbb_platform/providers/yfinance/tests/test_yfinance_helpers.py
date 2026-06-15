"""Test yfinance helpers."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from openbb_yfinance.models.equity_quote import (
    YFinanceEquityQuoteFetcher,
    YFinanceEquityQuoteQueryParams,
)
from openbb_yfinance.utils.helpers import (
    df_transform_numbers,
    get_custom_screener,
    get_defined_screener,
    get_futures_data,
    get_futures_symbols,
    normalize_yfinance_symbol,
    normalize_yfinance_symbols,
    yf_download,
)

# pylint: disable=redefined-outer-name, unused-argument

MOCK_FUTURES_DATA = pd.DataFrame({"Ticker": ["ES", "NQ"], "Exchange": ["CME", "CME"]})


@pytest.fixture
def mock_futures_csv(monkeypatch):
    """Mock pd.read_csv to return predefined futures data."""
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: MOCK_FUTURES_DATA)


def test_get_futures_data(mock_futures_csv):
    """Test get_futures_data."""
    df = get_futures_data()
    assert not df.empty
    assert df.equals(MOCK_FUTURES_DATA)


def test_df_transform_numbers():
    """Test df_transform_numbers."""
    data = pd.DataFrame(
        {"Value": ["1M", "2.5B", "3T"], "% Change": ["1%", "-2%", "3.5%"]}
    )
    transformed = df_transform_numbers(data, ["Value", "% Change"])
    assert transformed["Value"].equals(pd.Series([1e6, 2.5e9, 3e12]))
    assert transformed["% Change"].equals(pd.Series([1 / 100, -2 / 100, 3.5 / 100]))


@pytest.mark.parametrize(
    ("symbol", "expected"),
    [
        ("BRK.A", "BRK-A"),
        ("BF.B", "BF-B"),
        ("ABC.C", "ABC-C"),
        ("7203.T", "7203.T"),
        ("RY.TO", "RY.TO"),
        ("VOD.L", "VOD.L"),
        ("BTC-USD", "BTC-USD"),
        ("^GSPC", "^GSPC"),
        ("ES=F", "ES=F"),
    ],
)
def test_normalize_yfinance_symbol(symbol, expected):
    """Test class-share symbol normalization for yfinance requests."""
    assert normalize_yfinance_symbol(symbol) == expected


def test_normalize_yfinance_symbols():
    """Test comma-separated class-share symbol normalization."""
    symbols = "BRK.A,BF.B,7203.T,RY.TO,BTC-USD,^GSPC,ES=F"

    assert (
        normalize_yfinance_symbols(symbols)
        == "BRK-A,BF-B,7203.T,RY.TO,BTC-USD,^GSPC,ES=F"
    )


@pytest.mark.asyncio
async def test_get_custom_screener_no_session():
    """Test that get_custom_screener does not pass session to YfData."""
    with patch("yfinance.data.YfData") as mock_yfdata:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "finance": {
                "result": [
                    {
                        "quotes": [
                            {
                                "symbol": "AAPL",
                                "exchangeTimezoneName": "America/New_York",
                                "regularMarketTime": 1700000000,
                            }
                        ],
                        "total": 1,
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_yfdata.return_value = mock_instance

        await get_custom_screener({"query": {}}, limit=1)

        # Verify YfData was called without session parameter
        mock_yfdata.assert_called_once()
        call_kwargs = mock_yfdata.call_args[1] if mock_yfdata.call_args[1] else {}
        assert (
            "session" not in call_kwargs
        ), "YfData should not be called with session parameter"


@pytest.mark.asyncio
async def test_get_defined_screener_no_session():
    """Test that get_defined_screener does not pass session to yf.screen."""
    with patch("yfinance.screen") as mock_screen:
        mock_screen.return_value = {
            "quotes": [
                {
                    "symbol": "AAPL",
                    "exchangeTimezoneName": "America/New_York",
                    "regularMarketTime": 1700000000,
                    "regularMarketChange": 1.23,
                    "regularMarketVolume": 1000,
                }
            ],
            "total": 1,
        }

        await get_defined_screener("day_gainers", limit=1)

        # Verify yf.screen was called without session parameter
        assert mock_screen.called
        for call in mock_screen.call_args_list:
            call_kwargs = call[1] if len(call) > 1 and call[1] else {}
            assert (
                "session" not in call_kwargs
            ), "yf.screen should not be called with session parameter"


def test_get_futures_symbols_no_session():
    """Test that get_futures_symbols does not pass session to YfData."""
    with patch("yfinance.data.YfData") as mock_yfdata:
        mock_instance = MagicMock()
        mock_instance.get_raw_json.return_value = {
            "quoteSummary": {
                "result": [{"futuresChain": {"futures": [{"symbol": "ES=F"}]}}]
            }
        }
        mock_yfdata.return_value = mock_instance

        get_futures_symbols("ES")

        # Verify YfData was called without session parameter
        mock_yfdata.assert_called_once()
        call_kwargs = mock_yfdata.call_args[1] if mock_yfdata.call_args[1] else {}
        assert (
            "session" not in call_kwargs
        ), "YfData should not be called with session parameter"


def test_yf_download_no_session():
    """Test that yf_download does not pass session to yf.download."""
    with patch("yfinance.download") as mock_download:
        # Mock DataFrame with MultiIndex columns as returned by yfinance.download with group_by="ticker"
        columns = pd.MultiIndex.from_tuples(
            [
                ("AAPL", "Open"),
                ("AAPL", "High"),
                ("AAPL", "Low"),
                ("AAPL", "Close"),
                ("AAPL", "Adj Close"),
            ]
        )
        idx = pd.to_datetime(["2023-01-03"])
        idx.name = "Date"
        mock_data = pd.DataFrame([[100, 110, 90, 105, 105]], columns=columns, index=idx)
        mock_download.return_value = mock_data

        yf_download("AAPL", start_date="2023-01-01", end_date="2023-01-10")

        # Verify yf.download was called without session parameter
        assert mock_download.called
        for call in mock_download.call_args_list:
            call_kwargs = call[1] if len(call) > 1 and call[1] else {}
            assert (
                "session" not in call_kwargs
            ), "yf.download should not be called with session parameter"


def test_yf_download_normalizes_class_share_symbol():
    """Test that yf_download sends Yahoo's dash-form class-share symbol."""
    with patch("yfinance.download") as mock_download:
        columns = pd.MultiIndex.from_tuples(
            [
                ("BRK-A", "Open"),
                ("BRK-A", "High"),
                ("BRK-A", "Low"),
                ("BRK-A", "Close"),
                ("BRK-A", "Adj Close"),
            ]
        )
        idx = pd.to_datetime(["2023-01-03"])
        idx.name = "Date"
        mock_data = pd.DataFrame([[100, 110, 90, 105, 105]], columns=columns, index=idx)
        mock_download.return_value = mock_data

        yf_download("BRK.A", start_date="2023-01-01", end_date="2023-01-10")

        assert mock_download.call_args.kwargs["tickers"] == "BRK-A"


def test_yf_download_preserves_requested_symbol_output_for_multi_symbol():
    """Test that multi-symbol output keeps OpenBB's requested symbol format."""
    with patch("yfinance.download") as mock_download:
        fields = ["Open", "High", "Low", "Close", "Adj Close"]
        columns = pd.MultiIndex.from_product([["BRK-A", "AAPL"], fields])
        idx = pd.to_datetime(["2023-01-03"])
        idx.name = "Date"
        mock_data = pd.DataFrame(
            [[100, 110, 90, 105, 105, 200, 210, 190, 205, 205]],
            columns=columns,
            index=idx,
        )
        mock_download.return_value = mock_data

        data = yf_download("BRK.A,AAPL")

        assert mock_download.call_args.kwargs["tickers"] == "BRK-A,AAPL"
        assert set(data["symbol"]) == {"BRK.A", "AAPL"}
        assert "BRK-A" not in set(data["symbol"])


@pytest.mark.asyncio
async def test_equity_quote_fetcher_normalizes_class_share_ticker():
    """Test that quote requests use Yahoo's dash-form class-share symbol."""
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.get_info.return_value = {
            "symbol": "BRK-A",
            "longName": "Berkshire Hathaway Inc.",
            "quoteType": "EQUITY",
            "currentPrice": 100,
        }

        data = await YFinanceEquityQuoteFetcher.aextract_data(
            YFinanceEquityQuoteQueryParams(symbol="BRK.A"),
            credentials={},
        )

        mock_ticker.assert_called_once_with("BRK-A")
        assert data[0]["symbol"] == "BRK.A"
