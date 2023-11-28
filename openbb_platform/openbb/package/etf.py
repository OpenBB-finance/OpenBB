### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_etf(Container):
    """/etf
    countries
    /discovery
    holdings
    holdings_date
    holdings_performance
    info
    price_performance
    search
    sectors
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def countries(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for. (ETF)"),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """ETF Country weighting.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EtfCountries]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfCountries
        ------------
        country : str
            The country of the exposure.  Corresponding values are normalized percentage points.

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.countries(symbol="AAPL")
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
            "/etf/countries",
            **inputs,
        )

    @property
    def discovery(self):  # route = "/etf/discovery"
        from . import etf_discovery

        return etf_discovery.ROUTER_etf_discovery(command_runner=self._command_runner)

    @validate
    def holdings(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for. (ETF)"),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the holdings for an individual ETF.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        date : Optional[Union[str, datetime.date]]
            A specific date to get data for. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. (provider: fmp)
        cik : Optional[str]
            The CIK of the filing entity. Overrides symbol. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[EtfHoldings]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfHoldings
        -----------
        symbol : Optional[str]
            Symbol representing the entity requested in the data. (ETF)
        name : Optional[str]
            Name of the ETF holding.
        lei : Optional[str]
            The LEI of the holding. (provider: fmp)
        title : Optional[str]
            The title of the holding. (provider: fmp)
        cusip : Optional[str]
            The CUSIP of the holding. (provider: fmp)
        isin : Optional[str]
            The ISIN of the holding. (provider: fmp)
        balance : Optional[float]
            The balance of the holding. (provider: fmp)
        units : Optional[Union[str, float]]
            The units of the holding. (provider: fmp)
        currency : Optional[str]
            The currency of the holding. (provider: fmp)
        value : Optional[float]
            The value of the holding in USD. (provider: fmp)
        weight : Optional[float]
            The weight of the holding in ETF in %. (provider: fmp)
        payoff_profile : Optional[str]
            The payoff profile of the holding. (provider: fmp)
        asset_category : Optional[str]
            The asset category of the holding. (provider: fmp)
        issuer_category : Optional[str]
            The issuer category of the holding. (provider: fmp)
        country : Optional[str]
            The country of the holding. (provider: fmp)
        is_restricted : Optional[str]
            Whether the holding is restricted. (provider: fmp)
        fair_value_level : Optional[int]
            The fair value level of the holding. (provider: fmp)
        is_cash_collateral : Optional[str]
            Whether the holding is cash collateral. (provider: fmp)
        is_non_cash_collateral : Optional[str]
            Whether the holding is non-cash collateral. (provider: fmp)
        is_loan_by_fund : Optional[str]
            Whether the holding is loan by fund. (provider: fmp)
        cik : Optional[str]
            The CIK of the filing. (provider: fmp)
        acceptance_datetime : Optional[str]
            The acceptance datetime of the filing. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.holdings(symbol="AAPL")
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
            "/etf/holdings",
            **inputs,
        )

    @validate
    def holdings_date(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for. (ETF)"),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the holdings filing date for an individual ETF.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[str]
            The CIK of the filing entity. Overrides symbol. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[EtfHoldingsDate]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfHoldingsDate
        ---------------
        date : date
            The date of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.holdings_date(symbol="AAPL")
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
            "/etf/holdings_date",
            **inputs,
        )

    @validate
    def holdings_performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the ETF holdings performance.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EtfHoldingsPerformance]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfHoldingsPerformance
        ----------------------
        one_day : Optional[float]
            One-day return.
        wtd : Optional[float]
            Week to date return.
        one_week : Optional[float]
            One-week return.
        mtd : Optional[float]
            Month to date return.
        one_month : Optional[float]
            One-month return.
        qtd : Optional[float]
            Quarter to date return.
        three_month : Optional[float]
            Three-month return.
        six_month : Optional[float]
            Six-month return.
        ytd : Optional[float]
            Year to date return.
        one_year : Optional[float]
            One-year return.
        three_year : Optional[float]
            Three-year return.
        five_year : Optional[float]
            Five-year return.
        ten_year : Optional[float]
            Ten-year return.
        max : Optional[float]
            Return from the beginning of the time series.
        symbol : Optional[str]
            The ticker symbol. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.holdings_performance(symbol="AAPL")
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
            "/etf/holdings_performance",
            **inputs,
        )

    @validate
    def info(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for. (ETF)"),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """ETF Information Overview.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EtfInfo]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfInfo
        -------
        symbol : str
            Symbol representing the entity requested in the data. (ETF)
        name : Optional[str]
            Name of the ETF.
        inception_date : Optional[str]
            Inception date of the ETF.
        asset_class : Optional[str]
            Asset class of the ETF. (provider: fmp)
        aum : Optional[float]
            Assets under management. (provider: fmp)
        avg_volume : Optional[float]
            Average trading volume of the ETF. (provider: fmp)
        cusip : Optional[str]
            CUSIP of the ETF. (provider: fmp)
        description : Optional[str]
            Description of the ETF. (provider: fmp)
        domicile : Optional[str]
            Domicile of the ETF. (provider: fmp)
        etf_company : Optional[str]
            Company of the ETF. (provider: fmp)
        expense_ratio : Optional[float]
            Expense ratio of the ETF. (provider: fmp)
        isin : Optional[str]
            ISIN of the ETF. (provider: fmp)
        nav : Optional[float]
            Net asset value of the ETF. (provider: fmp)
        nav_currency : Optional[str]
            Currency of the ETF's net asset value. (provider: fmp)
        website : Optional[str]
            Website link of the ETF. (provider: fmp)
        holdings_count : Optional[int]
            Number of holdings in the ETF. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.info(symbol="AAPL")
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
            "/etf/info",
            **inputs,
        )

    @validate
    def price_performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Price performance as a return, over different periods.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[PricePerformance]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        PricePerformance
        ----------------
        one_day : Optional[float]
            One-day return.
        wtd : Optional[float]
            Week to date return.
        one_week : Optional[float]
            One-week return.
        mtd : Optional[float]
            Month to date return.
        one_month : Optional[float]
            One-month return.
        qtd : Optional[float]
            Quarter to date return.
        three_month : Optional[float]
            Three-month return.
        six_month : Optional[float]
            Six-month return.
        ytd : Optional[float]
            Year to date return.
        one_year : Optional[float]
            One-year return.
        three_year : Optional[float]
            Three-year return.
        five_year : Optional[float]
            Five-year return.
        ten_year : Optional[float]
            Ten-year return.
        max : Optional[float]
            Return from the beginning of the time series.
        symbol : Optional[str]
            The ticker symbol. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.price.performance(symbol="AAPL")
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
            "/etf/price_performance",
            **inputs,
        )

    @validate
    def search(
        self,
        query: Annotated[
            Optional[str], OpenBBCustomParameter(description="Search query.")
        ] = "",
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Search for ETFs.

            An empty query returns the full list of ETFs from the provider.


        Parameters
        ----------
        query : Optional[str]
            Search query.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        exchange : Optional[Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT']]
            The exchange code the ETF trades on. (provider: fmp)
        is_active : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[EtfSearch]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfSearch
        ---------
        symbol : str
            Symbol representing the entity requested in the data.(ETF)
        name : Optional[str]
            Name of the ETF.
        market_cap : Optional[float]
            The market cap of the ETF. (provider: fmp)
        sector : Optional[str]
            The sector of the ETF. (provider: fmp)
        industry : Optional[str]
            The industry of the ETF. (provider: fmp)
        beta : Optional[float]
            The beta of the ETF. (provider: fmp)
        price : Optional[float]
            The current price of the ETF. (provider: fmp)
        last_annual_dividend : Optional[float]
            The last annual dividend paid. (provider: fmp)
        volume : Optional[float]
            The current trading volume of the ETF. (provider: fmp)
        exchange : Optional[str]
            The exchange code the ETF trades on. (provider: fmp)
        exchange_name : Optional[str]
            The full name of the exchange the ETF trades on. (provider: fmp)
        country : Optional[str]
            The country the ETF is registered in. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/etf/search",
            **inputs,
        )

    @validate
    def sectors(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for. (ETF)"),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """ETF Sector weighting.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EtfSectors]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfSectors
        ----------
        sector : str
            Sector of exposure.
        weight : Optional[float]
            Exposure of the ETF to the sector in normalized percentage points.

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.sectors(symbol="AAPL")
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
            "/etf/sectors",
            **inputs,
        )
