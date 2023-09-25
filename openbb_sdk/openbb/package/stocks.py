### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import pydantic
import pydantic.main
import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import BaseModel, validate_arguments


class ROUTER_stocks(Container):
    """/stocks
    /ca
    /fa
    load
    multiples
    news
    /options
    quote
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def ca(self):  # route = "/stocks/ca"
        from . import stocks_ca

        return stocks_ca.ROUTER_stocks_ca(command_runner=self._command_runner)

    @property
    def fa(self):  # route = "/stocks/fa"
        from . import stocks_fa

        return stocks_fa.ROUTER_stocks_fa(command_runner=self._command_runner)

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
        provider: Union[Literal["fmp", "intrinio", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp', 'intrinio', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        timeseries : Union[pydantic.types.NonNegativeInt, None]
            Number of days to look back. (provider: fmp)
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Data granularity. (provider: fmp)
        timezone : Union[Literal['Africa/Algiers', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Monrovia', 'Africa/Nairobi', 'America/Argentina/Buenos_Aires', 'America/Bogota', 'America/Caracas', 'America/Chicago', 'America/Chihuahua', 'America/Denver', 'America/Godthab', 'America/Guatemala', 'America/Guyana', 'America/Halifax', 'America/Indiana/Indianapolis', 'America/Juneau', 'America/La_Paz', 'America/Lima', 'America/Lima', 'America/Los_Angeles', 'America/Mazatlan', 'America/Mexico_City', 'America/Mexico_City', 'America/Monterrey', 'America/Montevideo', 'America/New_York', 'America/Phoenix', 'America/Regina', 'America/Santiago', 'America/Sao_Paulo', 'America/St_Johns', 'America/Tijuana', 'Asia/Almaty', 'Asia/Baghdad', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Bangkok', 'Asia/Chongqing', 'Asia/Colombo', 'Asia/Dhaka', 'Asia/Dhaka', 'Asia/Hong_Kong', 'Asia/Irkutsk', 'Asia/Jakarta', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Karachi', 'Asia/Kathmandu', 'Asia/Kolkata', 'Asia/Kolkata', 'Asia/Kolkata', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuwait', 'Asia/Magadan', 'Asia/Muscat', 'Asia/Muscat', 'Asia/Novosibirsk', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tokyo', 'Asia/Tokyo', 'Asia/Tokyo', 'Asia/Ulaanbaatar', 'Asia/Urumqi', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Cape_Verde', 'Atlantic/South_Georgia', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Darwin', 'Australia/Hobart', 'Australia/Melbourne', 'Australia/Melbourne', 'Australia/Perth', 'Australia/Sydney', 'Etc/UTC', 'UTC', 'Europe/Amsterdam', 'Europe/Athens', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Helsinki', 'Europe/Istanbul', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/London', 'Europe/Madrid', 'Europe/Minsk', 'Europe/Moscow', 'Europe/Moscow', 'Europe/Paris', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/Sarajevo', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Auckland', 'Pacific/Chatham', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Majuro', 'Pacific/Midway', 'Pacific/Midway', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Port_Moresby', 'Pacific/Tongatapu'], None]
            Returns trading times in this timezone. (provider: intrinio)
        source : Union[Literal['realtime', 'delayed', 'nasdaq_basic'], None]
            The source of the data. (provider: intrinio)
        start_time : Union[datetime.time, None]
            Return intervals starting at the specified time on the `start_date` formatted as 'hh:mm:ss'. (provider: intrinio)
        end_time : Union[datetime.time, None]
            Return intervals stopping at the specified time on the `end_date` formatted as 'hh:mm:ss'. (provider: intrinio)
        interval_size : Union[Literal['1m', '5m', '10m', '15m', '30m', '60m', '1h'], None]
            The data time frequency. (provider: intrinio)
        multiplier : PositiveInt
            Multiplier of the timespan. (provider: polygon)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : PositiveInt
            The number of data entries to return. (provider: polygon)
        adjusted : bool
            Output time series is adjusted by historical split and dividend events. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[StockHistorical]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio', 'polygon'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        StockHistorical
        ---------------
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
        volume : Optional[NonNegativeInt]
            The volume of the symbol.
        vwap : Optional[PositiveFloat]
            Volume Weighted Average Price of the symbol.
        adj_close : Optional[float]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price of the symbol from the previous day. (provider: fmp, intrinio)
        change_percent : Optional[float]
            Change % in the price of the symbol. (provider: fmp)
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[float]
            Change % in the price of the symbol over a period of time. (provider: fmp)
        close_time : Optional[datetime]
            The timestamp that represents the end of the interval span. (provider: intrinio)
        interval : Optional[str]
            The data time frequency. (provider: intrinio)
        average : Optional[float]
            Average trade price of an individual stock during the interval. (provider: intrinio)
        transactions : Optional[PositiveInt]
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
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get valuation multiples for a stock ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        limit : Union[int, None]
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[StockMultiples]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        )

        return self._command_runner.run(
            "/stocks/multiples",
            **inputs,
        )

    @validate_arguments
    def news(
        self,
        symbols: typing_extensions.Annotated[
            str, OpenBBCustomParameter(description="Comma separated list of symbols.")
        ],
        limit: typing_extensions.Annotated[
            Union[pydantic.types.NonNegativeInt, None],
            OpenBBCustomParameter(description="Number of results to return per page."),
        ] = 20,
        provider: Union[Literal["benzinga", "fmp", "intrinio", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get news for one or more stock tickers.

        Parameters
        ----------
        symbols : str
            Comma separated list of symbols.
        limit : Union[pydantic.types.NonNegativeInt, None]
            Number of results to return per page.
        provider : Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        date : Union[str, None]
            Date of the news to retrieve. (provider: benzinga)
        start_date : Union[str, None]
            Start date of the news to retrieve. (provider: benzinga)
        end_date : Union[str, None]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Union[int, None]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Union[int, None]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Union[Literal['id', 'created', 'updated'], None]
            Key to sort the news by. (provider: benzinga)
        order : Union[Literal['asc', 'desc'], None]
            Order to sort the news by. (provider: benzinga); Sort order of the articles. (provider: polygon)
        isin : Union[str, None]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Union[str, None]
            The CUSIP of the news to retrieve. (provider: benzinga)
        channels : Union[str, None]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Union[str, None]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Union[str, None]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Union[str, None]
            Content types of the news to retrieve. (provider: benzinga)
        published_utc : Union[str, None]
            Date query to fetch articles. Supports operators <, <=, >, >= (provider: polygon)

        Returns
        -------
        OBBject
            results : List[StockNews]
                Serializable results.
            provider : Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon'], None]
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
        image : Optional[str]
            Image URL of the news.
        text : Optional[str]
            Text/body of the news.
        url : Optional[str]
            URL of the news.
        id : Optional[str]
            ID of the news. (provider: benzinga); Intrinio ID for the article. (provider: intrinio); Article ID. (provider: polygon)
        author : Optional[str]
            Author of the news. (provider: benzinga); Author of the article. (provider: polygon)
        updated : Optional[datetime]
            Updated date of the news. (provider: benzinga)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        channels : Optional[str]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[str]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[str]
            Tags associated with the news. (provider: benzinga)
        symbol : Optional[str]
            Ticker of the fetched news. (provider: fmp)
        site : Optional[str]
            Name of the news source. (provider: fmp)
        amp_url : Optional[str]
            AMP URL. (provider: polygon)
        image_url : Optional[str]
            Image URL. (provider: polygon)
        keywords : Optional[List[str]]
            Keywords in the article (provider: polygon)
        publisher : Optional[PolygonPublisher]
            Publisher of the article. (provider: polygon)
        tickers : Optional[List[str]]
            Tickers covered in the article. (provider: polygon)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbols": symbols,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/stocks/news",
            **inputs,
        )

    @property
    def options(self):  # route = "/stocks/options"
        from . import stocks_options

        return stocks_options.ROUTER_stocks_options(command_runner=self._command_runner)

    @validate_arguments
    def quote(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Comma separated list of symbols."),
        ] = None,
        provider: Union[Literal["fmp", "intrinio"], None] = None,
        **kwargs
    ) -> OBBject[BaseModel]:
        """Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Comma separated list of symbols.
        provider : Union[Literal['fmp', 'intrinio'], None]
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
            provider : Union[Literal['fmp', 'intrinio'], None]
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
            Whether or not the current trade is from a darkpool. (provider: intrinio)
        messages : Optional[List[str]]
            Messages associated with the endpoint. (provider: intrinio)
        security : Optional[Mapping[str, Any]]
            Security details related to the quote. (provider: intrinio)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/stocks/quote",
            **inputs,
        )
