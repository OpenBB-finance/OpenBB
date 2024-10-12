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
    losers
    top_retail
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
        market_cap : Optional[float]
            Market Cap displayed in billions. (provider: yfinance)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
            Optional[Literal["tmx", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: tmx, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the top price gainers in the stock market.

        Parameters
        ----------
        sort : Literal['asc', 'desc']
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        provider : Optional[Literal['tmx', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: tmx, yfinance.
        category : Literal['dividend', 'energy', 'healthcare', 'industrials', 'price_performer', 'rising_stars', 'real_estate', 'tech', 'utilities', '52w_high', 'volume']
            The category of list to retrieve. Defaults to `price_performer`. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EquityGainers]
                Serializable results.
            provider : Optional[Literal['tmx', 'yfinance']]
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
        thirty_day_price_change : Optional[float]
            30 Day Price Change. (provider: tmx)
        ninety_day_price_change : Optional[float]
            90 Day Price Change. (provider: tmx)
        dividend_yield : Optional[float]
            Dividend Yield. (provider: tmx)
        avg_volume_10d : Optional[float]
            10 Day Avg. Volume. (provider: tmx)
        rank : Optional[int]
            The rank of the stock in the list. (provider: tmx)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
                        ("tmx", "yfinance"),
                    )
                },
                standard_params={
                    "sort": sort,
                },
                extra_params=kwargs,
                info={
                    "category": {
                        "tmx": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "dividend",
                                "energy",
                                "healthcare",
                                "industrials",
                                "price_performer",
                                "rising_stars",
                                "real_estate",
                                "tech",
                                "utilities",
                                "52w_high",
                                "volume",
                            ],
                        }
                    }
                },
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
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
    def top_retail(
        self,
        limit: Annotated[
            int, OpenBBField(description="The number of data entries to return.")
        ] = 5,
        provider: Annotated[
            Optional[Literal["nasdaq"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: nasdaq."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Track over $30B USD/day of individual investors trades.

        It gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
        ADRs, and ETPs.


        Parameters
        ----------
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['nasdaq']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: nasdaq.

        Returns
        -------
        OBBject
            results : List[TopRetail]
                Serializable results.
            provider : Optional[Literal['nasdaq']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TopRetail
        ---------
        date : date
            The date of the data.
        symbol : str
            Symbol representing the entity requested in the data.
        activity : float
            Activity of the symbol.
        sentiment : float
            Sentiment of the symbol. 1 is bullish, -1 is bearish.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.discovery.top_retail(provider='nasdaq')
        """  # noqa: E501

        return self._run(
            "/equity/discovery/top_retail",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.discovery.top_retail",
                        ("nasdaq",),
                    )
                },
                standard_params={
                    "limit": limit,
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
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
        market_cap : Optional[float]
            Market Cap. (provider: yfinance)
        avg_volume_3_months : Optional[float]
            Average volume over the last 3 months in millions. (provider: yfinance)
        pe_ratio_ttm : Optional[float]
            PE Ratio (TTM). (provider: yfinance)

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
