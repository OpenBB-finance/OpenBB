### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from annotated_types import Ge
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_stocks(Container):
    """/stocks
    /ca
    calendar_dividend
    calendar_ipo
    /disc
    /dps
    /fa
    info
    load
    market_snapshots
    multiples
    nbbo
    news
    /options
    price_performance
    quote
    search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def ca(self):  # route = "/stocks/ca"
        from . import stocks_ca

        return stocks_ca.ROUTER_stocks_ca(command_runner=self._command_runner)

    @validate
    def calendar_dividend(
        self,
        start_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        provider: Union[Literal["fmp", "nasdaq"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Upcoming and Historical Dividend Calendar.

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp', 'nasdaq'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[CalendarDividend]]
                Serializable results.
            provider : Union[Literal['fmp', 'nasdaq'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CalendarDividend
        ----------------
        date : date
            The date of the data. (Ex-Dividend)
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[Union[str]]
            Name of the entity.
        record_date : Optional[Union[date]]
            The record date of ownership for eligibility.
        payment_date : Optional[Union[date]]
            The payment date of the dividend.
        declaration_date : Optional[Union[date]]
            Declaration date of the dividend.
        amount : Optional[Union[float]]
            Dividend amount, per-share.
        adjusted_amount : Optional[Union[float]]
            The adjusted-dividend amount. (provider: fmp)
        label : Optional[Union[str]]
            Ex-dividend date formatted for display. (provider: fmp)
        annualized_amount : Optional[Union[float]]
            The indicated annualized dividend amount. (provider: nasdaq)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.calendar_dividend()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/calendar_dividend",
            **inputs,
        )

    @validate
    def calendar_ipo(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, None, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ] = None,
        start_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        limit: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Union[Literal["intrinio", "nasdaq"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Upcoming and Historical IPO Calendar.

        Parameters
        ----------
        symbol : Union[str, None]
            Symbol to get data for.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        limit : Union[int, None]
            The number of data entries to return.
        provider : Union[Literal['intrinio', 'nasdaq'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        status : Optional[Union[Literal['upcoming', 'priced', 'withdrawn'], Literal['upcoming', 'priced', 'filed', 'withdrawn']]]
            Status of the IPO. [upcoming, priced, or withdrawn] (provider: intrinio); The status of the IPO. (provider: nasdaq)
        min_value : Optional[Union[int]]
            Return IPOs with an offer dollar amount greater than the given amount. (provider: intrinio)
        max_value : Optional[Union[int]]
            Return IPOs with an offer dollar amount less than the given amount. (provider: intrinio)
        is_spo : bool
            If True, returns data for secondary public offerings (SPOs). (provider: nasdaq)

        Returns
        -------
        OBBject
            results : Union[List[CalendarIpo]]
                Serializable results.
            provider : Union[Literal['intrinio', 'nasdaq'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CalendarIpo
        -----------
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data.
        ipo_date : Optional[Union[date]]
            The date of the IPO, when the stock first trades on a major exchange.
        status : Optional[Union[Literal['upcoming', 'priced', 'withdrawn']]]

                    The status of the IPO. Upcoming IPOs have not taken place yet but are expected to.
                    Priced IPOs have taken place.
                    Withdrawn IPOs were expected to take place, but were subsequently withdrawn and did not take place
                 (provider: intrinio)
        exchange : Optional[Union[str]]

                    The acronym of the stock exchange that the company is going to trade publicly on.
                    Typically NYSE or NASDAQ.
                 (provider: intrinio)
        offer_amount : Optional[Union[float]]
            The total dollar amount of shares offered in the IPO. Typically this is share price * share count (provider: intrinio); The dollar value of the shares offered. (provider: nasdaq)
        share_price : Optional[Union[float]]
            The price per share at which the IPO was offered. (provider: intrinio)
        share_price_lowest : Optional[Union[float]]

                    The expected lowest price per share at which the IPO will be offered.
                    Before an IPO is priced, companies typically provide a range of prices per share at which
                    they expect to offer the IPO (typically available for upcoming IPOs).
                 (provider: intrinio)
        share_price_highest : Optional[Union[float]]

                    The expected highest price per share at which the IPO will be offered.
                    Before an IPO is priced, companies typically provide a range of prices per share at which
                    they expect to offer the IPO (typically available for upcoming IPOs).
                 (provider: intrinio)
        share_count : Optional[Union[int]]
            The number of shares offered in the IPO. (provider: intrinio, nasdaq)
        share_count_lowest : Optional[Union[int]]

                    The expected lowest number of shares that will be offered in the IPO. Before an IPO is priced,
                    companies typically provide a range of shares that they expect to offer in the IPO
                    (typically available for upcoming IPOs).
                 (provider: intrinio)
        share_count_highest : Optional[Union[int]]

                    The expected highest number of shares that will be offered in the IPO. Before an IPO is priced,
                    companies typically provide a range of shares that they expect to offer in the IPO
                    (typically available for upcoming IPOs).
                 (provider: intrinio)
        announcement_url : Optional[Union[str]]
            The URL to the company's announcement of the IPO (provider: intrinio)
        sec_report_url : Optional[Union[str]]

                    The URL to the company's S-1, S-1/A, F-1, or F-1/A SEC filing,
                    which is required to be filed before an IPO takes place.
                 (provider: intrinio)
        open_price : Optional[Union[float]]
            The opening price at the beginning of the first trading day (only available for priced IPOs). (provider: intrinio)
        close_price : Optional[Union[float]]
            The closing price at the end of the first trading day (only available for priced IPOs). (provider: intrinio)
        volume : Optional[Union[int]]
            The volume at the end of the first trading day (only available for priced IPOs). (provider: intrinio)
        day_change : Optional[Union[float]]

                    The percentage change between the open price and the close price on the first trading day
                    (only available for priced IPOs).
                 (provider: intrinio)
        week_change : Optional[Union[float]]

                    The percentage change between the open price on the first trading day and the close price approximately
                    a week after the first trading day (only available for priced IPOs).
                 (provider: intrinio)
        month_change : Optional[Union[float]]

                    The percentage change between the open price on the first trading day and the close price approximately
                    a month after the first trading day (only available for priced IPOs).
                 (provider: intrinio)
        id : Optional[Union[str]]
            The Intrinio ID of the IPO. (provider: intrinio)
        company : Optional[Union[openbb_intrinio.utils.references.IntrinioCompany]]
            The company that is going public via the IPO. (provider: intrinio)
        security : Optional[Union[openbb_intrinio.utils.references.IntrinioSecurity]]
            The primary Security for the Company that is going public via the IPO (provider: intrinio)
        name : Optional[Union[str]]
            The name of the company. (provider: nasdaq)
        expected_price_date : Optional[Union[date]]
            The date the pricing is expected. (provider: nasdaq)
        filed_date : Optional[Union[date]]
            The date the IPO was filed. (provider: nasdaq)
        withdraw_date : Optional[Union[date]]
            The date the IPO was withdrawn. (provider: nasdaq)
        deal_status : Optional[Union[str]]
            The status of the deal. (provider: nasdaq)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.calendar_ipo(limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/calendar_ipo",
            **inputs,
        )

    @property
    def disc(self):  # route = "/stocks/disc"
        from . import stocks_disc

        return stocks_disc.ROUTER_stocks_disc(command_runner=self._command_runner)

    @property
    def dps(self):  # route = "/stocks/dps"
        from . import stocks_dps

        return stocks_dps.ROUTER_stocks_dps(command_runner=self._command_runner)

    @property
    def fa(self):  # route = "/stocks/fa"
        from . import stocks_fa

        return stocks_fa.ROUTER_stocks_fa(command_runner=self._command_runner)

    @validate
    def info(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Info. Get general price and performance metrics of a stock.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['cboe'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[StockInfo]]
                Serializable results.
            provider : Union[Literal['cboe'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockInfo
        ---------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name associated with the ticker symbol.
        price : Optional[Union[float]]
            Last transaction price.
        open : Optional[Union[float]]
            The open price of the symbol.
        high : Optional[Union[float]]
            The high price of the symbol.
        low : Optional[Union[float]]
            The low price of the symbol.
        close : Optional[Union[float]]
            The close price of the symbol.
        change : Optional[Union[float]]
            Change in price over the current trading period.
        change_percent : Optional[Union[float]]
            Percent change in price over the current trading period.
        prev_close : Optional[Union[float]]
            Previous closing price.
        type : Optional[Union[str]]
            Type of asset. (provider: cboe)
        exchange_id : Optional[Union[int]]
            The Exchange ID number. (provider: cboe)
        tick : Optional[Union[str]]
            Whether the last sale was an up or down tick. (provider: cboe)
        bid : Optional[Union[float]]
            Current bid price. (provider: cboe)
        bid_size : Optional[Union[float]]
            Bid lot size. (provider: cboe)
        ask : Optional[Union[float]]
            Current ask price. (provider: cboe)
        ask_size : Optional[Union[float]]
            Ask lot size. (provider: cboe)
        volume : Optional[Union[float]]
            Stock volume for the current trading day. (provider: cboe)
        iv30 : Optional[Union[float]]
            The 30-day implied volatility of the stock. (provider: cboe)
        iv30_change : Optional[Union[float]]
            Change in 30-day implied volatility of the stock. (provider: cboe)
        last_trade_timestamp : Optional[Union[datetime]]
            Last trade timestamp for the stock. (provider: cboe)
        iv30_annual_high : Optional[Union[float]]
            The 1-year high of implied volatility. (provider: cboe)
        hv30_annual_high : Optional[Union[float]]
            The 1-year high of realized volatility. (provider: cboe)
        iv30_annual_low : Optional[Union[float]]
            The 1-year low of implied volatility. (provider: cboe)
        hv30_annual_low : Optional[Union[float]]
            The 1-year low of realized volatility. (provider: cboe)
        iv60_annual_high : Optional[Union[float]]
            The 60-day high of implied volatility. (provider: cboe)
        hv60_annual_high : Optional[Union[float]]
            The 60-day high of realized volatility. (provider: cboe)
        iv60_annual_low : Optional[Union[float]]
            The 60-day low of implied volatility. (provider: cboe)
        hv60_annual_low : Optional[Union[float]]
            The 60-day low of realized volatility. (provider: cboe)
        iv90_annual_high : Optional[Union[float]]
            The 90-day high of implied volatility. (provider: cboe)
        hv90_annual_high : Optional[Union[float]]
            The 90-day high of realized volatility. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.info(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/info",
            **inputs,
        )

    @validate
    def load(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        interval: typing_extensions.Annotated[
            Union[str, None],
            OpenBBCustomParameter(description="Time interval of the data to return."),
        ] = "1d",
        start_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        chart: bool = False,
        provider: Union[
            Literal["alpha_vantage", "cboe", "fmp", "intrinio", "polygon", "yfinance"],
            None,
        ] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Historical price. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        interval : Union[str, None]
            Time interval of the data to return.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygo...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'alpha_vantage' if there is
            no default.
        adjusted : Optional[Union[bool]]
            Output time series is adjusted by historical split and dividend events. (provider: alpha_vantage, polygon); Adjust all OHLC data automatically. (provider: yfinance)
        extended_hours : Optional[Union[bool]]
            Extended trading hours during pre-market and after-hours.Only available for intraday data. (provider: alpha_vantage)
        month : Optional[Union[str]]
            Query a specific month in history (in YYYY-MM format). (provider: alpha_vantage)
        output_size : Optional[Union[Literal['compact', 'full']]]
            Compact returns only the latest 100 data points in the intraday time series; full returns trailing 30 days of the most recent intraday data if the month parameter is not specified, or the full intraday data for aspecific month in history if the month parameter is specified. (provider: alpha_vantage)
        limit : Optional[Union[typing_extensions.Annotated[int, Ge(ge=0)], int]]
            Number of days to look back (Only for interval 1d). (provider: fmp); The number of data entries to return. (provider: polygon)
        start_time : Optional[Union[datetime.time]]
            Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        end_time : Optional[Union[datetime.time]]
            Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        timezone : str
            Timezone of the data, in the IANA format (Continent/City). (provider: intrinio)
        source : Optional[Union[Literal['realtime', 'delayed', 'nasdaq_basic']]]
            The source of the data. (provider: intrinio)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        include : bool
            Include Dividends and Stock Splits in results. (provider: yfinance)
        back_adjust : bool
            Attempt to adjust all the data automatically. (provider: yfinance)
        ignore_tz : bool
            When combining from different timezones, ignore that part of datetime. (provider: yfinance)

        Returns
        -------
        OBBject
            results : Union[List[StockHistorical]]
                Serializable results.
            provider : Union[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockHistorical
        ---------------
        date : datetime
            The date of the data.
        open : float
            The open price of the symbol.
        high : float
            The high price of the symbol.
        low : float
            The low price of the symbol.
        close : float
            The close price of the symbol.
        volume : Union[float, int]
            The volume of the symbol.
        vwap : Optional[Union[typing_extensions.Annotated[float, Gt(gt=0)]]]
            Volume Weighted Average Price of the symbol.
        adj_close : Optional[Union[typing_extensions.Annotated[float, Gt(gt=0)], float]]
            The adjusted close price of the symbol. (provider: alpha_vantage, fmp); Adjusted closing price during the period. (provider: intrinio)
        dividend_amount : Optional[Union[typing_extensions.Annotated[float, Ge(ge=0)]]]
            Dividend amount paid for the corresponding date. (provider: alpha_vantage)
        split_coefficient : Optional[Union[typing_extensions.Annotated[float, Ge(ge=0)]]]
            Split coefficient for the corresponding date. (provider: alpha_vantage)
        calls_volume : Optional[Union[float]]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[Union[float]]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[Union[float]]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        label : Optional[Union[str]]
            Human readable format of the date. (provider: fmp)
        unadjusted_volume : Optional[Union[float]]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[Union[float]]
            Change in the price of the symbol from the previous day. (provider: fmp, intrinio)
        change_percent : Optional[Union[float]]
            Change % in the price of the symbol. (provider: fmp)
        change_over_time : Optional[Union[float]]
            Change % in the price of the symbol over a period of time. (provider: fmp)
        close_time : Optional[Union[datetime]]
            The timestamp that represents the end of the interval span. (provider: intrinio)
        interval : Optional[Union[str]]
            The data time frequency. (provider: intrinio)
        average : Optional[Union[float]]
            Average trade price of an individual stock during the interval. (provider: intrinio)
        intra_period : Optional[Union[bool]]
            If true, the stock price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period (provider: intrinio)
        adj_open : Optional[Union[float]]
            Adjusted open price during the period. (provider: intrinio)
        adj_high : Optional[Union[float]]
            Adjusted high price during the period. (provider: intrinio)
        adj_low : Optional[Union[float]]
            Adjusted low price during the period. (provider: intrinio)
        adj_volume : Optional[Union[float]]
            Adjusted volume during the period. (provider: intrinio)
        factor : Optional[Union[float]]
            factor by which to multiply stock prices before this date, in order to calculate historically-adjusted stock prices. (provider: intrinio)
        split_ratio : Optional[Union[float]]
            Ratio of the stock split, if a stock split occurred. (provider: intrinio)
        dividend : Optional[Union[float]]
            Dividend amount, if a dividend was paid. (provider: intrinio)
        percent_change : Optional[Union[float]]
            Percent change in the price of the symbol from the previous day. (provider: intrinio)
        fifty_two_week_high : Optional[Union[float]]
            52 week high price for the symbol. (provider: intrinio)
        fifty_two_week_low : Optional[Union[float]]
            52 week low price for the symbol. (provider: intrinio)
        transactions : Optional[Union[typing_extensions.Annotated[int, Gt(gt=0)]]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.load(symbol="AAPL", interval="1d")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "interval": interval,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._run(
            "/stocks/load",
            **inputs,
        )

    @validate
    def market_snapshots(
        self, provider: Union[Literal["fmp", "polygon"], None] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Get a current, complete, market snapshot.

        Parameters
        ----------
        provider : Union[Literal['fmp', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        market : Literal['AMEX', 'AMS', 'ASE', 'ASX', 'ATH', 'BME', 'BRU', 'BUD', 'BUE', 'CAI', 'CNQ', 'CPH', 'DFM', 'DOH', 'DUS', 'ETF', 'EURONEXT', 'HEL', 'HKSE', 'ICE', 'IOB', 'IST', 'JKT', 'JNB', 'JPX', 'KLS', 'KOE', 'KSC', 'KUW', 'LSE', 'MEX', 'MIL', 'NASDAQ', 'NEO', 'NSE', 'NYSE', 'NZE', 'OSL', 'OTC', 'PNK', 'PRA', 'RIS', 'SAO', 'SAU', 'SES', 'SET', 'SGO', 'SHH', 'SHZ', 'SIX', 'STO', 'TAI', 'TLV', 'TSX', 'TWO', 'VIE', 'WSE', 'XETRA']
            The market to fetch data for. (provider: fmp)

        Returns
        -------
        OBBject
            results : Union[List[MarketSnapshots]]
                Serializable results.
            provider : Union[Literal['fmp', 'polygon'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MarketSnapshots
        ---------------
        symbol : str
            Symbol representing the entity requested in the data.
        open : Optional[Union[float]]
            The open price of the symbol.
        high : Optional[Union[float]]
            The high price of the symbol.
        low : Optional[Union[float]]
            The low price of the symbol.
        close : Optional[Union[float]]
            The close price of the symbol.
        prev_close : Optional[Union[float]]
            The previous closing price of the stock.
        change : Optional[Union[float]]
            The change in price.
        change_percent : Optional[Union[float]]
            The change, as a percent.
        volume : Optional[Union[int]]
            The volume of the symbol.
        price : Optional[Union[float]]
            The last price of the stock. (provider: fmp)
        avg_volume : Optional[Union[int]]
            Average volume of the stock. (provider: fmp)
        ma50 : Optional[Union[float]]
            The 50-day moving average. (provider: fmp)
        ma200 : Optional[Union[float]]
            The 200-day moving average. (provider: fmp)
        year_high : Optional[Union[float]]
            The 52-week high. (provider: fmp)
        year_low : Optional[Union[float]]
            The 52-week low. (provider: fmp)
        market_cap : Optional[Union[float]]
            Market cap of the stock. (provider: fmp)
        shares_outstanding : Optional[Union[float]]
            Number of shares outstanding. (provider: fmp)
        eps : Optional[Union[float]]
            Earnings per share. (provider: fmp)
        pe : Optional[Union[float]]
            Price to earnings ratio. (provider: fmp)
        exchange : Optional[Union[str]]
            The exchange of the stock. (provider: fmp)
        timestamp : Optional[Union[int, float]]
            The timestamp of the data. (provider: fmp)
        earnings_announcement : Optional[Union[str]]
            The earnings announcement of the stock. (provider: fmp)
        name : Optional[Union[str]]
            The name associated with the stock symbol. (provider: fmp)
        vwap : Optional[float]
            The volume weighted average price of the stock on the current trading day. (provider: polygon)
        prev_open : Optional[float]
            The previous trading session opening price. (provider: polygon)
        prev_high : Optional[float]
            The previous trading session high price. (provider: polygon)
        prev_low : Optional[float]
            The previous trading session low price. (provider: polygon)
        prev_volume : Optional[float]
            The previous trading session volume. (provider: polygon)
        prev_vwap : Optional[float]
            The previous trading session VWAP. (provider: polygon)
        last_updated : Optional[Union[datetime]]
            The last time the data was updated. (provider: polygon)
        bid : Optional[Union[float]]
            The current bid price. (provider: polygon)
        bid_size : Optional[Union[int]]
            The current bid size. (provider: polygon)
        ask_size : Optional[Union[int]]
            The current ask size. (provider: polygon)
        ask : Optional[Union[float]]
            The current ask price. (provider: polygon)
        quote_timestamp : Optional[Union[datetime]]
            The timestamp of the last quote. (provider: polygon)
        last_trade_price : Optional[Union[float]]
            The last trade price. (provider: polygon)
        last_trade_size : Optional[Union[int]]
            The last trade size. (provider: polygon)
        last_trade_conditions : Optional[Union[List[int]]]
            The last trade condition codes. (provider: polygon)
        last_trade_exchange : Optional[Union[int]]
            The last trade exchange ID code. (provider: polygon)
        last_trade_timestamp : Optional[Union[datetime]]
            The last trade timestamp. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.market_snapshots()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/market_snapshots",
            **inputs,
        )

    @validate
    def multiples(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        chart: bool = False,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Multiples. Valuation multiples for a stock ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : Union[int, None]
            The number of data entries to return.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[StockMultiples]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockMultiples
        --------------
        revenue_per_share_ttm : Optional[Union[float]]
            Revenue per share calculated as trailing twelve months.
        net_income_per_share_ttm : Optional[Union[float]]
            Net income per share calculated as trailing twelve months.
        operating_cash_flow_per_share_ttm : Optional[Union[float]]
            Operating cash flow per share calculated as trailing twelve months.
        free_cash_flow_per_share_ttm : Optional[Union[float]]
            Free cash flow per share calculated as trailing twelve months.
        cash_per_share_ttm : Optional[Union[float]]
            Cash per share calculated as trailing twelve months.
        book_value_per_share_ttm : Optional[Union[float]]
            Book value per share calculated as trailing twelve months.
        tangible_book_value_per_share_ttm : Optional[Union[float]]
            Tangible book value per share calculated as trailing twelve months.
        shareholders_equity_per_share_ttm : Optional[Union[float]]
            Shareholders equity per share calculated as trailing twelve months.
        interest_debt_per_share_ttm : Optional[Union[float]]
            Interest debt per share calculated as trailing twelve months.
        market_cap_ttm : Optional[Union[float]]
            Market capitalization calculated as trailing twelve months.
        enterprise_value_ttm : Optional[Union[float]]
            Enterprise value calculated as trailing twelve months.
        pe_ratio_ttm : Optional[Union[float]]
            Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months.
        price_to_sales_ratio_ttm : Optional[Union[float]]
            Price-to-sales ratio calculated as trailing twelve months.
        pocf_ratio_ttm : Optional[Union[float]]
            Price-to-operating cash flow ratio calculated as trailing twelve months.
        pfcf_ratio_ttm : Optional[Union[float]]
            Price-to-free cash flow ratio calculated as trailing twelve months.
        pb_ratio_ttm : Optional[Union[float]]
            Price-to-book ratio calculated as trailing twelve months.
        ptb_ratio_ttm : Optional[Union[float]]
            Price-to-tangible book ratio calculated as trailing twelve months.
        ev_to_sales_ttm : Optional[Union[float]]
            Enterprise value-to-sales ratio calculated as trailing twelve months.
        enterprise_value_over_ebitda_ttm : Optional[Union[float]]
            Enterprise value-to-EBITDA ratio calculated as trailing twelve months.
        ev_to_operating_cash_flow_ttm : Optional[Union[float]]
            Enterprise value-to-operating cash flow ratio calculated as trailing twelve months.
        ev_to_free_cash_flow_ttm : Optional[Union[float]]
            Enterprise value-to-free cash flow ratio calculated as trailing twelve months.
        earnings_yield_ttm : Optional[Union[float]]
            Earnings yield calculated as trailing twelve months.
        free_cash_flow_yield_ttm : Optional[Union[float]]
            Free cash flow yield calculated as trailing twelve months.
        debt_to_equity_ttm : Optional[Union[float]]
            Debt-to-equity ratio calculated as trailing twelve months.
        debt_to_assets_ttm : Optional[Union[float]]
            Debt-to-assets ratio calculated as trailing twelve months.
        net_debt_to_ebitda_ttm : Optional[Union[float]]
            Net debt-to-EBITDA ratio calculated as trailing twelve months.
        current_ratio_ttm : Optional[Union[float]]
            Current ratio calculated as trailing twelve months.
        interest_coverage_ttm : Optional[Union[float]]
            Interest coverage calculated as trailing twelve months.
        income_quality_ttm : Optional[Union[float]]
            Income quality calculated as trailing twelve months.
        dividend_yield_ttm : Optional[Union[float]]
            Dividend yield calculated as trailing twelve months.
        dividend_yield_percentage_ttm : Optional[Union[float]]
            Dividend yield percentage calculated as trailing twelve months.
        dividend_to_market_cap_ttm : Optional[Union[float]]
            Dividend to market capitalization ratio calculated as trailing twelve months.
        dividend_per_share_ttm : Optional[Union[float]]
            Dividend per share calculated as trailing twelve months.
        payout_ratio_ttm : Optional[Union[float]]
            Payout ratio calculated as trailing twelve months.
        sales_general_and_administrative_to_revenue_ttm : Optional[Union[float]]
            Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months.
        research_and_development_to_revenue_ttm : Optional[Union[float]]
            Research and development expenses-to-revenue ratio calculated as trailing twelve months.
        intangibles_to_total_assets_ttm : Optional[Union[float]]
            Intangibles-to-total assets ratio calculated as trailing twelve months.
        capex_to_operating_cash_flow_ttm : Optional[Union[float]]
            Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months.
        capex_to_revenue_ttm : Optional[Union[float]]
            Capital expenditures-to-revenue ratio calculated as trailing twelve months.
        capex_to_depreciation_ttm : Optional[Union[float]]
            Capital expenditures-to-depreciation ratio calculated as trailing twelve months.
        stock_based_compensation_to_revenue_ttm : Optional[Union[float]]
            Stock-based compensation-to-revenue ratio calculated as trailing twelve months.
        graham_number_ttm : Optional[Union[float]]
            Graham number calculated as trailing twelve months.
        roic_ttm : Optional[Union[float]]
            Return on invested capital calculated as trailing twelve months.
        return_on_tangible_assets_ttm : Optional[Union[float]]
            Return on tangible assets calculated as trailing twelve months.
        graham_net_net_ttm : Optional[Union[float]]
            Graham net-net working capital calculated as trailing twelve months.
        working_capital_ttm : Optional[Union[float]]
            Working capital calculated as trailing twelve months.
        tangible_asset_value_ttm : Optional[Union[float]]
            Tangible asset value calculated as trailing twelve months.
        net_current_asset_value_ttm : Optional[Union[float]]
            Net current asset value calculated as trailing twelve months.
        invested_capital_ttm : Optional[Union[float]]
            Invested capital calculated as trailing twelve months.
        average_receivables_ttm : Optional[Union[float]]
            Average receivables calculated as trailing twelve months.
        average_payables_ttm : Optional[Union[float]]
            Average payables calculated as trailing twelve months.
        average_inventory_ttm : Optional[Union[float]]
            Average inventory calculated as trailing twelve months.
        days_sales_outstanding_ttm : Optional[Union[float]]
            Days sales outstanding calculated as trailing twelve months.
        days_payables_outstanding_ttm : Optional[Union[float]]
            Days payables outstanding calculated as trailing twelve months.
        days_of_inventory_on_hand_ttm : Optional[Union[float]]
            Days of inventory on hand calculated as trailing twelve months.
        receivables_turnover_ttm : Optional[Union[float]]
            Receivables turnover calculated as trailing twelve months.
        payables_turnover_ttm : Optional[Union[float]]
            Payables turnover calculated as trailing twelve months.
        inventory_turnover_ttm : Optional[Union[float]]
            Inventory turnover calculated as trailing twelve months.
        roe_ttm : Optional[Union[float]]
            Return on equity calculated as trailing twelve months.
        capex_per_share_ttm : Optional[Union[float]]
            Capital expenditures per share calculated as trailing twelve months.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.multiples(symbol="AAPL", limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._run(
            "/stocks/multiples",
            **inputs,
        )

    @validate
    def nbbo(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["polygon"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Quote. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'polygon' if there is
            no default.
        limit : int
            The number of data entries to return. Up to ten million records will be returned. Pagination occurs in groups of 50,000. Remaining limit values will always return 50,000 more records unless it is the last page. High volume tickers will require multiple max requests for a single day's NBBO records. Expect stocks, like SPY, to approach 1GB in size, per day, as a raw CSV. Splitting large requests into chunks is recommended for full-day requests of high-volume symbols. (provider: polygon)
        date : Optional[Union[datetime.date]]
            A specific date to get data for. Use bracketed the timestamp parameters to specify exact time ranges. (provider: polygon)
        timestamp_lt : Optional[Union[datetime.datetime, str]]

                    Query by datetime, less than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)
        timestamp_gt : Optional[Union[datetime.datetime, str]]

                    Query by datetime, greater than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)
        timestamp_lte : Optional[Union[datetime.datetime, str]]

                    Query by datetime, less than or equal to.
                    Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)
        timestamp_gte : Optional[Union[datetime.datetime, str]]

                    Query by datetime, greater than or equal to.
                    Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[StockNBBO]]
                Serializable results.
            provider : Union[Literal['polygon'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockNBBO
        ---------
        ask_exchange : str
            The exchange ID for the ask.
        ask : float
            The last ask price.
        ask_size : int

                The ask size. This represents the number of round lot orders at the given ask price.
                The normal round lot size is 100 shares.
                An ask size of 2 means there are 200 shares available to purchase at the given ask price.

        bid_size : int
            The bid size in round lots.
        bid : float
            The last bid price.
        bid_exchange : str
            The exchange ID for the bid.
        tape : Optional[Union[str]]
            The exchange tape. (provider: polygon)
        conditions : Optional[Union[str, List[int], List[str]]]
            A list of condition codes. (provider: polygon)
        indicators : Optional[Union[List]]
            A list of indicator codes. (provider: polygon)
        sequence_num : Optional[Union[int]]

                    The sequence number represents the sequence in which message events happened.
                    These are increasing and unique per ticker symbol, but will not always be sequential
                    (e.g., 1, 2, 6, 9, 10, 11)
                 (provider: polygon)
        participant_timestamp : Optional[Union[datetime]]

                    The nanosecond accuracy Participant/Exchange Unix Timestamp.
                    This is the timestamp of when the quote was actually generated at the exchange.
                 (provider: polygon)
        sip_timestamp : Optional[Union[datetime]]

                    The nanosecond accuracy SIP Unix Timestamp.
                    This is the timestamp of when the SIP received this quote from the exchange which produced it.
                 (provider: polygon)
        trf_timestamp : Optional[Union[datetime]]

                    The nanosecond accuracy TRF (Trade Reporting Facility) Unix Timestamp.
                    This is the timestamp of when the trade reporting facility received this quote.
                 (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.nbbo(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/nbbo",
            **inputs,
        )

    @validate
    def news(
        self,
        symbols: typing_extensions.Annotated[
            str,
            OpenBBCustomParameter(
                description=" Here it is a separated list of symbols."
            ),
        ],
        limit: typing_extensions.Annotated[
            Union[typing_extensions.Annotated[int, Ge(ge=0)], None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 20,
        chart: bool = False,
        provider: Union[
            Literal["benzinga", "fmp", "intrinio", "polygon", "ultima", "yfinance"],
            None,
        ] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Company News. Get news for one or more companies.

        Parameters
        ----------
        symbols : str
             Here it is a separated list of symbols.
        limit : Union[typing_extensions.Annotated[int, Ge(ge=0)], None]
            The number of data entries to return.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima',...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        date : Optional[Union[str]]
            Date of the news to retrieve. (provider: benzinga)
        start_date : Optional[Union[str]]
            Start date of the news to retrieve. (provider: benzinga)
        end_date : Optional[Union[str]]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Optional[Union[int]]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Optional[Union[int]]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Optional[Union[Literal['id', 'created', 'updated']]]
            Key to sort the news by. (provider: benzinga)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order to sort the news by. (provider: benzinga); Sort order of the articles. (provider: polygon)
        isin : Optional[Union[str]]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Optional[Union[str]]
            The CUSIP of the news to retrieve. (provider: benzinga)
        channels : Optional[Union[str]]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Optional[Union[str]]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Optional[Union[str]]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Optional[Union[str]]
            Content types of the news to retrieve. (provider: benzinga)
        page : Optional[Union[int]]
            Page number of the results. Use in combination with limit. (provider: fmp)
        published_utc : Optional[Union[str]]
            Date query to fetch articles. Supports operators <, <=, >, >= (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[CompanyNews]]
                Serializable results.
            provider : Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CompanyNews
        -----------
        date : datetime
            The date of the data. Here it is the date of the news.
        title : str
            Title of the news.
        image : Optional[Union[str]]
            Image URL of the news.
        text : Optional[Union[str]]
            Text/body of the news.
        url : str
            URL of the news.
        id : Optional[Union[str]]
            ID of the news. (provider: benzinga); Intrinio ID for the article. (provider: intrinio); Article ID. (provider: polygon)
        author : Optional[Union[str]]
            Author of the news. (provider: benzinga); Author of the article. (provider: polygon)
        teaser : Optional[Union[str]]
            Teaser of the news. (provider: benzinga)
        images : Optional[Union[List[Dict[str, str]], List[str], str]]
            Images associated with the news. (provider: benzinga); URL to the images of the news. (provider: fmp)
        channels : Optional[Union[str]]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[Union[str]]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[Union[str]]
            Tags associated with the news. (provider: benzinga)
        updated : Optional[Union[datetime]]
            Updated date of the news. (provider: benzinga)
        symbol : Optional[Union[str]]
            Ticker of the fetched news. (provider: fmp)
        site : Optional[Union[str]]
            Name of the news source. (provider: fmp)
        amp_url : Optional[Union[str]]
            AMP URL. (provider: polygon)
        image_url : Optional[Union[str]]
            Image URL. (provider: polygon)
        keywords : Optional[Union[List[str]]]
            Keywords in the article (provider: polygon)
        publisher : Optional[Union[openbb_polygon.models.company_news.PolygonPublisher, str]]
            Publisher of the article. (provider: polygon, ultima, yfinance)
        tickers : Optional[Union[List[str]]]
            Tickers covered in the article. (provider: polygon)
        ticker : Optional[Union[str]]
            Ticker associated with the news. (provider: ultima)
        risk_category : Optional[Union[str]]
            Risk category of the news. (provider: ultima)
        uuid : Optional[Union[str]]
            Unique identifier for the news article (provider: yfinance)
        type : Optional[Union[str]]
            Type of the news article (provider: yfinance)
        thumbnail : Optional[Union[List]]
            Thumbnail related data to the ticker news article. (provider: yfinance)
        related_tickers : Optional[Union[str]]
            Tickers related to the news article. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.news.company(symbols="AAPL,MSFT", limit=20)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbols": symbols,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._run(
            "/stocks/news",
            **inputs,
        )

    @property
    def options(self):  # route = "/stocks/options"
        from . import stocks_options

        return stocks_options.ROUTER_stocks_options(command_runner=self._command_runner)

    @validate
    def price_performance(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Price performance as a return, over different periods.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[PricePerformance]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        PricePerformance
        ----------------
        one_day : Optional[Union[float]]
            One-day return.
        wtd : Optional[Union[float]]
            Week to date return.
        one_week : Optional[Union[float]]
            One-week return.
        mtd : Optional[Union[float]]
            Month to date return.
        one_month : Optional[Union[float]]
            One-month return.
        qtd : Optional[Union[float]]
            Quarter to date return.
        three_month : Optional[Union[float]]
            Three-month return.
        six_month : Optional[Union[float]]
            Six-month return.
        ytd : Optional[Union[float]]
            Year to date return.
        one_year : Optional[Union[float]]
            One-year return.
        three_year : Optional[Union[float]]
            Three-year return.
        five_year : Optional[Union[float]]
            Five-year return.
        ten_year : Optional[Union[float]]
            Ten-year return.
        max : Optional[Union[float]]
            Return from the beginning of the time series.
        symbol : Optional[Union[str]]
            The ticker symbol. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.price_performance(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/price_performance",
            **inputs,
        )

    @validate
    def quote(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. In this case, the comma separated list of symbols."
            ),
        ],
        provider: Union[Literal["fmp", "intrinio"], None] = None,
        **kwargs
    ) -> OBBject[Union[List[Data], Data]]:
        """Stock Quote. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. In this case, the comma separated list of symbols.
        provider : Union[Literal['fmp', 'intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        source : Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip']
            Source of the data. (provider: intrinio)

        Returns
        -------
        OBBject
            results : Union[List[StockQuote], StockQuote]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockQuote
        ----------
        day_low : Optional[Union[float]]
            Lowest price of the stock in the current trading day.
        day_high : Optional[Union[float]]
            Highest price of the stock in the current trading day.
        date : Optional[Union[datetime]]
            The date of the data.
        symbol : Optional[Union[str]]
            Symbol of the company. (provider: fmp)
        name : Optional[Union[str]]
            Name of the company. (provider: fmp)
        price : Optional[Union[float]]
            Current trading price of the stock. (provider: fmp)
        changes_percentage : Optional[Union[float]]
            Change percentage of the stock price. (provider: fmp)
        change : Optional[Union[float]]
            Change in the stock price. (provider: fmp)
        year_high : Optional[Union[float]]
            Highest price of the stock in the last 52 weeks. (provider: fmp)
        year_low : Optional[Union[float]]
            Lowest price of the stock in the last 52 weeks. (provider: fmp)
        market_cap : Optional[Union[float]]
            Market cap of the company. (provider: fmp)
        price_avg50 : Optional[Union[float]]
            50 days average price of the stock. (provider: fmp)
        price_avg200 : Optional[int]
            200 days average price of the stock. (provider: fmp)
        volume : Optional[int]
            Volume of the stock in the current trading day. (provider: fmp)
        avg_volume : Optional[int]
            Average volume of the stock in the last 10 trading days. (provider: fmp)
        exchange : Optional[Union[str]]
            Exchange the stock is traded on. (provider: fmp)
        open : Optional[Union[float]]
            Opening price of the stock in the current trading day. (provider: fmp)
        previous_close : Optional[Union[float]]
            Previous closing price of the stock. (provider: fmp)
        eps : Optional[Union[float]]
            Earnings per share of the stock. (provider: fmp)
        pe : Optional[Union[float]]
            Price earnings ratio of the stock. (provider: fmp)
        earnings_announcement : Optional[Union[str]]
            Earnings announcement date of the stock. (provider: fmp)
        shares_outstanding : Optional[int]
            Number of shares outstanding of the stock. (provider: fmp)
        last_price : Optional[Union[float]]
            Price of the last trade. (provider: intrinio)
        last_time : Optional[Union[datetime]]
            Date and Time when the last trade occurred. (provider: intrinio)
        last_size : Optional[Union[int]]
            Size of the last trade. (provider: intrinio)
        bid_price : Optional[Union[float]]
            Price of the top bid order. (provider: intrinio)
        bid_size : Optional[Union[int]]
            Size of the top bid order. (provider: intrinio)
        ask_price : Optional[Union[float]]
            Price of the top ask order. (provider: intrinio)
        ask_size : Optional[Union[int]]
            Size of the top ask order. (provider: intrinio)
        open_price : Optional[Union[float]]
            Open price for the trading day. (provider: intrinio)
        close_price : Optional[Union[float]]
            Closing price for the trading day (IEX source only). (provider: intrinio)
        high_price : Optional[Union[float]]
            High Price for the trading day. (provider: intrinio)
        low_price : Optional[Union[float]]
            Low Price for the trading day. (provider: intrinio)
        exchange_volume : Optional[Union[int]]
            Number of shares exchanged during the trading day on the exchange. (provider: intrinio)
        market_volume : Optional[Union[int]]
            Number of shares exchanged during the trading day for the whole market. (provider: intrinio)
        updated_on : Optional[Union[datetime]]
            Date and Time when the data was last updated. (provider: intrinio)
        source : Optional[Union[str]]
            Source of the data. (provider: intrinio)
        listing_venue : Optional[Union[str]]
            Listing venue where the trade took place (SIP source only). (provider: intrinio)
        sales_conditions : Optional[Union[str]]
            Indicates any sales condition modifiers associated with the trade. (provider: intrinio)
        quote_conditions : Optional[Union[str]]
            Indicates any quote condition modifiers associated with the trade. (provider: intrinio)
        market_center_code : Optional[Union[str]]
            Market center character code. (provider: intrinio)
        is_darkpool : Optional[Union[bool]]
            Whether or not the current trade is from a darkpool. (provider: intrinio)
        messages : Optional[Union[List[str]]]
            Messages associated with the endpoint. (provider: intrinio)
        security : Optional[Union[Dict[str, Any]]]
            Security details related to the quote. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.quote(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/quote",
            **inputs,
        )

    @validate
    def search(
        self,
        query: typing_extensions.Annotated[
            str, OpenBBCustomParameter(description="Search query.")
        ] = "",
        is_symbol: typing_extensions.Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        provider: Union[Literal["cboe", "fmp", "sec"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Search. Search for a company or stock ticker.

        Parameters
        ----------
        query : str
            Search query.
        is_symbol : bool
            Whether to search by ticker symbol.
        provider : Union[Literal['cboe', 'fmp', 'sec'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        mktcap_min : Optional[Union[int]]
            Filter by market cap greater than this value. (provider: fmp)
        mktcap_max : Optional[Union[int]]
            Filter by market cap less than this value. (provider: fmp)
        price_min : Optional[Union[float]]
            Filter by price greater than this value. (provider: fmp)
        price_max : Optional[Union[float]]
            Filter by price less than this value. (provider: fmp)
        beta_min : Optional[Union[float]]
            Filter by a beta greater than this value. (provider: fmp)
        beta_max : Optional[Union[float]]
            Filter by a beta less than this value. (provider: fmp)
        volume_min : Optional[Union[int]]
            Filter by volume greater than this value. (provider: fmp)
        volume_max : Optional[Union[int]]
            Filter by volume less than this value. (provider: fmp)
        dividend_min : Optional[Union[float]]
            Filter by dividend amount greater than this value. (provider: fmp)
        dividend_max : Optional[Union[float]]
            Filter by dividend amount less than this value. (provider: fmp)
        is_etf : Optional[Union[bool]]
            If true, returns only ETFs. (provider: fmp)
        is_active : Optional[Union[bool]]
            If false, returns only inactive tickers. (provider: fmp)
        sector : Optional[Union[Literal['Consumer Cyclical', 'Energy', 'Technology', 'Industrials', 'Financial Services', 'Basic Materials', 'Communication Services', 'Consumer Defensive', 'Healthcare', 'Real Estate', 'Utilities', 'Industrial Goods', 'Financial', 'Services', 'Conglomerates']]]
            Filter by sector. (provider: fmp)
        industry : Optional[Union[str]]
            Filter by industry. (provider: fmp)
        country : Optional[Union[str]]
            Filter by country, as a two-letter country code. (provider: fmp)
        exchange : Optional[Union[Literal['amex', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra']]]
            Filter by exchange. (provider: fmp)
        limit : Optional[Union[int]]
            Limit the number of results to return. (provider: fmp)
        is_fund : bool
            Whether to direct the search to the list of mutual funds and ETFs. (provider: sec)
        use_cache : bool
            Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. (provider: sec)

        Returns
        -------
        OBBject
            results : Union[List[StockSearch]]
                Serializable results.
            provider : Union[Literal['cboe', 'fmp', 'sec'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockSearch
        -----------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the company.
        dpm_name : Optional[Union[str]]
            Name of the primary market maker. (provider: cboe)
        post_station : Optional[Union[str]]
            Post and station location on the CBOE trading floor. (provider: cboe)
        market_cap : Optional[Union[int]]
            The market cap of ticker. (provider: fmp)
        sector : Optional[Union[str]]
            The sector the ticker belongs to. (provider: fmp)
        industry : Optional[Union[str]]
            The industry ticker belongs to. (provider: fmp)
        beta : Optional[Union[float]]
            The beta of the ETF. (provider: fmp)
        price : Optional[Union[float]]
            The current price. (provider: fmp)
        last_annual_dividend : Optional[Union[float]]
            The last annual amount dividend paid. (provider: fmp)
        volume : Optional[Union[int]]
            The current trading volume. (provider: fmp)
        exchange : Optional[Union[str]]
            The exchange code the asset trades on. (provider: fmp)
        exchange_name : Optional[Union[str]]
            The full name of the primary exchange. (provider: fmp)
        country : Optional[Union[str]]
            The two-letter country abbreviation where the head office is located. (provider: fmp)
        is_etf : Optional[Union[Literal[True, False]]]
            Whether the ticker is an ETF. (provider: fmp)
        actively_trading : Optional[Union[Literal[True, False]]]
            Whether the ETF is actively trading. (provider: fmp)
        cik : Optional[Union[str]]
            Central Index Key (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
                "is_symbol": is_symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/search",
            **inputs,
        )
