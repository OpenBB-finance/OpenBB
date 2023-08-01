### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import Literal, Optional, Union

import pydantic
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
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
        symbol: str,
        start_date: Union[datetime.date, None, str] = None,
        end_date: Union[datetime.date, None, str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Load stock data for a specific ticker.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format.

        Returns
        -------
        CommandOutput
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
        open : PositiveFloat
            The open price of the symbol.
        high : PositiveFloat
            The high price of the symbol.
        low : PositiveFloat
            The low price of the symbol.
        close : PositiveFloat
            The close price of the symbol.
        volume : PositiveFloat
            The volume of the symbol.

        fmp
        ===

        Parameters
        ----------
        timeseries : Optional[NonNegativeInt]
            Number of days to look back.


        StockEOD
        --------
        date : datetime
            The date of the data.
        adjClose : float
            Adjusted Close Price of the symbol.
        unadjustedVolume : float
            Unadjusted volume of the symbol.
        change : float
            Change in the price of the symbol from the previous day.
        changePercent : float
            Change \\% in the price of the symbol.
        vwap : float
            Volume Weighted Average Price of the symbol.
        label : str
            Human readable format of the date.
        changeOverTime : float
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
        t : datetime
            The timestamp of the data.
        n : PositiveInt
            The number of transactions for the symbol in the time period.
        vw : PositiveFloat
            The volume weighted average price of the symbol."""
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
        symbols: str,
        page: int = 0,
        limit: Optional[pydantic.types.NonNegativeInt] = 15,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Get news for one or more stock tickers.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[benzinga, fmp, polygon]
            The provider to use for the query.
        symbols : ConstrainedStrValue

        page : int
            The page of the stock news to be retrieved.
        limit : Optional[NonNegativeInt]
            The number of results to return per page.

        Returns
        -------
        CommandOutput
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
        date : date
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
        image : List[BenzingaImage]
            The images associated with the news.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockNews
        ---------
        symbol : str
            None
        publishedDate : datetime
            None
        image : Optional[str]
            None
        site : str
            None

        polygon
        =======

        Parameters
        ----------
        ticker_lt : Optional[str]
            None
        ticker_lte : Optional[str]
            None
        ticker_gt : Optional[str]
            None
        ticker_gte : Optional[str]
            None
        published_utc : Optional[str]
            None
        published_utc_lt : Optional[str]
            None
        published_utc_lte : Optional[str]
            None
        published_utc_gt : Optional[str]
            None
        published_utc_gte : Optional[str]
            None
        order : Optional[Literal['asc', 'desc']]
            None
        sort : Optional[str]
            None


        StockNews
        ---------
        amp_url : Optional[str]
            None
        article_url : str
            None
        author : Optional[str]
            None
        description : Optional[str]
            None
        id : str
            None
        image_url : Optional[str]
            None
        keywords : Optional[List[str]]
            None
        published_utc : datetime
            None
        publisher : PolygonPublisher
            None
        tickers : List[str]
            None"""
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
        symbol: str,
        limit: Optional[int] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
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
            None

        Returns
        -------
        CommandOutput
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
            None
        net_income_per_share_ttm : Optional[float]
            None
        operating_cash_flow_per_share_ttm : Optional[float]
            None
        free_cash_flow_per_share_ttm : Optional[float]
            None
        cash_per_share_ttm : Optional[float]
            None
        book_value_per_share_ttm : Optional[float]
            None
        tangible_book_value_per_share_ttm : Optional[float]
            None
        shareholders_equity_per_share_ttm : Optional[float]
            None
        interest_debt_per_share_ttm : Optional[float]
            None
        market_cap_ttm : Optional[float]
            None
        enterprise_value_ttm : Optional[float]
            None
        pe_ratio_ttm : Optional[float]
            None
        price_to_sales_ratio_ttm : Optional[float]
            None
        pocf_ratio_ttm : Optional[float]
            None
        pfcf_ratio_ttm : Optional[float]
            None
        pb_ratio_ttm : Optional[float]
            None
        ptb_ratio_ttm : Optional[float]
            None
        ev_to_sales_ttm : Optional[float]
            None
        enterprise_value_over_ebitda_ttm : Optional[float]
            None
        ev_to_operating_cash_flow_ttm : Optional[float]
            None
        ev_to_free_cash_flow_ttm : Optional[float]
            None
        earnings_yield_ttm : Optional[float]
            None
        free_cash_flow_yield_ttm : Optional[float]
            None
        debt_to_equity_ttm : Optional[float]
            None
        debt_to_assets_ttm : Optional[float]
            None
        net_debt_to_ebitda_ttm : Optional[float]
            None
        current_ratio_ttm : Optional[float]
            None
        interest_coverage_ttm : Optional[float]
            None
        income_quality_ttm : Optional[float]
            None
        dividend_yield_ttm : Optional[float]
            None
        payout_ratio_ttm : Optional[float]
            None
        sales_general_and_administrative_to_revenue_ttm : Optional[float]
            None
        research_and_development_to_revenue_ttm : Optional[float]
            None
        intangibles_to_total_assets_ttm : Optional[float]
            None
        capex_to_operating_cash_flow_ttm : Optional[float]
            None
        capex_to_revenue_ttm : Optional[float]
            None
        capex_to_depreciation_ttm : Optional[float]
            None
        stock_based_compensation_to_revenue_ttm : Optional[float]
            None
        graham_number_ttm : Optional[float]
            None
        roic_ttm : Optional[float]
            None
        return_on_tangible_assets_ttm : Optional[float]
            None
        graham_net_net_ttm : Optional[float]
            None
        working_capital_ttm : Optional[float]
            None
        tangible_asset_value_ttm : Optional[float]
            None
        net_current_asset_value_ttm : Optional[float]
            None
        invested_capital_ttm : Optional[float]
            None
        average_receivables_ttm : Optional[float]
            None
        average_payables_ttm : Optional[float]
            None
        average_inventory_ttm : Optional[float]
            None
        days_sales_outstanding_ttm : Optional[float]
            None
        days_payables_outstanding_ttm : Optional[float]
            None
        days_of_inventory_on_hand_ttm : Optional[float]
            None
        receivables_turnover_ttm : Optional[float]
            None
        payables_turnover_ttm : Optional[float]
            None
        inventory_turnover_ttm : Optional[float]
            None
        roe_ttm : Optional[float]
            None
        capex_per_share_ttm : Optional[float]
            None

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockMultiples
        --------------
        revenuePerShareTTM : Optional[float]
            None
        netIncomePerShareTTM : Optional[float]
            None
        operatingCashFlowPerShareTTM : Optional[float]
            None
        freeCashFlowPerShareTTM : Optional[float]
            None
        cashPerShareTTM : Optional[float]
            None
        bookValuePerShareTTM : Optional[float]
            None
        tangibleBookValuePerShareTTM : Optional[float]
            None
        shareholdersEquityPerShareTTM : Optional[float]
            None
        interestDebtPerShareTTM : Optional[float]
            None
        marketCapTTM : Optional[float]
            None
        enterpriseValueTTM : Optional[float]
            None
        peRatioTTM : Optional[float]
            None
        priceToSalesRatioTTM : Optional[float]
            None
        pocfratioTTM : Optional[float]
            None
        pfcfRatioTTM : Optional[float]
            None
        pbRatioTTM : Optional[float]
            None
        ptbRatioTTM : Optional[float]
            None
        evToSalesTTM : Optional[float]
            None
        enterpriseValueOverEBITDATTM : Optional[float]
            None
        evToOperatingCashFlowTTM : Optional[float]
            None
        evToFreeCashFlowTTM : Optional[float]
            None
        earningsYieldTTM : Optional[float]
            None
        freeCashFlowYieldTTM : Optional[float]
            None
        debtToEquityTTM : Optional[float]
            None
        debtToAssetsTTM : Optional[float]
            None
        netDebtToEBITDATTM : Optional[float]
            None
        currentRatioTTM : Optional[float]
            None
        interestCoverageTTM : Optional[float]
            None
        incomeQualityTTM : Optional[float]
            None
        dividendYieldTTM : Optional[float]
            None
        payoutRatioTTM : Optional[float]
            None
        salesGeneralAndAdministrativeToRevenueTTM : Optional[float]
            None
        researchAndDevelopementToRevenueTTM : Optional[float]
            None
        intangiblesToTotalAssetsTTM : Optional[float]
            None
        capexToOperatingCashFlowTTM : Optional[float]
            None
        capexToRevenueTTM : Optional[float]
            None
        capexToDepreciationTTM : Optional[float]
            None
        stockBasedCompensationToRevenueTTM : Optional[float]
            None
        grahamNumberTTM : Optional[float]
            None
        roicTTM : Optional[float]
            None
        returnOnTangibleAssetsTTM : Optional[float]
            None
        grahamNetNetTTM : Optional[float]
            None
        workingCapitalTTM : Optional[float]
            None
        tangibleAssetValueTTM : Optional[float]
            None
        netCurrentAssetValueTTM : Optional[float]
            None
        investedCapitalTTM : Optional[float]
            None
        averageReceivablesTTM : Optional[float]
            None
        averagePayablesTTM : Optional[float]
            None
        averageInventoryTTM : Optional[float]
            None
        daysSalesOutstandingTTM : Optional[float]
            None
        daysPayablesOutstandingTTM : Optional[float]
            None
        daysOfInventoryOnHandTTM : Optional[float]
            None
        receivablesTurnoverTTM : Optional[float]
            None
        payablesTurnoverTTM : Optional[float]
            None
        inventoryTurnoverTTM : Optional[float]
            None
        roeTTM : Optional[float]
            None
        capexPerShareTTM : Optional[float]
            None"""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """View top of book for loaded ticker (US exchanges only)."""
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
    def quote(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """View the current price for a specific stock ticker."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/quote",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def search(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Search a specific stock ticker for analysis."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/search",
            **inputs,
        ).output

        return filter_output(o)
