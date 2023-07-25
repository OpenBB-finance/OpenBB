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

        Available providers: fmp, polygon

        Standard
        ========
        Parameter
        ---------
        symbol : str
            The symbol of the company.
        start_date : Optional[date]
            The start date of the stock data from which to retrieve the data.
        end_date : Optional[date]
            The end date of the stock data up to which to retrieve the data.


        Returns
        -------
        date : datetime
            The date of the stock.
        open : PositiveFloat
            The open price of the stock.
        high : PositiveFloat
            The high price of the stock.
        low : PositiveFloat
            The low price of the stock.
        close : PositiveFloat
            The close price of the stock.
        adj_close : Optional[PositiveFloat]
            The adjusted close price of the stock.
        volume : PositiveFloat
            The volume of the stock.

        fmp
        ===

        Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price

        Parameter
        ---------
        timeseries : Optional[int]
            The number of days to look back.
        series_type : Optional[Literal["line"]]
            The type of the series. Only "line" is supported.


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/stocks/getting-started

        Parameters
        ----------
        timespan : Timespan, optional
            The timespan of the query, by default Timespan.day
        sort : Literal["asc", "desc"], optional
            The sort order of the query, by default "desc"
        limit : PositiveInt, optional
            The limit of the query, by default 49999
        adjusted : bool, optional
            Whether the query is adjusted, by default True
        multiplier : PositiveInt, optional
            The multiplier of the query, by default 1


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: benzinga, fmp, polygon

        Standard
        ========


        Returns
        -------
        date : date
            The published date of the news.
        title : str
            The title of the news.
        image : Optional[str]
            The image URL of the news.
        text : str
            The text/body of the news.
        url : str
            The URL of the news.

        benzinga
        ========

        Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html


        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/stock-news-api/


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/stocks/get_v2_reference_news

        Parameters
        ----------
        symbol : str
            The symbol of the stocks to fetch.
        ticker_lt : str, optional
            Less than, by default None
        ticker_lte : str, optional
            Less than or equal, by default None
        ticker_gt : str, optional
            Greater than, by default None
        ticker_gte : str, optional
            Greater than or equal, by default None
        published_utc : str, optional
            The published date of the query, by default None
        published_utc_lt : str, optional
            Less than, by default None
        published_utc_lte : str, optional
            Less than or equal, by default None
        published_utc_gt : str, optional
            Greater than, by default None
        published_utc_gte : str, optional
            Greater than or equal, by default None
        order : Literal["asc", "desc"], optional
            The sort order of the query, by default None
        sort : str, optional
            The sort of the query, by default None
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
                The symbol of the company.
        limit : Optional[int]
                The limit of the key metrics ttm to be returned.


        Returns
        -------
        revenue_per_share_ttm: Optional[float]
            The revenue per share of the stock calculated as trailing twelve months.
        net_income_per_share_ttm: Optional[float]
            The net income per share of the stock calculated as trailing twelve months.
        operating_cash_flow_per_share_ttm: Optional[float]
            The operating cash flow per share of the stock calculated as trailing twelve months.
        free_cash_flow_per_share_ttm: Optional[float]
            The free cash flow per share of the stock calculated as trailing twelve months.
        cash_per_share_ttm: Optional[float]
            The cash per share of the stock calculated as trailing twelve months.
        book_value_per_share_ttm: Optional[float]
            The book value per share of the stock calculated as trailing twelve months.
        tangible_book_value_per_share_ttm: Optional[float]
            The tangible book value per share of the stock calculated as trailing twelve months.
        shareholders_equity_per_share_ttm: Optional[float]
            The shareholders equity per share of the stock calculated as trailing twelve months.
        interest_debt_per_share_ttm: Optional[float]
            The interest debt per share of the stock calculated as trailing twelve months.
        market_cap_ttm: Optional[float]
            The market cap of the stock calculated as trailing twelve months.
        enterprise_value_ttm: Optional[float]
            The enterprise value of the stock calculated as trailing twelve months.
        pe_ratio_ttm: Optional[float]
            The PE ratio of the stock calculated as trailing twelve months.
        price_to_sales_ratio_ttm: Optional[float]
            The price to sales ratio of the stock calculated as trailing twelve months.
        pocf_ratio_ttm: Optional[float]
            The POCF ratio of the stock calculated as trailing twelve months.
        pfcf_ratio_ttm: Optional[float]
            The PFCF ratio of the stock calculated as trailing twelve months.
        pb_ratio_ttm: Optional[float]
            The PB ratio of the stock calculated as trailing twelve months.
        ptb_ratio_ttm: Optional[float]
            The PTB ratio of the stock calculated as trailing twelve months.
        ev_to_sales_ttm: Optional[float]
            The EV to sales of the stock calculated as trailing twelve months.
        enterprise_value_over_ebitda_ttm: Optional[float]
            The enterprise value over EBITDA of the stock calculated as trailing twelve months.
        ev_to_operating_cash_flow_ttm: Optional[float]
            The EV to operating cash flow of the stock calculated as trailing twelve months.
        ev_to_free_cash_flow_ttm: Optional[float]
            The EV to free cash flow of the stock calculated as trailing twelve months.
        earnings_yield_ttm: Optional[float]
            The earnings yield of the stock calculated as trailing twelve months.
        free_cash_flow_yield_ttm: Optional[float]
            The free cash flow yield of the stock calculated as trailing twelve months.
        debt_to_equity_ttm: Optional[float]
            The debt to equity of the stock calculated as trailing twelve months.
        debt_to_assets_ttm: Optional[float]
            The debt to assets of the stock calculated as trailing twelve months.
        net_debt_to_ebitda_ttm: Optional[float]
            The net debt to EBITDA of the stock calculated as trailing twelve months.
        current_ratio_ttm: Optional[float]
            The current ratio of the stock calculated as trailing twelve months.
        interest_coverage_ttm: Optional[float]
            The interest coverage of the stock calculated as trailing twelve months.
        income_quality_ttm: Optional[float]
            The income quality of the stock calculated as trailing twelve months.
        dividend_yield_ttm: Optional[float]
            The dividend yield of the stock calculated as trailing twelve months.
        payout_ratio_ttm: Optional[float]
            The payout ratio of the stock calculated as trailing twelve months.
        sales_general_and_administrative_to_revenue_ttm: Optional[float]
            The sales general and administrative to revenue of the stock calculated as trailing twelve months.
        research_and_development_to_revenue_ttm: Optional[float]
            The research and development to revenue of the stock calculated as trailing twelve months.
        intangibles_to_total_assets_ttm: Optional[float]
            The intangibles to total assets of the stock calculated as trailing twelve months.
        capex_to_operating_cash_flow_ttm: Optional[float]
            The capex to operating cash flow of the stock calculated as trailing twelve months.
        capex_to_revenue_ttm: Optional[float]
            The capex to revenue of the stock calculated as trailing twelve months.
        capex_to_depreciation_ttm: Optional[float]
            The capex to depreciation of the stock calculated as trailing twelve months.
        stock_based_compensation_to_revenue_ttm: Optional[float]
            The stock based compensation to revenue of the stock calculated as trailing twelve months.
        graham_number_ttm: Optional[float]
            The graham number of the stock calculated as trailing twelve months.
        roic_ttm: Optional[float]
            The ROIC of the stock calculated as trailing twelve months.
        return_on_tangible_assets_ttm: Optional[float]
            The return on tangible assets of the stock calculated as trailing twelve months.
        graham_net_net_ttm: Optional[float]
            The graham net net of the stock calculated as trailing twelve months.
        working_capital_ttm: Optional[float]
            The working capital of the stock calculated as trailing twelve months.
        tangible_asset_value_ttm: Optional[float]
            The tangible asset value of the stock calculated as trailing twelve months.
        net_current_asset_value_ttm: Optional[float]
            The net current asset value of the stock calculated as trailing twelve months.
        invested_capital_ttm: Optional[float]
            The invested capital of the stock calculated as trailing twelve months.
        average_receivables_ttm: Optional[float]
            The average receivables of the stock calculated as trailing twelve months.
        average_payables_ttm: Optional[float]
            The average payables of the stock calculated as trailing twelve months.
        average_inventory_ttm: Optional[float]
            The average inventory of the stock calculated as trailing twelve months.
        days_sales_outstanding_ttm: Optional[float]
            The days sales outstanding of the stock calculated as trailing twelve months.
        days_payables_outstanding_ttm: Optional[float]
            The days payables outstanding of the stock calculated as trailing twelve months.
        days_of_inventory_on_hand_ttm: Optional[float]
            The days of inventory on hand of the stock calculated as trailing twelve months.
        receivables_turnover_ttm: Optional[float]
            The receivables turnover of the stock calculated as trailing twelve months.
        payables_turnover_ttm: Optional[float]
            The payables turnover of the stock calculated as trailing twelve months.
        inventory_turnover_ttm: Optional[float]
            The inventory turnover of the stock calculated as trailing twelve months.
        roe_ttm: Optional[float]
            The ROE of the stock calculated as trailing twelve months.
        capex_per_share_ttm: Optional[float]
            The capex per share of the stock calculated as trailing twelve months.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Company-Key-Metrics

        Parameter
        ---------
        All fields are standardized.
        """
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
