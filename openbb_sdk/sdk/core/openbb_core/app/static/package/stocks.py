### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Annotated, List, Literal, Optional, Union

import pydantic
import pydantic.main
from pydantic import BaseModel, validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks(Container):
    @property
    def fa(self):  # route = "/stocks/fa"
        from openbb_core.app.static.package import stocks_fa

        return stocks_fa.CLASS_stocks_fa(
            command_runner_session=self._command_runner_session
        )

    @property
    def ca(self):  # route = "/stocks/ca"
        from openbb_core.app.static.package import stocks_ca

        return stocks_ca.CLASS_stocks_ca(
            command_runner_session=self._command_runner_session
        )

    @property
    def dd(self):  # route = "/stocks/dd"
        from openbb_core.app.static.package import stocks_dd

        return stocks_dd.CLASS_stocks_dd(
            command_runner_session=self._command_runner_session
        )

    @property
    def dps(self):  # route = "/stocks/dps"
        from openbb_core.app.static.package import stocks_dps

        return stocks_dps.CLASS_stocks_dps(
            command_runner_session=self._command_runner_session
        )

    @property
    def disc(self):  # route = "/stocks/disc"
        from openbb_core.app.static.package import stocks_disc

        return stocks_disc.CLASS_stocks_disc(
            command_runner_session=self._command_runner_session
        )

    @property
    def gov(self):  # route = "/stocks/gov"
        from openbb_core.app.static.package import stocks_gov

        return stocks_gov.CLASS_stocks_gov(
            command_runner_session=self._command_runner_session
        )

    @property
    def ins(self):  # route = "/stocks/ins"
        from openbb_core.app.static.package import stocks_ins

        return stocks_ins.CLASS_stocks_ins(
            command_runner_session=self._command_runner_session
        )

    @property
    def options(self):  # route = "/stocks/options"
        from openbb_core.app.static.package import stocks_options

        return stocks_options.CLASS_stocks_options(
            command_runner_session=self._command_runner_session
        )

    @filter_call
    @validate_arguments
    def load(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        chart: bool = False,
        provider: Optional[Literal["cboe", "fmp", "polygon", "yfinance"]] = None,
        **kwargs,
    ) -> Obbject[BaseModel]:
        """Load stock data for a specific ticker.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[cboe, fmp, polygon, yfinance]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockEOD
        --------
        date : datetime
            The date of the data.
        open : PositiveFloat
            The open price of the symbol.
        high : PositiveFloat
            The high price of the symbol.
        low : PositiveFloat
            The low price of the symbol.
        close : PositiveFloat
            The close price of the symbol.
        volume : float
            The volume of the symbol.
        vwap : Optional[PositiveFloat]
            Volume Weighted Average Price of the symbol.

        cboe
        ====

        Parameters
        ----------
        All fields are standardized.


        StockEOD
        --------
        All fields are standardized.

        fmp
        ===

        Parameters
        ----------
        timeseries : Optional[NonNegativeInt]
            Number of days to look back.
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Interval of the data to fetch.


        StockEOD
        --------
        adjClose : Optional[float]
            Adjusted Close Price of the symbol.
        unadjustedVolume : Optional[float]
            Unadjusted volume of the symbol.
        change : Optional[float]
            Change in the price of the symbol from the previous day.
        changePercent : Optional[float]
            Change \\% in the price of the symbol.
        label : Optional[str]
            Human readable format of the date.
        changeOverTime : Optional[float]
            Change \\% in the price of the symbol over a period of time.

        polygon
        =======

        Parameters
        ----------
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            The timespan of the data.
        sort : Literal['asc', 'desc']
            Sort order of the data.
        limit : PositiveInt
            The number of data entries to return.
        adjusted : bool
            Whether the data is adjusted.
        multiplier : PositiveInt
            The multiplier of the timespan.


        StockEOD
        --------
        n : Optional[PositiveInt]
            The number of transactions for the symbol in the time period.

        yfinance
        ========

        Parameters
        ----------
        interval : Optional[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]
            Data granularity.
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
            Period of the data to return (quarterly or annually).


        StockEOD
        --------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/load",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def news(
        self,
        symbols: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        page: Annotated[
            int,
            OpenBBCustomParameter(
                description="The page of the stock news to be retrieved."
            ),
        ] = 0,
        limit: Annotated[
            Optional[pydantic.types.NonNegativeInt],
            OpenBBCustomParameter(
                description="The number of results to return per page."
            ),
        ] = 15,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon"]] = None,
        **kwargs,
    ) -> Obbject[List]:
        """Get news for one or more stock tickers.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[benzinga, fmp, polygon]
            The provider to use for the query.
        symbols : ConstrainedStrValue
            Symbol to get data for.
        page : int
            The page of the stock news to be retrieved.
        limit : Optional[NonNegativeInt]
            The number of results to return per page.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockNews
        ---------
        date : datetime
            The published date of the news.
        title : str
            The title of the news.
        text : Optional[str]
            The text/body of the news.
        url : str
            The URL of the news.

        benzinga
        ========

        Parameters
        ----------
        displayOutput : Literal['headline', 'summary', 'full', 'all']
            The type of data to return.
        date : Optional[datetime]
            The date of the news to retrieve.
        dateFrom : Optional[datetime]
            The start date of the news to retrieve.
        dateTo : Optional[datetime]
            The end date of the news to retrieve.
        updatedSince : Optional[int]
            The number of seconds since the news was updated.
        publishedSince : Optional[int]
            The number of seconds since the news was published.
        sort : Optional[Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type']]
            The order in which to sort the news. Options are: published_at, updated_at, title, author, channel, ticker, topic, content_type.
        isin : Optional[str]
            The ISIN of the news to retrieve.
        cusip : Optional[str]
            The CUSIP of the news to retrieve.
        channels : Optional[str]
            The channels of the news to retrieve.
        topics : Optional[str]
            The topics of the news to retrieve.
        authors : Optional[str]
            The authors of the news to retrieve.
        content_types : Optional[str]
            The content types of the news to retrieve.


        StockNews
        ---------
        images : List[BenzingaImage]
            The images associated with the news.
        channels : Optional[List[str]]
            The channels associated with the news.
        stocks : Optional[List[str]]
            The stocks associated with the news.
        tags : Optional[List[str]]
            The tags associated with the news.
        teaser : Optional[str]
            The teaser of the news.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockNews
        ---------
        symbol : str
            Ticker of the fetched news.
        image : Optional[str]
            URL to the image of the news source.
        site : str
            Name of the news source.

        polygon
        =======

        Parameters
        ----------
        ticker_lt : Optional[str]
            Less than, by default None
        ticker_lte : Optional[str]
            Less than or equal, by default None
        ticker_gt : Optional[str]
            Greater than, by default None
        ticker_gte : Optional[str]
            Greater than or equal, by default None
        published_utc : Optional[str]
            The published date of the query, by default None
        published_utc_lt : Optional[str]
            Less than, by default None
        published_utc_lte : Optional[str]
            Less than or equal, by default None
        published_utc_gt : Optional[str]
            Greater than, by default None
        published_utc_gte : Optional[str]
            Greater than or equal, by default None
        order : Optional[Literal['asc', 'desc']]
            The sort order of the query, by default None
        sort : Optional[str]
            The sort of the query, by default None


        StockNews
        ---------
        amp_url : Optional[str]
            AMP URL.
        author : Optional[str]
            Author of the article.
        id : str
            Article ID.
        image_url : Optional[str]
            Image URL.
        keywords : Optional[List[str]]
            Keywords in the article
        publisher : PolygonPublisher
            Publisher of the article.
        tickers : List[str]
            Tickers covered in the article."""  # noqa: E501
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

        o = self._command_runner_session.run(
            "/stocks/news",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def multiples(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs,
    ) -> Obbject[List]:
        """Get valuation multiples for a stock ticker.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        limit : Optional[int]
            The number of data entries to return.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


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
            Capital expenditures per share calculated as trailing twelve months.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockMultiples
        --------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/multiples",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def tob(
        self, chart: bool = False
    ) -> Obbject[openbb_core.app.model.results.empty.Empty]:
        """View top of book for loaded ticker (US exchanges only)."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/tob",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def search(
        self,
        query: Annotated[
            str, OpenBBCustomParameter(description="The search query.")
        ] = "",
        ticker: Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        chart: bool = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs,
    ) -> Obbject[BaseModel]:
        """Search for a company or stock ticker.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[cboe]
            The provider to use for the query.
        query : str
            The search query.
        ticker : bool
            Whether to search by ticker symbol.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockSearch
        -----------
        symbol : str
            The ticker symbol of the company.
        name : str
            The name of the company.

        cboe
        ====

        Parameters
        ----------
        All fields are standardized.


        StockSearch
        -----------
        dpmName : Optional[str]
            The name of the primary market maker.
        postStation : Optional[str]
            The post and station location on the CBOE trading floor."""  # noqa: E501
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

        o = self._command_runner_session.run(
            "/stocks/search",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def quote(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs,
    ) -> Obbject[List]:
        """Load stock data for a specific ticker.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockQuote
        ----------
        symbol : str
            Symbol of the company.
        name : Optional[str]
            The name of the company.
        price : Optional[float]
            The current trading price of the stock.
        changes_percentage : Optional[float]
            The change percentage of the stock price.
        change : Optional[float]
            The change of the stock price.
        day_low : Optional[float]
            The lowest price of the stock in the current trading day.
        day_high : Optional[float]
            The highest price of the stock in the current trading day.
        year_high : Optional[float]
            The highest price of the stock in the last 52 weeks.
        year_low : Optional[float]
            The lowest price of the stock in the last 52 weeks.
        market_cap : Optional[float]
            The market cap of the company.
        price_avg50 : Optional[float]
            The 50 days average price of the stock.
        price_avg200 : Optional[float]
            The 200 days average price of the stock.
        volume : Optional[int]
            The volume of the stock in the current trading day.
        avg_volume : Optional[int]
            The average volume of the stock in the last 10 trading days.
        exchange : Optional[str]
            The exchange the stock is traded on.
        open : Optional[float]
            The opening price of the stock in the current trading day.
        previous_close : Optional[float]
            The previous closing price of the stock.
        eps : Optional[float]
            The earnings per share of the stock.
        pe : Optional[float]
            The price earnings ratio of the stock.
        earnings_announcement : Optional[str]
            The earnings announcement date of the stock.
        shares_outstanding : Optional[int]
            The number of shares outstanding of the stock.
        date : Optional[datetime]
            The timestamp of the stock quote.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockQuote
        ----------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/quote",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def info(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        chart: bool = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs,
    ) -> Obbject[BaseModel]:
        """Get general price and performance metrics of a stock.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[cboe]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockInfo
        ---------
        symbol : str
            The ticker symbol.
        name : str
            The name associated with the ticker symbol.
        price : float
            The last price of the stock.
        open : Optional[float]
            The opening price of the stock.
        high : Optional[float]
            The high price of the current trading day.
        low : Optional[float]
            The low price of the current trading day.
        close : Optional[float]
            The closing price of the stock.
        change : Optional[float]
            The change in price over the current trading period.
        change_percent : Optional[float]
            The % change in price over the current trading period.
        previous_close : Optional[float]
            The previous closing price of the stock.

        cboe
        ====

        Parameters
        ----------
        All fields are standardized.


        StockInfo
        ---------
        type : Optional[str]
            The type of asset.
        tick : Optional[str]
            Whether the last sale was an up or down tick.
        bid : Optional[float]
            The current bid price.
        bid_size : Optional[float]
            The bid lot size.
        ask : Optional[float]
            The current ask price.
        ask_size : Optional[float]
            The ask lot size.
        volume : Optional[float]
            The stock volume for the current trading day.
        iv_thirty : Optional[float]
            The 30-day implied volatility of the stock.
        iv_thirty_change : Optional[float]
            The change in 30-day implied volatility of the stock.
        last_trade_timestamp : Optional[datetime]
            The last trade timestamp for the stock.
        iv_thirty_one_year_high : Optional[float]
            The 1-year high of implied volatility.
        hv_thirty_one_year_high : Optional[float]
            The 1-year high of realized volatility.
        iv_thirty_one_year_low : Optional[float]
            The 1-year low of implied volatility.
        hv_thirty_one_year_low : Optional[float]
            The 1-year low of realized volatility.
        iv_sixty_one_year_high : Optional[float]
            The 60-day high of implied volatility.
        hv_sixty_one_year_high : Optional[float]
            The 60-day high of realized volatility.
        iv_sixty_one_year_low : Optional[float]
            The 60-day low of implied volatility.
        hv_sixty_one_year_low : Optional[float]
            The 60-day low of realized volatility.
        iv_ninety_one_year_high : Optional[float]
            The 90-day high of implied volatility.
        hv_ninety_one_year_high : Optional[float]
            The 90-day high of realized volatility."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/info",
            **inputs,
        ).output

        return filter_output(o)
