### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_discovery(Container):
    """/equity/discovery
    active
    aggressive_small_caps
    filings
    gainers
    growth_tech
    latest_financial_reports
    losers
    undervalued_growth
    undervalued_large_caps
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def active(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the most actively traded stocks based on volume.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityActive]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityActive
        ------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.active(provider='yfinance')
        >>> obb.equity.discovery.active(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/active",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.active",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def aggressive_small_caps(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get top small cap stocks based on earnings growth.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. Default is all. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityAggressiveSmallCaps]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityAggressiveSmallCaps
        -------------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.aggressive_small_caps(provider='yfinance')
        >>> obb.equity.discovery.aggressive_small_caps(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/aggressive_small_caps",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.aggressive_small_caps",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def filings(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        form_type: Annotated[
            Optional[str],
            OpenBBField(
                description="Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types."
            ),
        ] = None,
        limit: Annotated[
            int, OpenBBField(description="The number of data entries to return.")
        ] = 100,
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the URLs to SEC filings reported to EDGAR database, such as 10-K, 10-Q, 8-K, and more.

        SEC filings include Form 10-K, Form 10-Q, Form 8-K, the proxy statement, Forms 3, 4, and 5, Schedule 13, Form 114,
        Foreign Investment Disclosures and others. The annual 10-K report is required to be
        filed annually and includes the company's financial statements, management discussion and analysis,
        and audited financial statements.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        form_type : Optional[str]
            Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp.
        is_done : Optional[bool]
            Flag for whether or not the filing is done. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[DiscoveryFilings]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        DiscoveryFilings
        ----------------
        symbol : str
            Symbol representing the entity requested in the data.
        cik : str
            Central Index Key (CIK) for the requested entity.
        title : str
            Title of the filing.
        date : datetime
            The date of the data.
        form_type : str
            The form type of the filing
        link : str
            URL to the filing page on the SEC site.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.filings(provider='fmp')
        >>> # Get filings for the year 2023, limited to 100 results
        >>> obb.equity.discovery.filings(start_date='2023-01-01', end_date='2023-12-31', limit=100, provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/filings",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.filings",
                        ("fmp",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "form_type": form_type,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def gainers(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the top price gainers in the stock market.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityGainers]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityGainers
        -------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.gainers(provider='yfinance')
        >>> obb.equity.discovery.gainers(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/gainers",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.gainers",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def growth_tech(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get top tech stocks based on revenue and earnings growth.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[GrowthTechEquities]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        GrowthTechEquities
        ------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.growth_tech(provider='yfinance')
        >>> obb.equity.discovery.growth_tech(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/growth_tech",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.growth_tech",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def latest_financial_reports(
        self,
        provider: Annotated[
            Optional[Literal["sec"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: sec."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the newest quarterly, annual, and current reports for all companies.

        Parameters
        ----------
        provider : Optional[Literal['sec']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: sec.
        date : Optional[datetime.date]
            A specific date to get data for. Defaults to today. (provider: sec)
        report_type : Optional[str]
            Return only a specific form type. Default is all quarterly, annual, and current reports. Choices: 1-K, 1-SA, 1-U, 10-D, 10-K, 10-KT, 10-Q, 10-QT, 20-F, 40-F, 6-K, 8-K. Multiple comma separated items allowed. (provider: sec)

        Returns
        -------
        OBBject
            results : List[LatestFinancialReports]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        LatestFinancialReports
        ----------------------
        filing_date : date
            The date of the filing.
        period_ending : Optional[date]
            Report for the period ending.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the company.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        sic : Optional[str]
            Standard Industrial Classification code.
        report_type : Optional[str]
            Type of filing.
        description : Optional[str]
            Description of the report.
        url : str
            URL to the filing page.
        items : Optional[str]
            Item codes associated with the filing. (provider: sec)
        index_headers : Optional[str]
            URL to the index headers file. (provider: sec)
        complete_submission : Optional[str]
            URL to the complete submission text file. (provider: sec)
        metadata : Optional[str]
            URL to the MetaLinks.json file, if available. (provider: sec)
        financial_report : Optional[str]
            URL to the Financial_Report.xlsx file, if available. (provider: sec)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.latest_financial_reports(provider='sec')
        >>> obb.equity.discovery.latest_financial_reports(provider='sec', date='2024-09-30')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/latest_financial_reports",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.latest_financial_reports",
                        ("sec",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "report_type": {
                        "sec": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "1-K",
                                "1-SA",
                                "1-U",
                                "10-D",
                                "10-K",
                                "10-KT",
                                "10-Q",
                                "10-QT",
                                "20-F",
                                "40-F",
                                "6-K",
                                "8-K",
                            ],
                        }
                    }
                },
            )
        )

    @exception_handler
    @validate
    def losers(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the top price losers in the stock market.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityLosers]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityLosers
        ------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.losers(provider='yfinance')
        >>> obb.equity.discovery.losers(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/losers",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.losers",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def undervalued_growth(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get potentially undervalued growth stocks.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityUndervaluedGrowth]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityUndervaluedGrowth
        -----------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.undervalued_growth(provider='yfinance')
        >>> obb.equity.discovery.undervalued_growth(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/undervalued_growth",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.undervalued_growth",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def undervalued_large_caps(
        self,
        sort: Annotated[
            Literal["asc", "desc"],
            OpenBBField(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get potentially undervalued large cap stocks.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        limit : Optional[int]
            Limit the number of results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityUndervaluedLargeCaps]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityUndervaluedLargeCaps
        --------------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        price : float
            Last price.
        change : float
            Change in price.
        percent_change : float
            Percent change.
        volume : Union[int, float]
            The trading volume.
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange : Optional[str]
            Exchange where the stock is listed. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.undervalued_large_caps(provider='yfinance')
        >>> obb.equity.discovery.undervalued_large_caps(sort='desc', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/undervalued_large_caps",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.undervalued_large_caps",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
            )
        )
