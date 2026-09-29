"""Tests for openbb_cboe.utils.vix."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pandas import DataFrame, to_datetime

from openbb_cboe.utils import vix


def _quote_rows(symbols, prices, timestamps):
    """Build fake quote rows for the equity-quote fetcher."""
    return [
        type(
            "Row",
            (),
            {
                "model_dump": lambda self, s=s, p=p, t=t: {
                    "symbol": s,
                    "last_price": p,
                    "last_timestamp": t,
                }
            },
        )()
        for s, p, t in zip(symbols, prices, timestamps)
    ]


def _historical_rows(dates, symbols, closes):
    """Build fake historical rows for the equity-historical fetcher."""
    return [
        type(
            "Row",
            (),
            {
                "model_dump": lambda self, d=d, s=s, c=c: {
                    "date": d,
                    "symbol": s,
                    "close": c,
                }
            },
        )()
        for d, s, c in zip(dates, symbols, closes)
    ]


class TestFrontMonth:
    """Front-month roll on the third Wednesday."""

    def test_before_third_wednesday(self):
        """Dates on or before the third Wednesday keep the current month."""
        assert vix.get_front_month("2024-06-01") == 6

    def test_after_third_wednesday(self):
        """Dates after the third Wednesday roll to the next month."""
        assert vix.get_front_month("2024-06-27") == 7

    def test_december_rolls_to_january(self):
        """December rolls around to January, not month 13."""
        assert vix.get_front_month("2024-12-31") == 1

    def test_defaults_to_today(self):
        """Omitting the date uses the current session."""
        assert vix.get_front_month() in range(1, 13)


class TestSymbolMaps:
    """Relative-contract symbol and month maps."""

    def test_vx_symbols_rotate(self):
        """VX1 is the front-month symbol for the given date."""
        symbols = vix.get_vx_symbols("2024-06-01")

        assert symbols["VX1"] == "UZM"
        assert len(symbols) == 12

    def test_get_months_rotates(self):
        """VX1 maps to the front month and wraps around the year."""
        months = vix.get_months(6)

        assert months["VX1"] == 6
        assert months["VX12"] == 5


class TestCheckDate:
    """Weekend roll-back."""

    def test_weekday_unchanged(self):
        """A weekday is returned untouched."""
        wednesday = to_datetime("2024-06-26")

        assert vix.check_date(wednesday) == wednesday

    @pytest.mark.parametrize("day", ["2024-06-29", "2024-06-30"])
    def test_weekend_rolls_back_to_friday(self, day):
        """Saturday and Sunday roll back to the preceding Friday."""
        assert vix.check_date(to_datetime(day)).strftime("%Y-%m-%d") == "2024-06-28"


class TestGetVxCurrent:
    """Current VX curve construction."""

    def test_rejects_bad_type(self):
        """An unknown vx_type raises."""
        with pytest.raises(OpenBBError, match="vx_type"):
            asyncio.run(vix.get_vx_current(vx_type="bad"))

    def test_eod_curve(self):
        """EOD symbols are ordered by the relative front month."""
        symbols = list(vix.get_vx_symbols().values())[:9]
        rows = _quote_rows(symbols, list(range(10, 19)), list(range(9)))

        with patch(
            "openbb_cboe.models.equity_quote.CboeEquityQuoteFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_current(vx_type="eod"))

        assert df.columns.tolist() == ["expiration", "price"]
        assert len(df) == 9
        assert all("-" in e for e in df.expiration)

    def test_am_curve(self):
        """AM symbols use the TWLV series."""
        rows = _quote_rows(vix.VX_AM_SYMBOLS, list(range(10, 19)), list(range(9)))

        with patch(
            "openbb_cboe.models.equity_quote.CboeEquityQuoteFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_current(vx_type="am"))

        assert df.columns.tolist() == ["expiration", "price"]
        assert len(df) == 9


class TestGetVxByDate:
    """Historical VX curve construction."""

    def test_rejects_bad_type(self):
        """An unknown vx_type raises."""
        with pytest.raises(OpenBBError, match="vx_type"):
            asyncio.run(vix.get_vx_by_date(date="2024-06-27", vx_type="bad"))

    def test_single_past_date(self):
        """A single past date returns one curve, ordered by relative month."""
        symbols = list(vix.get_vx_symbols().values())
        dates = ["2024-06-26", "2024-06-27"]
        rows = _historical_rows(
            [d for d in dates for _ in symbols],
            symbols * len(dates),
            [12.0 + i for i in range(len(symbols) * len(dates))],
        )

        with patch(
            "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_by_date(date="2024-06-27"))

        assert set(df.columns) == {"date", "expiration", "symbol", "price"}
        assert df.date.unique().tolist() == ["2024-06-27"]
        assert df.symbol.tolist() == sorted(df.symbol.tolist())

    def test_multiple_dates(self):
        """Comma-separated dates return one curve per date."""
        symbols = list(vix.get_vx_symbols().values())
        dates = ["2024-06-26", "2024-06-27"]
        rows = _historical_rows(
            [d for d in dates for _ in symbols],
            symbols * len(dates),
            [12.0 + i for i in range(len(symbols) * len(dates))],
        )

        with patch(
            "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_by_date(date="2024-06-26,2024-06-27"))

        assert sorted(df.date.unique()) == dates

    def test_list_input(self):
        """A list of dates is accepted as well as a comma-separated string."""
        symbols = list(vix.get_vx_symbols().values())
        dates = ["2024-06-26", "2024-06-27"]
        rows = _historical_rows(
            [d for d in dates for _ in symbols],
            symbols * len(dates),
            [12.0 + i for i in range(len(symbols) * len(dates))],
        )

        with patch(
            "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_by_date(date=dates))

        assert sorted(df.date.unique()) == dates

    def test_am_type_drops_incomplete_rows(self):
        """AM curves drop dates with any missing leg."""
        dates = ["2024-06-26", "2024-06-27"]
        rows = _historical_rows(
            [d for d in dates for _ in vix.VX_AM_SYMBOLS],
            vix.VX_AM_SYMBOLS * len(dates),
            [12.0 + i for i in range(len(vix.VX_AM_SYMBOLS) * len(dates))],
        )

        with patch(
            "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_by_date(date=dates, vx_type="am"))

        assert df.symbol.str.startswith("VX").all()

    def test_today_returns_current_curve(self):
        """Requesting today short-circuits to the live curve."""
        today = vix.check_date(datetime.today()).strftime("%Y-%m-%d")
        current = DataFrame({"expiration": ["2024-07"], "price": [13.0]})

        with patch.object(vix, "get_vx_current", new=AsyncMock(return_value=current)):
            df = asyncio.run(vix.get_vx_by_date(date=today))

        assert df.date.tolist() == [today]

    def test_nearest_date_fallback(self):
        """A date before all available history snaps to the nearest session."""
        symbols = list(vix.get_vx_symbols().values())
        rows = _historical_rows(
            ["2024-06-27"] * len(symbols),
            symbols,
            [12.0 + i for i in range(len(symbols))],
        )

        with patch(
            "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
            new=AsyncMock(return_value=rows),
        ):
            df = asyncio.run(vix.get_vx_by_date(date="2024-06-20"))

        assert df.date.unique().tolist() == ["2024-06-27"]

    def test_empty_output_raises(self):
        """A curve with no priced legs raises EmptyDataError."""
        symbols = list(vix.get_vx_symbols().values())
        rows = _historical_rows(
            ["2024-06-27"] * len(symbols), symbols, [None] * len(symbols)
        )

        with (
            patch(
                "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
                new=AsyncMock(return_value=rows),
            ),
            pytest.raises(EmptyDataError),
        ):
            asyncio.run(vix.get_vx_by_date(date="2024-06-27"))


class TestGetVxByDateToday:
    """The live-session branch of the historical curve."""

    def test_range_ending_today_appends_current_curve(self):
        """A range ending today splices the live curve onto the history."""
        symbols = list(vix.get_vx_symbols().values())
        today = vix.check_date(datetime.today()).strftime("%Y-%m-%d")
        past = "2024-06-27"
        rows = _historical_rows(
            [past] * len(symbols), symbols, [12.0 + i for i in range(len(symbols))]
        )
        current = DataFrame(
            {
                "expiration": [f"2026-{m:02d}" for m in range(1, 10)],
                "price": [13.0 + i for i in range(9)],
            }
        )

        with (
            patch.object(vix, "get_vx_current", new=AsyncMock(return_value=current)),
            patch(
                "openbb_cboe.models.equity_historical.CboeEquityHistoricalFetcher.fetch_data",
                new=AsyncMock(return_value=rows),
            ),
        ):
            df = asyncio.run(vix.get_vx_by_date(date=f"{past},{today}"))

        assert today in df.date.unique().tolist()
        assert set(df.symbol.unique()) <= {f"VX{i}" for i in range(1, 13)}
