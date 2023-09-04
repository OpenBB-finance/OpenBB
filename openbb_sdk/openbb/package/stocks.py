### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import pydantic
import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_stocks(Container):
    """/stocks
    /ca
    /dd
    /fa
    load
    multiples
    news
    quote
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def ca(self):  # route = "/stocks/ca"
        from . import stocks_ca

        return stocks_ca.CLASS_stocks_ca(command_runner=self._command_runner)

    @property
    def dd(self):  # route = "/stocks/dd"
        from . import stocks_dd

        return stocks_dd.CLASS_stocks_dd(command_runner=self._command_runner)

    @property
    def fa(self):  # route = "/stocks/fa"
        from . import stocks_fa

        return stocks_fa.CLASS_stocks_fa(command_runner=self._command_runner)

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
        provider: Union[Literal["fmp", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Load stock data for a specific ticker.

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
        provider : Union[Literal['fmp', 'polygon'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        timeseries : Union[pydantic.types.NonNegativeInt, NoneType]
            Number of days to look back. (provider: fmp)
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Interval of the data to fetch. (provider: fmp)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        multiplier : PositiveInt
            Multiplier of the timespan. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[StockHistorical]
                Serializable results.
            provider : Union[Literal['fmp', 'polygon'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockHistorical
        ---------------
        date : Union[datetime, date]
            The date of the data.
        open : Optional[PositiveFloat]
            The open price of the symbol.
        high : Optional[PositiveFloat]
            The high price of the symbol.
        low : Optional[PositiveFloat]
            The low price of the symbol.
        close : Optional[PositiveFloat]
            The close price of the symbol.
        volume : Optional[NonNegativeInt]
            The volume of the symbol.
        calls_volume : Optional[float]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[float]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[float]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        adj_close : Optional[float]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price of the symbol from the previous day. (provider: fmp)
        change_percent : Optional[float]
            Change \\% in the price of the symbol. (provider: fmp)
<<<<<<< HEAD
        vwap : Optional[float]
            Volume Weighted Average Price of the symbol. (provider: fmp)
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[float]
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            Change \% in the price of the symbol over a period of time. (provider: fmp)
=======
            Change \\% in the price of the symbol over a period of time. (provider: fmp)
>>>>>>> 5bc4b6c2e4 (Rename EOD to Historical in code and files (#5395))
=======
            Change \\% in the price of the symbol over a period of time. (provider: fmp)
>>>>>>> c9435cec4a (static)
=======
            Change \\% in the price of the symbol over a period of time. (provider: fmp)
>>>>>>> 026b9329553dd45edc1c0d36efd457cb9a8af77f
        close_time : Optional[datetime]
            The timestamp that represents the end of the interval span. (provider: intrinio)
        interval : Optional[str]
            The data time frequency. (provider: intrinio)
        average : Optional[float]
            Average trade price of an individual stock during the interval. (provider: intrinio)
        transactions : Optional[PositiveInt]
=======
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[float]
            Change \\% in the price of the symbol over a period of time. (provider: fmp)
        n : Optional[PositiveInt]
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
            Number of transactions for the symbol in the time period. (provider: polygon)
        """  # noqa: E501

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
            Capital expenditures per share calculated as trailing twelve months."""  # noqa: E501

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
<<<<<<< HEAD
        provider: Optional[
            Literal["benzinga", "fmp", "intrinio", "polygon", "yfinance"]
        ] = None,
=======
        provider: Union[Literal["benzinga", "fmp", "polygon"], None] = None,
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
        **kwargs
    ) -> OBBject[BaseModel]:
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
<<<<<<< HEAD
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'yfinance']]
=======
        provider : Union[Literal['benzinga', 'fmp', 'polygon'], NoneType]
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
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
<<<<<<< HEAD
        next_page : Optional[str]
            Token to get the next page of data from a previous API call. (provider: intrinio)
        all_pages : Optional[bool]
            Returns all pages of data from the API call at once. (provider: intrinio)
        ticker_lt : Optional[str]
=======
        ticker_lt : Union[str, NoneType]
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
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
<<<<<<< HEAD
            provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'yfinance']]
=======
            provider : Union[Literal['benzinga', 'fmp', 'polygon'], NoneType]
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
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
        id : Optional[str]
            Intrinio ID for the news article. (provider: intrinio)
        amp_url : Optional[str]
            AMP URL. (provider: polygon)
        author : Optional[str]
            Author of the article. (provider: polygon)
        image_url : Optional[str]
            Image URL. (provider: polygon)
        keywords : Optional[List[str]]
            Keywords in the article (provider: polygon)
        publisher : Union[PolygonPublisher, NoneType, str]
            Publisher of the article. (provider: polygon)
        tickers : Optional[List[str]]
            Tickers covered in the article. (provider: polygon)
        uuid : Optional[str]
            Unique identifier for the news article (provider: yfinance)
        type : Optional[str]
            Type of the news article (provider: yfinance)
        thumbnail : Optional[Mapping[str, Any]]
            Thumbnail related data to the ticker news article. (provider: yfinance)
        related_tickers : Optional[str]
            Tickers related to the news article. (provider: yfinance)"""  # noqa: E501

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

    @validate_arguments
    def quote(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        chart: bool = False,
=======
>>>>>>> c9435cec4a (static)
=======
>>>>>>> 026b9329553dd45edc1c0d36efd457cb9a8af77f
        provider: Optional[Literal["fmp", "intrinio"]] = None,
=======
        chart: bool = False,
        provider: Union[Literal["fmp"], None] = None,
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
        **kwargs
    ) -> OBBject[List]:
        """Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        chart : bool
            Whether to create a chart or not, by default False.
=======
>>>>>>> c9435cec4a (static)
=======
>>>>>>> 026b9329553dd45edc1c0d36efd457cb9a8af77f
        provider : Optional[Literal['fmp', 'intrinio']]
=======
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['fmp'], NoneType]
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        source : Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip']
            Source of the data. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[StockQuote]
                Serializable results.
<<<<<<< HEAD
            provider : Optional[Literal['fmp', 'intrinio']]
=======
            provider : Union[Literal['fmp'], NoneType]
>>>>>>> cd9a3dc9c839ee359d2e310df2c30695778ebee7
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockQuote
        ----------
        day_low : Optional[float]
            Lowest price of the stock in the current trading day.
        day_high : Optional[float]
            Highest price of the stock in the current trading day.
        date : Optional[datetime]
            Timestamp of the stock quote.
        symbol : Optional[str]
            Symbol of the company. (provider: fmp)
        name : Optional[str]
            Name of the company. (provider: fmp)
        price : Optional[float]
            Current trading price of the stock. (provider: fmp)
        changes_percentage : Optional[float]
            Change percentage of the stock price. (provider: fmp)
        change : Optional[float]
            Change in the stock price. (provider: fmp)
        year_high : Optional[float]
            Highest price of the stock in the last 52 weeks. (provider: fmp)
        year_low : Optional[float]
            Lowest price of the stock in the last 52 weeks. (provider: fmp)
        market_cap : Optional[float]
            Market cap of the company. (provider: fmp)
        price_avg50 : Optional[float]
            50 days average price of the stock. (provider: fmp)
        price_avg200 : Optional[float]
            200 days average price of the stock. (provider: fmp)
        volume : Optional[int]
            Volume of the stock in the current trading day. (provider: fmp)
        avg_volume : Optional[int]
            Average volume of the stock in the last 10 trading days. (provider: fmp)
        exchange : Optional[str]
            Exchange the stock is traded on. (provider: fmp)
        open : Optional[float]
            Opening price of the stock in the current trading day. (provider: fmp)
        previous_close : Optional[float]
            Previous closing price of the stock. (provider: fmp)
        eps : Optional[float]
            Earnings per share of the stock. (provider: fmp)
        pe : Optional[float]
            Price earnings ratio of the stock. (provider: fmp)
        earnings_announcement : Optional[str]
            Earnings announcement date of the stock. (provider: fmp)
        shares_outstanding : Optional[int]
            Number of shares outstanding of the stock. (provider: fmp)
        last_price : Optional[float]
            Price of the last trade. (provider: intrinio)
        last_time : Optional[datetime]
            Date and Time when the last trade occurred. (provider: intrinio)
        last_size : Optional[int]
            Size of the last trade. (provider: intrinio)
        bid_price : Optional[float]
            Price of the top bid order. (provider: intrinio)
        bid_size : Optional[int]
            Size of the top bid order. (provider: intrinio)
        ask_price : Optional[float]
            Price of the top ask order. (provider: intrinio)
        ask_size : Optional[int]
            Size of the top ask order. (provider: intrinio)
        open_price : Optional[float]
            Open price for the trading day. (provider: intrinio)
        close_price : Optional[float]
            Closing price for the trading day (IEX source only). (provider: intrinio)
        high_price : Optional[float]
            High Price for the trading day. (provider: intrinio)
        low_price : Optional[float]
            Low Price for the trading day. (provider: intrinio)
        exchange_volume : Optional[int]
            Number of shares exchanged during the trading day on the exchange. (provider: intrinio)
        market_volume : Optional[int]
            Number of shares exchanged during the trading day for the whole market. (provider: intrinio)
        updated_on : Optional[datetime]
            Date and Time when the data was last updated. (provider: intrinio)
        source : Optional[str]
            Source of the data. (provider: intrinio)
        listing_venue : Optional[str]
            Listing venue where the trade took place (SIP source only). (provider: intrinio)
        sales_conditions : Optional[str]
            Indicates any sales condition modifiers associated with the trade. (provider: intrinio)
        quote_conditions : Optional[str]
            Indicates any quote condition modifiers associated with the trade. (provider: intrinio)
        market_center_code : Optional[str]
            Market center character code. (provider: intrinio)
        is_darkpool : Optional[bool]
            Whether or not the current trade is from a darkpool. (provider: intrinio)"""  # noqa: E501

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
