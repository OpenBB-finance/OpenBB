### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import pydantic
import typing_extensions
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs


class CLASS_stocks(Container):
    """/stocks
    /ca
    /dd
    /disc
    /dps
    /fa
    /gov
    info
    /ins
    load
    multiples
    news
    /options
    quote
    search
    tob
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def ca(self):  # route = "/stocks/ca"
        from openbb_core.app.static.package import stocks_ca

        return stocks_ca.CLASS_stocks_ca(command_runner=self._command_runner)

    @property
    def dd(self):  # route = "/stocks/dd"
        from openbb_core.app.static.package import stocks_dd

        return stocks_dd.CLASS_stocks_dd(command_runner=self._command_runner)

    @property
    def disc(self):  # route = "/stocks/disc"
        from openbb_core.app.static.package import stocks_disc

        return stocks_disc.CLASS_stocks_disc(command_runner=self._command_runner)

    @property
    def dps(self):  # route = "/stocks/dps"
        from openbb_core.app.static.package import stocks_dps

        return stocks_dps.CLASS_stocks_dps(command_runner=self._command_runner)

    @property
    def fa(self):  # route = "/stocks/fa"
        from openbb_core.app.static.package import stocks_fa

        return stocks_fa.CLASS_stocks_fa(command_runner=self._command_runner)

    @property
    def gov(self):  # route = "/stocks/gov"
        from openbb_core.app.static.package import stocks_gov

        return stocks_gov.CLASS_stocks_gov(command_runner=self._command_runner)

    @validate_arguments
    def info(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get general price and performance metrics of a stock.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['cboe'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[StockInfo]
                Serializable results.
            provider : Union[Literal['cboe'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockInfo
        ---------
        symbol : Optional[str]
            Symbol to get data for.
        name : Optional[str]
            Name associated with the ticker symbol.
        price : Optional[float]
            Last price of the stock.
        open : Optional[float]
            Opening price of the stock.
        high : Optional[float]
            High price of the current trading day.
        low : Optional[float]
            Low price of the current trading day.
        close : Optional[float]
            Closing price of the stock.
        change : Optional[float]
            Change in price over the current trading period.
        change_percent : Optional[float]
            % change in price over the current trading period.
        previous_close : Optional[float]
            Previous closing price of the stock.
        type : Optional[str]
            Type of asset. (provider: cboe)
        tick : Optional[str]
            Whether the last sale was an up or down tick. (provider: cboe)
        bid : Optional[float]
            Current bid price. (provider: cboe)
        bid_size : Optional[float]
            Bid lot size. (provider: cboe)
        ask : Optional[float]
            Current ask price. (provider: cboe)
        ask_size : Optional[float]
            Ask lot size. (provider: cboe)
        volume : Optional[float]
            Stock volume for the current trading day. (provider: cboe)
        iv_thirty : Optional[float]
            The 30-day implied volatility of the stock. (provider: cboe)
        iv_thirty_change : Optional[float]
            Change in 30-day implied volatility of the stock. (provider: cboe)
        last_trade_timestamp : Optional[datetime]
            Last trade timestamp for the stock. (provider: cboe)
        iv_thirty_one_year_high : Optional[float]
            The 1-year high of implied volatility. (provider: cboe)
        hv_thirty_one_year_high : Optional[float]
            The 1-year high of realized volatility. (provider: cboe)
        iv_thirty_one_year_low : Optional[float]
            The 1-year low of implied volatility. (provider: cboe)
        hv_thirty_one_year_low : Optional[float]
            The 1-year low of realized volatility. (provider: cboe)
        iv_sixty_one_year_high : Optional[float]
            The 60-day high of implied volatility. (provider: cboe)
        hv_sixty_one_year_high : Optional[float]
            The 60-day high of realized volatility. (provider: cboe)
        iv_sixty_one_year_low : Optional[float]
            The 60-day low of implied volatility. (provider: cboe)
        hv_sixty_one_year_low : Optional[float]
            The 60-day low of realized volatility. (provider: cboe)
        iv_ninety_one_year_high : Optional[float]
            The 90-day high of implied volatility. (provider: cboe)
        hv_ninety_one_year_high : Optional[float]
            The 90-day high of realized volatility. (provider: cboe)"""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/info",
            **inputs,
        )

    @property
    def ins(self):  # route = "/stocks/ins"
        from openbb_core.app.static.package import stocks_ins

        return stocks_ins.CLASS_stocks_ins(command_runner=self._command_runner)

    @validate_arguments
    def load(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
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
        provider: Union[Literal["cboe", "fmp", "polygon", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        r"""Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        start_date : Union[datetime.date, NoneType, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, NoneType, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['cboe', 'fmp', 'polygon', 'yfinance'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        timeseries : Union[pydantic.types.NonNegativeInt, NoneType]
            Number of days to look back. (provider: fmp)
        interval : Union[Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], NoneType]
            None
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : PositiveInt
            The number of data entries to return. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        multiplier : PositiveInt
            Multiplier of the timespan. (provider: polygon)
        period : Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], NoneType]
            Period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        adjust : bool
            Adjust all the data automatically. (provider: yfinance)
        back_adjust : bool
            Back-adjusted data to mimic true historical prices. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[StockEOD]
                Serializable results.
            provider : Union[Literal['cboe', 'fmp', 'polygon', 'yfinance'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockEOD
        --------
        date : Optional[datetime]
            The date of the data.
        open : Optional[PositiveFloat]
            The open price of the symbol.
        high : Optional[PositiveFloat]
            The high price of the symbol.
        low : Optional[PositiveFloat]
            The low price of the symbol.
        close : Optional[PositiveFloat]
            The close price of the symbol.
        volume : Optional[float]
            The volume of the symbol.
        vwap : Optional[PositiveFloat]
            Volume Weighted Average Price of the symbol.
        adj_close : Optional[float]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price of the symbol from the previous day. (provider: fmp)
        change_percent : Optional[float]
            Change \% in the price of the symbol. (provider: fmp)
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[float]
            Change \% in the price of the symbol over a period of time. (provider: fmp)
        n : Optional[PositiveInt]
            Number of transactions for the symbol in the time period. (provider: polygon)
        """

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/load",
            **inputs,
        )

    @validate_arguments
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
    ) -> OBBject[List]:
        """Get valuation multiples for a stock ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        limit : Union[int, NoneType]
            The number of data entries to return.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['fmp'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[StockMultiples]
                Serializable results.
            provider : Union[Literal['fmp'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockMultiples
        --------------
        revenue_per_share_ttm : Optional[float]
            Revenue per share calculated as trailing twelve months.
        net_income_per_share_ttm : Optional[float]
            Net income per share calculated as trailing twelve months.
        operating_cash_flow_per_share_ttm : Optional[float]
            Operating cash flow per share calculated as trailing twelve months.
        free_cash_flow_per_share_ttm : Optional[float]
            Free cash flow per share calculated as trailing twelve months.
        cash_per_share_ttm : Optional[float]
            Cash per share calculated as trailing twelve months.
        book_value_per_share_ttm : Optional[float]
            Book value per share calculated as trailing twelve months.
        tangible_book_value_per_share_ttm : Optional[float]
            Tangible book value per share calculated as trailing twelve months.
        shareholders_equity_per_share_ttm : Optional[float]
            Shareholders equity per share calculated as trailing twelve months.
        interest_debt_per_share_ttm : Optional[float]
            Interest debt per share calculated as trailing twelve months.
        market_cap_ttm : Optional[float]
            Market capitalization calculated as trailing twelve months.
        enterprise_value_ttm : Optional[float]
            Enterprise value calculated as trailing twelve months.
        pe_ratio_ttm : Optional[float]
            Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months.
        price_to_sales_ratio_ttm : Optional[float]
            Price-to-sales ratio calculated as trailing twelve months.
        pocf_ratio_ttm : Optional[float]
            Price-to-operating cash flow ratio calculated as trailing twelve months.
        pfcf_ratio_ttm : Optional[float]
            Price-to-free cash flow ratio calculated as trailing twelve months.
        pb_ratio_ttm : Optional[float]
            Price-to-book ratio calculated as trailing twelve months.
        ptb_ratio_ttm : Optional[float]
            Price-to-tangible book ratio calculated as trailing twelve months.
        ev_to_sales_ttm : Optional[float]
            Enterprise value-to-sales ratio calculated as trailing twelve months.
        enterprise_value_over_ebitda_ttm : Optional[float]
            Enterprise value-to-EBITDA ratio calculated as trailing twelve months.
        ev_to_operating_cash_flow_ttm : Optional[float]
            Enterprise value-to-operating cash flow ratio calculated as trailing twelve months.
        ev_to_free_cash_flow_ttm : Optional[float]
            Enterprise value-to-free cash flow ratio calculated as trailing twelve months.
        earnings_yield_ttm : Optional[float]
            Earnings yield calculated as trailing twelve months.
        free_cash_flow_yield_ttm : Optional[float]
            Free cash flow yield calculated as trailing twelve months.
        debt_to_equity_ttm : Optional[float]
            Debt-to-equity ratio calculated as trailing twelve months.
        debt_to_assets_ttm : Optional[float]
            Debt-to-assets ratio calculated as trailing twelve months.
        net_debt_to_ebitda_ttm : Optional[float]
            Net debt-to-EBITDA ratio calculated as trailing twelve months.
        current_ratio_ttm : Optional[float]
            Current ratio calculated as trailing twelve months.
        interest_coverage_ttm : Optional[float]
            Interest coverage calculated as trailing twelve months.
        income_quality_ttm : Optional[float]
            Income quality calculated as trailing twelve months.
        dividend_yield_ttm : Optional[float]
            Dividend yield calculated as trailing twelve months.
        dividend_yield_percentage_ttm : Optional[float]
            Dividend yield percentage calculated as trailing twelve months.
        dividend_to_market_cap_ttm : Optional[float]
            Dividend to market capitalization ratio calculated as trailing twelve months.
        dividend_per_share_ttm : Optional[float]
            Dividend per share calculated as trailing twelve months.
        payout_ratio_ttm : Optional[float]
            Payout ratio calculated as trailing twelve months.
        sales_general_and_administrative_to_revenue_ttm : Optional[float]
            Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months.
        research_and_development_to_revenue_ttm : Optional[float]
            Research and development expenses-to-revenue ratio calculated as trailing twelve months.
        intangibles_to_total_assets_ttm : Optional[float]
            Intangibles-to-total assets ratio calculated as trailing twelve months.
        capex_to_operating_cash_flow_ttm : Optional[float]
            Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months.
        capex_to_revenue_ttm : Optional[float]
            Capital expenditures-to-revenue ratio calculated as trailing twelve months.
        capex_to_depreciation_ttm : Optional[float]
            Capital expenditures-to-depreciation ratio calculated as trailing twelve months.
        stock_based_compensation_to_revenue_ttm : Optional[float]
            Stock-based compensation-to-revenue ratio calculated as trailing twelve months.
        graham_number_ttm : Optional[float]
            Graham number calculated as trailing twelve months.
        roic_ttm : Optional[float]
            Return on invested capital calculated as trailing twelve months.
        return_on_tangible_assets_ttm : Optional[float]
            Return on tangible assets calculated as trailing twelve months.
        graham_net_net_ttm : Optional[float]
            Graham net-net working capital calculated as trailing twelve months.
        working_capital_ttm : Optional[float]
            Working capital calculated as trailing twelve months.
        tangible_asset_value_ttm : Optional[float]
            Tangible asset value calculated as trailing twelve months.
        net_current_asset_value_ttm : Optional[float]
            Net current asset value calculated as trailing twelve months.
        invested_capital_ttm : Optional[float]
            Invested capital calculated as trailing twelve months.
        average_receivables_ttm : Optional[float]
            Average receivables calculated as trailing twelve months.
        average_payables_ttm : Optional[float]
            Average payables calculated as trailing twelve months.
        average_inventory_ttm : Optional[float]
            Average inventory calculated as trailing twelve months.
        days_sales_outstanding_ttm : Optional[float]
            Days sales outstanding calculated as trailing twelve months.
        days_payables_outstanding_ttm : Optional[float]
            Days payables outstanding calculated as trailing twelve months.
        days_of_inventory_on_hand_ttm : Optional[float]
            Days of inventory on hand calculated as trailing twelve months.
        receivables_turnover_ttm : Optional[float]
            Receivables turnover calculated as trailing twelve months.
        payables_turnover_ttm : Optional[float]
            Payables turnover calculated as trailing twelve months.
        inventory_turnover_ttm : Optional[float]
            Inventory turnover calculated as trailing twelve months.
        roe_ttm : Optional[float]
            Return on equity calculated as trailing twelve months.
        capex_per_share_ttm : Optional[float]
            Capital expenditures per share calculated as trailing twelve months."""

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

        return self._command_runner.run(
            "/stocks/multiples",
            **inputs,
        )

    @validate_arguments
    def news(
        self,
        symbols: typing_extensions.Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        page: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(
                description="Page of the stock news to be retrieved."
            ),
        ] = 0,
        limit: typing_extensions.Annotated[
            Union[pydantic.types.NonNegativeInt, None],
            OpenBBCustomParameter(description="Number of results to return per page."),
        ] = 15,
        chart: bool = False,
        provider: Union[Literal["benzinga", "fmp", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get news for one or more stock tickers.

        Parameters
        ----------
        symbols : str
            Symbol to get data for.
        page : int
            Page of the stock news to be retrieved.
        limit : Union[pydantic.types.NonNegativeInt, NoneType]
            Number of results to return per page.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['benzinga', 'fmp', 'polygon'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display_output : Literal['headline', 'summary', 'full', 'all']
            Type of data to return. (provider: benzinga)
        date : Union[datetime.datetime, NoneType]
            Date of the news to retrieve. (provider: benzinga)
        date_from : Union[datetime.datetime, NoneType]
            Start date of the news to retrieve. (provider: benzinga)
        date_to : Union[datetime.datetime, NoneType]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Union[int, NoneType]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Union[int, NoneType]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Union[Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type'], NoneType, str]
            None
        isin : Union[str, NoneType]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Union[str, NoneType]
            The CUSIP of the news to retrieve. (provider: benzinga)
        channels : Union[str, NoneType]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Union[str, NoneType]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Union[str, NoneType]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Union[str, NoneType]
            Content types of the news to retrieve. (provider: benzinga)
        ticker_lt : Union[str, NoneType]
            Less than, by default None (provider: polygon)
        ticker_lte : Union[str, NoneType]
            Less than or equal, by default None (provider: polygon)
        ticker_gt : Union[str, NoneType]
            Greater than, by default None (provider: polygon)
        ticker_gte : Union[str, NoneType]
            Greater than or equal, by default None (provider: polygon)
        published_utc : Union[str, NoneType]
            Published date of the query, by default None (provider: polygon)
        published_utc_lt : Union[str, NoneType]
            Less than, by default None (provider: polygon)
        published_utc_lte : Union[str, NoneType]
            Less than or equal, by default None (provider: polygon)
        published_utc_gt : Union[str, NoneType]
            Greater than, by default None (provider: polygon)
        published_utc_gte : Union[str, NoneType]
            Greater than or equal, by default None (provider: polygon)
        order : Union[Literal['asc', 'desc'], NoneType]
            Sort order of the query, by default None (provider: polygon)

        Returns
        -------
        OBBject
            results : List[StockNews]
                Serializable results.
            provider : Union[Literal['benzinga', 'fmp', 'polygon'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockNews
        ---------
        date : Optional[datetime]
            Published date of the news.
        title : Optional[str]
            Title of the news.
        text : Optional[str]
            Text/body of the news.
        url : Optional[str]
            URL of the news.
        images : Optional[List[BenzingaImage]]
            Images associated with the news. (provider: benzinga)
        channels : Optional[List[str]]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[List[str]]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[List[str]]
            Tags associated with the news. (provider: benzinga)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        symbol : Optional[str]
            Ticker of the fetched news. (provider: fmp)
        image : Optional[str]
            URL to the image of the news source. (provider: fmp)
        site : Optional[str]
            Name of the news source. (provider: fmp)
        amp_url : Optional[str]
            AMP URL. (provider: polygon)
        author : Optional[str]
            Author of the article. (provider: polygon)
        id : Optional[str]
            Article ID. (provider: polygon)
        image_url : Optional[str]
            Image URL. (provider: polygon)
        keywords : Optional[List[str]]
            Keywords in the article (provider: polygon)
        publisher : Optional[PolygonPublisher]
            Publisher of the article. (provider: polygon)
        tickers : Optional[List[str]]
            Tickers covered in the article. (provider: polygon)"""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbols": symbols,
                "page": page,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/news",
            **inputs,
        )

    @property
    def options(self):  # route = "/stocks/options"
        from openbb_core.app.static.package import stocks_options

        return stocks_options.CLASS_stocks_options(command_runner=self._command_runner)

    @validate_arguments
    def quote(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['fmp'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[StockQuote]
                Serializable results.
            provider : Union[Literal['fmp'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockQuote
        ----------
        symbol : Optional[str]
            Symbol of the company.
        name : Optional[str]
            Name of the company.
        price : Optional[float]
            Current trading price of the stock.
        changes_percentage : Optional[float]
            Change percentage of the stock price.
        change : Optional[float]
            Change of the stock price.
        day_low : Optional[float]
            Lowest price of the stock in the current trading day.
        day_high : Optional[float]
            Highest price of the stock in the current trading day.
        year_high : Optional[float]
            Highest price of the stock in the last 52 weeks.
        year_low : Optional[float]
            Lowest price of the stock in the last 52 weeks.
        market_cap : Optional[float]
            Market cap of the company.
        price_avg50 : Optional[float]
            50 days average price of the stock.
        price_avg200 : Optional[float]
            200 days average price of the stock.
        volume : Optional[int]
            Volume of the stock in the current trading day.
        avg_volume : Optional[int]
            Average volume of the stock in the last 10 trading days.
        exchange : Optional[str]
            Exchange the stock is traded on.
        open : Optional[float]
            Opening price of the stock in the current trading day.
        previous_close : Optional[float]
            Previous closing price of the stock.
        eps : Optional[float]
            Earnings per share of the stock.
        pe : Optional[float]
            Price earnings ratio of the stock.
        earnings_announcement : Optional[str]
            Earnings announcement date of the stock.
        shares_outstanding : Optional[int]
            Number of shares outstanding of the stock.
        date : Optional[datetime]
            Timestamp of the stock quote."""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/quote",
            **inputs,
        )

    @validate_arguments
    def search(
        self,
        query: typing_extensions.Annotated[
            str, OpenBBCustomParameter(description="Search query.")
        ] = "",
        ticker: typing_extensions.Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        chart: bool = False,
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Search for a company or stock ticker.

        Parameters
        ----------
        query : str
            Search query.
        ticker : bool
            Whether to search by ticker symbol.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['cboe'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[StockSearch]
                Serializable results.
            provider : Union[Literal['cboe'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockSearch
        -----------
        symbol : Optional[str]
            Symbol to get data for.
        name : Optional[str]
            Name of the company.
        dpm_name : Optional[str]
            Name of the primary market maker. (provider: cboe)
        post_station : Optional[str]
            Post and station location on the CBOE trading floor. (provider: cboe)"""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
                "ticker": ticker,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/search",
            **inputs,
        )

    @validate_arguments
    def tob(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """View top of book for loaded ticker (US exchanges only)."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/tob",
            **inputs,
        )
