### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union
from warnings import simplefilter, warn

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_etf(Container):
    """/etf
    countries
    equity_exposure
    historical
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

    @exception_handler
    @validate
    def countries(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. (ETF) Multiple comma separated items allowed for provider(s): fmp."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """ETF Country weighting.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. (ETF) Multiple comma separated items allowed for provider(s): fmp.
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
            extra : Dict[str, Any]
                Extra info.

        EtfCountries
        ------------
        country : str
            The country of the exposure.  Corresponding values are normalized percentage points.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.countries(symbol='VT', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/countries",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/countries",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    def equity_exposure(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. (Stock) Multiple comma separated items allowed for provider(s): fmp."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the exposure to ETFs for a specific stock.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. (Stock) Multiple comma separated items allowed for provider(s): fmp.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EtfEquityExposure]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EtfEquityExposure
        -----------------
        equity_symbol : str
            The symbol of the equity requested.
        etf_symbol : str
            The symbol of the ETF with exposure to the requested equity.
        shares : Optional[float]
            The number of shares held in the ETF.
        weight : Optional[float]
            The weight of the equity in the ETF, as a normalized percent.
        market_value : Optional[Union[float, int]]
            The market value of the equity position in the ETF.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.equity_exposure(symbol='MSFT', provider='fmp')
        >>> # This function accepts multiple tickers.
        >>> obb.etf.equity_exposure(symbol='MSFT,AAPL', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/equity_exposure",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/equity_exposure",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, polygon, tiingo, yfinance."
            ),
        ],
        interval: Annotated[
            Optional[str],
            OpenBBField(description="Time interval of the data to return."),
        ] = "1d",
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "polygon", "tiingo", "yfinance"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """ETF Historical Market Price.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, polygon, tiingo, yfinance.
        interval : Optional[str]
            Time interval of the data to return.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'tiingo', 'yfinanc...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        start_time : Optional[datetime.time]
            Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        end_time : Optional[datetime.time]
            Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        timezone : Optional[str]
            Timezone of the data, in the IANA format (Continent/City). (provider: intrinio)
        source : Literal['realtime', 'delayed', 'nasdaq_basic']
            The source of the data. (provider: intrinio)
        adjustment : Union[Literal['splits_only', 'unadjusted'], Literal['splits_only', 'splits_and_dividends']]
            The adjustment factor to apply. Default is splits only. (provider: polygon, yfinance)
        extended_hours : bool
            Include Pre and Post market data. (provider: polygon, yfinance)
        sort : Literal['asc', 'desc']
            Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date. (provider: polygon)
        limit : int
            The number of data entries to return. (provider: polygon)
        include_actions : bool
            Include dividends and stock splits in results. (provider: yfinance)
        adjusted : bool
            This field is deprecated (4.1.5) and will be removed in a future version. Use 'adjustment' set as 'splits_and_dividends' instead. (provider: yfinance)
        prepost : bool
            This field is deprecated (4.1.5) and will be removed in a future version. Use 'extended_hours' as True instead. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EtfHistorical]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EtfHistorical
        -------------
        date : Union[date, datetime]
            The date of the data.
        open : float
            The open price.
        high : float
            The high price.
        low : float
            The low price.
        close : float
            The close price.
        volume : Optional[Union[float, int]]
            The trading volume.
        vwap : Optional[float]
            Volume Weighted Average Price over the period.
        adj_close : Optional[float]
            The adjusted close price. (provider: fmp, intrinio, tiingo)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price from the previous close. (provider: fmp);
            Change in the price of the symbol from the previous day. (provider: intrinio)
        change_percent : Optional[float]
            Change in the price from the previous close, as a normalized percent. (provider: fmp);
            Percent change in the price of the symbol from the previous day. (provider: intrinio)
        average : Optional[float]
            Average trade price of an individual equity during the interval. (provider: intrinio)
        adj_open : Optional[float]
            The adjusted open price. (provider: intrinio, tiingo)
        adj_high : Optional[float]
            The adjusted high price. (provider: intrinio, tiingo)
        adj_low : Optional[float]
            The adjusted low price. (provider: intrinio, tiingo)
        adj_volume : Optional[float]
            The adjusted volume. (provider: intrinio, tiingo)
        fifty_two_week_high : Optional[float]
            52 week high price for the symbol. (provider: intrinio)
        fifty_two_week_low : Optional[float]
            52 week low price for the symbol. (provider: intrinio)
        factor : Optional[float]
            factor by which to multiply equity prices before this date, in order to calculate historically-adjusted equity prices. (provider: intrinio)
        split_ratio : Optional[float]
            Ratio of the equity split, if a split occurred. (provider: intrinio, tiingo, yfinance)
        dividend : Optional[float]
            Dividend amount, if a dividend was paid. (provider: intrinio, tiingo, yfinance)
        close_time : Optional[datetime]
            The timestamp that represents the end of the interval span. (provider: intrinio)
        interval : Optional[str]
            The data time frequency. (provider: intrinio)
        intra_period : Optional[bool]
            If true, the equity price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period (provider: intrinio)
        transactions : Optional[Annotated[int, Gt(gt=0)]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.historical(symbol='SPY', provider='fmp')
        >>> obb.etf.historical(symbol='SPY', provider='yfinance')
        >>> # This function accepts multiple tickers.
        >>> obb.etf.historical(symbol='SPY,IWM,QQQ,DJIA', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/etf/historical",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/historical",
                        ("fmp", "intrinio", "polygon", "tiingo", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "interval": interval,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "multiple_items_allowed": [
                            "fmp",
                            "polygon",
                            "tiingo",
                            "yfinance",
                        ]
                    },
                    "adjusted": {"deprecated": True},
                    "prepost": {"deprecated": True},
                },
            )
        )

    @exception_handler
    @validate
    def holdings(
        self,
        symbol: Annotated[
            str, OpenBBField(description="Symbol to get data for. (ETF)")
        ],
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "sec"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the holdings for an individual ETF.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp', 'intrinio', 'sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        date : Optional[Union[str, datetime.date]]
            A specific date to get data for. Entering a date will attempt to return the NPORT-P filing for the entered date. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. (provider: fmp);
            A specific date to get data for. (provider: intrinio);
            A specific date to get data for.  The date represents the period ending. The date entered will return the closest filing. (provider: sec)
        cik : Optional[str]
            The CIK of the filing entity. Overrides symbol. (provider: fmp)
        use_cache : bool
            Whether or not to use cache for the request. (provider: sec)

        Returns
        -------
        OBBject
            results : List[EtfHoldings]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EtfHoldings
        -----------
        symbol : Optional[str]
            Symbol representing the entity requested in the data. (ETF)
        name : Optional[str]
            Name of the ETF holding.
        lei : Optional[str]
            The LEI of the holding. (provider: fmp, sec)
        title : Optional[str]
            The title of the holding. (provider: fmp)
        cusip : Optional[str]
            The CUSIP of the holding. (provider: fmp, sec)
        isin : Optional[str]
            The ISIN of the holding. (provider: fmp, intrinio, sec)
        balance : Optional[int]
            The balance of the holding, in shares or units. (provider: fmp);
            The number of units of the security held, if available. (provider: intrinio);
            The balance of the holding. (provider: sec)
        units : Optional[Union[str, float]]
            The type of units. (provider: fmp);
            The units of the holding. (provider: sec)
        currency : Optional[str]
            The currency of the holding. (provider: fmp, sec)
        value : Optional[float]
            The value of the holding, in dollars. (provider: fmp, intrinio, sec)
        weight : Optional[float]
            The weight of the holding, as a normalized percent. (provider: fmp, intrinio);
            The weight of the holding in ETF in %. (provider: sec)
        payoff_profile : Optional[str]
            The payoff profile of the holding. (provider: fmp, sec)
        asset_category : Optional[str]
            The asset category of the holding. (provider: fmp, sec)
        issuer_category : Optional[str]
            The issuer category of the holding. (provider: fmp, sec)
        country : Optional[str]
            The country of the holding. (provider: fmp, intrinio, sec)
        is_restricted : Optional[str]
            Whether the holding is restricted. (provider: fmp, sec)
        fair_value_level : Optional[int]
            The fair value level of the holding. (provider: fmp, sec)
        is_cash_collateral : Optional[str]
            Whether the holding is cash collateral. (provider: fmp, sec)
        is_non_cash_collateral : Optional[str]
            Whether the holding is non-cash collateral. (provider: fmp, sec)
        is_loan_by_fund : Optional[str]
            Whether the holding is loan by fund. (provider: fmp, sec)
        cik : Optional[str]
            The CIK of the filing. (provider: fmp)
        acceptance_datetime : Optional[str]
            The acceptance datetime of the filing. (provider: fmp)
        updated : Optional[Union[date, datetime]]
            The date the data was updated. (provider: fmp);
            The 'as_of' date for the holding. (provider: intrinio)
        security_type : Optional[str]
            The type of instrument for this holding. Examples(Bond='BOND', Equity='EQUI') (provider: intrinio)
        ric : Optional[str]
            The Reuters Instrument Code. (provider: intrinio)
        sedol : Optional[str]
            The Stock Exchange Daily Official List. (provider: intrinio)
        share_class_figi : Optional[str]
            The OpenFIGI symbol for the holding. (provider: intrinio)
        maturity_date : Optional[date]
            The maturity date for the debt security, if available. (provider: intrinio, sec)
        contract_expiry_date : Optional[date]
            Expiry date for the futures contract held, if available. (provider: intrinio)
        coupon : Optional[float]
            The coupon rate of the debt security, if available. (provider: intrinio)
        unit : Optional[str]
            The units of the 'balance' field. (provider: intrinio)
        units_per_share : Optional[float]
            Number of units of the security held per share outstanding of the ETF, if available. (provider: intrinio)
        face_value : Optional[float]
            The face value of the debt security, if available. (provider: intrinio)
        derivatives_value : Optional[float]
            The notional value of derivatives contracts held. (provider: intrinio)
        other_id : Optional[str]
            Internal identifier for the holding. (provider: sec)
        loan_value : Optional[float]
            The loan value of the holding. (provider: sec)
        issuer_conditional : Optional[str]
            The issuer conditions of the holding. (provider: sec)
        asset_conditional : Optional[str]
            The asset conditions of the holding. (provider: sec)
        coupon_kind : Optional[str]
            The type of coupon for the debt security. (provider: sec)
        rate_type : Optional[str]
            The type of rate for the debt security, floating or fixed. (provider: sec)
        annualized_return : Optional[float]
            The annualized return on the debt security. (provider: sec)
        is_default : Optional[str]
            If the debt security is defaulted. (provider: sec)
        in_arrears : Optional[str]
            If the debt security is in arrears. (provider: sec)
        is_paid_kind : Optional[str]
            If the debt security payments are paid in kind. (provider: sec)
        derivative_category : Optional[str]
            The derivative category of the holding. (provider: sec)
        counterparty : Optional[str]
            The counterparty of the derivative. (provider: sec)
        underlying_name : Optional[str]
            The name of the underlying asset associated with the derivative. (provider: sec)
        option_type : Optional[str]
            The type of option. (provider: sec)
        derivative_payoff : Optional[str]
            The payoff profile of the derivative. (provider: sec)
        expiry_date : Optional[date]
            The expiry or termination date of the derivative. (provider: sec)
        exercise_price : Optional[float]
            The exercise price of the option. (provider: sec)
        exercise_currency : Optional[str]
            The currency of the option exercise price. (provider: sec)
        shares_per_contract : Optional[float]
            The number of shares per contract. (provider: sec)
        delta : Optional[Union[str, float]]
            The delta of the option. (provider: sec)
        rate_type_rec : Optional[str]
            The type of rate for receivable portion of the swap. (provider: sec)
        receive_currency : Optional[str]
            The receive currency of the swap. (provider: sec)
        upfront_receive : Optional[float]
            The upfront amount received of the swap. (provider: sec)
        floating_rate_index_rec : Optional[str]
            The floating rate index for receivable portion of the swap. (provider: sec)
        floating_rate_spread_rec : Optional[float]
            The floating rate spread for reveivable portion of the swap. (provider: sec)
        rate_tenor_rec : Optional[str]
            The rate tenor for receivable portion of the swap. (provider: sec)
        rate_tenor_unit_rec : Optional[Union[str, int]]
            The rate tenor unit for receivable portion of the swap. (provider: sec)
        reset_date_rec : Optional[str]
            The reset date for receivable portion of the swap. (provider: sec)
        reset_date_unit_rec : Optional[Union[str, int]]
            The reset date unit for receivable portion of the swap. (provider: sec)
        rate_type_pmnt : Optional[str]
            The type of rate for payment portion of the swap. (provider: sec)
        payment_currency : Optional[str]
            The payment currency of the swap. (provider: sec)
        upfront_payment : Optional[float]
            The upfront amount received of the swap. (provider: sec)
        floating_rate_index_pmnt : Optional[str]
            The floating rate index for payment portion of the swap. (provider: sec)
        floating_rate_spread_pmnt : Optional[float]
            The floating rate spread for payment portion of the swap. (provider: sec)
        rate_tenor_pmnt : Optional[str]
            The rate tenor for payment portion of the swap. (provider: sec)
        rate_tenor_unit_pmnt : Optional[Union[str, int]]
            The rate tenor unit for payment portion of the swap. (provider: sec)
        reset_date_pmnt : Optional[str]
            The reset date for payment portion of the swap. (provider: sec)
        reset_date_unit_pmnt : Optional[Union[str, int]]
            The reset date unit for payment portion of the swap. (provider: sec)
        repo_type : Optional[str]
            The type of repo. (provider: sec)
        is_cleared : Optional[str]
            If the repo is cleared. (provider: sec)
        is_tri_party : Optional[str]
            If the repo is tri party. (provider: sec)
        principal_amount : Optional[float]
            The principal amount of the repo. (provider: sec)
        principal_currency : Optional[str]
            The currency of the principal amount. (provider: sec)
        collateral_type : Optional[str]
            The collateral type of the repo. (provider: sec)
        collateral_amount : Optional[float]
            The collateral amount of the repo. (provider: sec)
        collateral_currency : Optional[str]
            The currency of the collateral amount. (provider: sec)
        exchange_currency : Optional[str]
            The currency of the exchange rate. (provider: sec)
        exchange_rate : Optional[float]
            The exchange rate. (provider: sec)
        currency_sold : Optional[str]
            The currency sold in a Forward Derivative. (provider: sec)
        currency_amount_sold : Optional[float]
            The amount of currency sold in a Forward Derivative. (provider: sec)
        currency_bought : Optional[str]
            The currency bought in a Forward Derivative. (provider: sec)
        currency_amount_bought : Optional[float]
            The amount of currency bought in a Forward Derivative. (provider: sec)
        notional_amount : Optional[float]
            The notional amount of the derivative. (provider: sec)
        notional_currency : Optional[str]
            The currency of the derivative's notional amount. (provider: sec)
        unrealized_gain : Optional[float]
            The unrealized gain or loss on the derivative. (provider: sec)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.holdings(symbol='XLK', provider='fmp')
        >>> # Including a date (FMP, SEC) will return the holdings as per NPORT-P filings.
        >>> obb.etf.holdings(symbol='XLK', date='2022-03-31', provider='fmp')
        >>> # The same data can be returned from the SEC directly.
        >>> obb.etf.holdings(symbol='XLK', date='2022-03-31', provider='sec')
        """  # noqa: E501

        return self._run(
            "/etf/holdings",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/holdings",
                        ("fmp", "intrinio", "sec"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def holdings_date(
        self,
        symbol: Annotated[
            str, OpenBBField(description="Symbol to get data for. (ETF)")
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Use this function to get the holdings dates, if available.

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
            extra : Dict[str, Any]
                Extra info.

        EtfHoldingsDate
        ---------------
        date : date
            The date of the data.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.holdings_date(symbol='XLK', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/holdings_date",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/holdings_date",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint is deprecated; pass a list of holdings symbols directly to `/equity/price/performance` instead. Deprecated in OpenBB Platform V4.1 to be removed in V4.2.",
        category=OpenBBDeprecationWarning,
    )
    def holdings_performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the recent price performance of each ticker held in the ETF.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp.
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
            extra : Dict[str, Any]
                Extra info.

        EtfHoldingsPerformance
        ----------------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
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
        two_year : Optional[float]
            Two-year return.
        three_year : Optional[float]
            Three-year return.
        four_year : Optional[float]
            Four-year
        five_year : Optional[float]
            Five-year return.
        ten_year : Optional[float]
            Ten-year return.
        max : Optional[float]
            Return from the beginning of the time series.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.holdings_performance(symbol='XLK', provider='fmp')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint is deprecated; pass a list of holdings symbols directly to `/equity/price/performance` instead. Deprecated in OpenBB Platform V4.1 to be removed in V4.2.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/etf/holdings_performance",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/holdings_performance",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    def info(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. (ETF) Multiple comma separated items allowed for provider(s): fmp, intrinio, yfinance."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "yfinance"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """ETF Information Overview.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. (ETF) Multiple comma separated items allowed for provider(s): fmp, intrinio, yfinance.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EtfInfo]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EtfInfo
        -------
        symbol : str
            Symbol representing the entity requested in the data. (ETF)
        name : Optional[str]
            Name of the ETF.
        description : Optional[str]
            Description of the fund.
        inception_date : Optional[str]
            Inception date of the ETF.
        issuer : Optional[str]
            Company of the ETF. (provider: fmp);
            Issuer of the ETF. (provider: intrinio)
        cusip : Optional[str]
            CUSIP of the ETF. (provider: fmp)
        isin : Optional[str]
            ISIN of the ETF. (provider: fmp);
            International Securities Identification Number (ISIN). (provider: intrinio)
        domicile : Optional[str]
            Domicile of the ETF. (provider: fmp);
            2 letter ISO country code for the country where the ETP is domiciled. (provider: intrinio)
        asset_class : Optional[str]
            Asset class of the ETF. (provider: fmp);
            Captures the underlying nature of the securities in the Exchanged Traded Product (ETP). (provider: intrinio)
        aum : Optional[float]
            Assets under management. (provider: fmp)
        nav : Optional[float]
            Net asset value of the ETF. (provider: fmp)
        nav_currency : Optional[str]
            Currency of the ETF's net asset value. (provider: fmp)
        expense_ratio : Optional[float]
            The expense ratio, as a normalized percent. (provider: fmp)
        holdings_count : Optional[int]
            Number of holdings. (provider: fmp)
        avg_volume : Optional[float]
            Average daily trading volume. (provider: fmp)
        website : Optional[str]
            Website of the issuer. (provider: fmp)
        fund_listing_date : Optional[date]
            The date on which the Exchange Traded Product (ETP) or share class of the ETP is listed on a specific exchange. (provider: intrinio)
        data_change_date : Optional[date]
            The last date on which there was a change in a classifications data field for this ETF. (provider: intrinio)
        etn_maturity_date : Optional[date]
            If the product is an ETN, this field identifies the maturity date for the ETN. (provider: intrinio)
        is_listed : Optional[bool]
            If true, the ETF is still listed on an exchange. (provider: intrinio)
        close_date : Optional[date]
            The date on which the ETF was de-listed if it is no longer listed. (provider: intrinio)
        exchange : Optional[str]
            The exchange Market Identifier Code (MIC). (provider: intrinio);
            The exchange the fund is listed on. (provider: yfinance)
        ric : Optional[str]
            Reuters Instrument Code (RIC). (provider: intrinio)
        sedol : Optional[str]
            Stock Exchange Daily Official List (SEDOL). (provider: intrinio)
        figi_symbol : Optional[str]
            Financial Instrument Global Identifier (FIGI) symbol. (provider: intrinio)
        share_class_figi : Optional[str]
            Financial Instrument Global Identifier (FIGI). (provider: intrinio)
        firstbridge_id : Optional[str]
            The FirstBridge unique identifier for the Exchange Traded Fund (ETF). (provider: intrinio)
        firstbridge_parent_id : Optional[str]
            The FirstBridge unique identifier for the parent Exchange Traded Fund (ETF), if applicable. (provider: intrinio)
        intrinio_id : Optional[str]
            Intrinio unique identifier for the security. (provider: intrinio)
        intraday_nav_symbol : Optional[str]
            Intraday Net Asset Value (NAV) symbol. (provider: intrinio)
        primary_symbol : Optional[str]
            The primary ticker field is used for Exchange Traded Products (ETPs) that have multiple listings and share classes. If an ETP has multiple listings or share classes, the same primary ticker is assigned to all the listings and share classes. (provider: intrinio)
        etp_structure_type : Optional[str]
            Classifies Exchange Traded Products (ETPs) into very broad categories based on its legal structure. (provider: intrinio)
        legal_structure : Optional[str]
            Legal structure of the fund. (provider: intrinio)
        etn_issuing_bank : Optional[str]
            If the product is an Exchange Traded Note (ETN), this field identifies the issuing bank. (provider: intrinio)
        fund_family : Optional[str]
            This field identifies the fund family to which the ETF belongs, as categorized by the ETF Sponsor. (provider: intrinio);
            The fund family. (provider: yfinance)
        investment_style : Optional[str]
            Investment style of the ETF. (provider: intrinio)
        derivatives_based : Optional[str]
            This field is populated if the ETF holds either listed or over-the-counter derivatives in its portfolio. (provider: intrinio)
        income_category : Optional[str]
            Identifies if an Exchange Traded Fund (ETF) falls into a category that is specifically designed to provide a high yield or income (provider: intrinio)
        other_asset_types : Optional[str]
            If 'asset_class' field is classified as 'Other Asset Types' this field captures the specific category of the underlying assets. (provider: intrinio)
        single_category_designation : Optional[str]
            This categorization is created for those users who want every ETF to be 'forced' into a single bucket, so that the assets for all categories will always sum to the total market. (provider: intrinio)
        beta_type : Optional[str]
            This field identifies whether an ETF provides 'Traditional' beta exposure or 'Smart' beta exposure. ETFs that are active (i.e. non-indexed), leveraged / inverse or have a proprietary quant model (i.e. that don't provide indexed exposure to a targeted factor) are classified separately. (provider: intrinio)
        beta_details : Optional[str]
            This field provides further detail within the traditional and smart beta categories. (provider: intrinio)
        market_cap_range : Optional[str]
            Equity ETFs are classified as falling into categories based on the description of their investment strategy in the prospectus. Examples ('Mega Cap', 'Large Cap', 'Mid Cap', etc.) (provider: intrinio)
        market_cap_weighting_type : Optional[str]
            For ETFs that take the value 'Market Cap Weighted' in the 'index_weighting_scheme' field, this field provides detail on the market cap weighting type. (provider: intrinio)
        index_weighting_scheme : Optional[str]
            For ETFs that track an underlying index, this field provides detail on the index weighting type. (provider: intrinio)
        index_linked : Optional[str]
            This field identifies whether an ETF is index linked or active. (provider: intrinio)
        index_name : Optional[str]
            This field identifies the name of the underlying index tracked by the ETF, if applicable. (provider: intrinio)
        index_symbol : Optional[str]
            This field identifies the OpenFIGI ticker for the Index underlying the ETF. (provider: intrinio)
        parent_index : Optional[str]
            This field identifies the name of the parent index, which represents the broader universe from which the index underlying the ETF is created, if applicable. (provider: intrinio)
        index_family : Optional[str]
            This field identifies the index family to which the index underlying the ETF belongs. The index family is represented as categorized by the index provider. (provider: intrinio)
        broader_index_family : Optional[str]
            This field identifies the broader index family to which the index underlying the ETF belongs. The broader index family is represented as categorized by the index provider. (provider: intrinio)
        index_provider : Optional[str]
            This field identifies the Index provider for the index underlying the ETF, if applicable. (provider: intrinio)
        index_provider_code : Optional[str]
            This field provides the First Bridge code for each Index provider, corresponding to the index underlying the ETF if applicable. (provider: intrinio)
        replication_structure : Optional[str]
            The replication structure of the Exchange Traded Product (ETP). (provider: intrinio)
        growth_value_tilt : Optional[str]
            Classifies equity ETFs as either 'Growth' or Value' based on the stated style tilt in the ETF prospectus. Equity ETFs that do not have a stated style tilt are classified as 'Core / Blend'. (provider: intrinio)
        growth_type : Optional[str]
            For ETFs that are classified as 'Growth' in 'growth_value_tilt', this field further identifies those where the stocks in the ETF are both selected and weighted based on their growth (style factor) scores. (provider: intrinio)
        value_type : Optional[str]
            For ETFs that are classified as 'Value' in 'growth_value_tilt', this field further identifies those where the stocks in the ETF are both selected and weighted based on their value (style factor) scores. (provider: intrinio)
        sector : Optional[str]
            For equity ETFs that aim to provide targeted exposure to a sector or industry, this field identifies the Sector that it provides the exposure to. (provider: intrinio)
        industry : Optional[str]
            For equity ETFs that aim to provide targeted exposure to an industry, this field identifies the Industry that it provides the exposure to. (provider: intrinio)
        industry_group : Optional[str]
            For equity ETFs that aim to provide targeted exposure to a sub-industry, this field identifies the sub-Industry that it provides the exposure to. (provider: intrinio)
        cross_sector_theme : Optional[str]
            For equity ETFs that aim to provide targeted exposure to a specific investment theme that cuts across GICS sectors, this field identifies the specific cross-sector theme. Examples ('Agri-business', 'Natural Resources', 'Green Investing', etc.) (provider: intrinio)
        natural_resources_type : Optional[str]
            For ETFs that are classified as 'Natural Resources' in the 'cross_sector_theme' field, this field provides further detail on the type of Natural Resources exposure. (provider: intrinio)
        us_or_excludes_us : Optional[str]
            Takes the value of 'Domestic' for US exposure, 'International' for non-US exposure and 'Global' for exposure that includes all regions including the US. (provider: intrinio)
        developed_emerging : Optional[str]
            This field identifies the stage of development of the markets that the ETF provides exposure to. (provider: intrinio)
        specialized_region : Optional[str]
            This field is populated if the ETF provides targeted exposure to a specific type of geography-based grouping that does not fall into a specific country or continent grouping. Examples ('BRIC', 'Chindia', etc.) (provider: intrinio)
        continent : Optional[str]
            This field is populated if the ETF provides targeted exposure to a specific continent or country within that Continent. (provider: intrinio)
        latin_america_sub_group : Optional[str]
            For ETFs that are classified as 'Latin America' in the 'continent' field, this field provides further detail on the type of regional exposure. (provider: intrinio)
        europe_sub_group : Optional[str]
            For ETFs that are classified as 'Europe' in the 'continent' field, this field provides further detail on the type of regional exposure. (provider: intrinio)
        asia_sub_group : Optional[str]
            For ETFs that are classified as 'Asia' in the 'continent' field, this field provides further detail on the type of regional exposure. (provider: intrinio)
        specific_country : Optional[str]
            This field is populated if the ETF provides targeted exposure to a specific country. (provider: intrinio)
        china_listing_location : Optional[str]
            For ETFs that are classified as 'China' in the 'country' field, this field provides further detail on the type of exposure in the underlying securities. (provider: intrinio)
        us_state : Optional[str]
            Takes the value of a US state if the ETF provides targeted exposure to the municipal bonds or equities of companies. (provider: intrinio)
        real_estate : Optional[str]
            For ETFs that provide targeted real estate exposure, this field is populated if the ETF provides targeted exposure to a specific segment of the real estate market. (provider: intrinio)
        fundamental_weighting_type : Optional[str]
            For ETFs that take the value 'Fundamental Weighted' in the 'index_weighting_scheme' field, this field provides detail on the fundamental weighting methodology. (provider: intrinio)
        dividend_weighting_type : Optional[str]
            For ETFs that take the value 'Dividend Weighted' in the 'index_weighting_scheme' field, this field provides detail on the dividend weighting methodology. (provider: intrinio)
        bond_type : Optional[str]
            For ETFs where 'asset_class_type' is 'Bonds', this field provides detail on the type of bonds held in the ETF. (provider: intrinio)
        government_bond_types : Optional[str]
            For bond ETFs that take the value 'Treasury & Government' in 'bond_type', this field provides detail on the exposure. (provider: intrinio)
        municipal_bond_region : Optional[str]
            For bond ETFs that take the value 'Municipal' in 'bond_type', this field provides additional detail on the geographic exposure. (provider: intrinio)
        municipal_vrdo : Optional[bool]
            For bond ETFs that take the value 'Municipal' in 'bond_type', this field identifies those ETFs that specifically provide exposure to Variable Rate Demand Obligations. (provider: intrinio)
        mortgage_bond_types : Optional[str]
            For bond ETFs that take the value 'Mortgage' in 'bond_type', this field provides additional detail on the type of underlying securities. (provider: intrinio)
        bond_tax_status : Optional[str]
            For all US bond ETFs, this field provides additional detail on the tax treatment of the underlying securities. (provider: intrinio)
        credit_quality : Optional[str]
            For all bond ETFs, this field helps to identify if the ETF provides targeted exposure to securities of a specific credit quality range. (provider: intrinio)
        average_maturity : Optional[str]
            For all bond ETFs, this field helps to identify if the ETF provides targeted exposure to securities of a specific maturity range. (provider: intrinio)
        specific_maturity_year : Optional[int]
            For all bond ETFs that take the value 'Specific Maturity Year' in the 'average_maturity' field, this field specifies the calendar year. (provider: intrinio)
        commodity_types : Optional[str]
            For ETFs where 'asset_class_type' is 'Commodities', this field provides detail on the type of commodities held in the ETF. (provider: intrinio)
        energy_type : Optional[str]
            For ETFs where 'commodity_type' is 'Energy', this field provides detail on the type of energy exposure provided by the ETF. (provider: intrinio)
        agricultural_type : Optional[str]
            For ETFs where 'commodity_type' is 'Agricultural', this field provides detail on the type of agricultural exposure provided by the ETF. (provider: intrinio)
        livestock_type : Optional[str]
            For ETFs where 'commodity_type' is 'Livestock', this field provides detail on the type of livestock exposure provided by the ETF. (provider: intrinio)
        metal_type : Optional[str]
            For ETFs where 'commodity_type' is 'Gold & Metals', this field provides detail on the type of exposure provided by the ETF. (provider: intrinio)
        inverse_leveraged : Optional[str]
            This field is populated if the ETF provides inverse or leveraged exposure. (provider: intrinio)
        target_date_multi_asset_type : Optional[str]
            For ETFs where 'asset_class_type' is 'Target Date / MultiAsset', this field provides detail on the type of commodities held in the ETF. (provider: intrinio)
        currency_pair : Optional[str]
            This field is populated if the ETF's strategy involves providing exposure to the movements of a currency or involves hedging currency exposure. (provider: intrinio)
        social_environmental_type : Optional[str]
            This field is populated if the ETF's strategy involves providing exposure to a specific social or environmental theme. (provider: intrinio)
        clean_energy_type : Optional[str]
            This field is populated if the ETF has a value of 'Clean Energy' in the 'social_environmental_type' field. (provider: intrinio)
        dividend_type : Optional[str]
            This field is populated if the ETF has an intended investment objective of holding dividend-oriented stocks as stated in the prospectus. (provider: intrinio)
        regular_dividend_payor_type : Optional[str]
            This field is populated if the ETF has a value of'Dividend - Regular Payors' in the 'dividend_type' field. (provider: intrinio)
        quant_strategies_type : Optional[str]
            This field is populated if the ETF has either an index-linked or active strategy that is based on a proprietary quantitative strategy. (provider: intrinio)
        other_quant_models : Optional[str]
            For ETFs where 'quant_strategies_type' is 'Other Quant Model', this field provides the name of the specific proprietary quant model used as the underlying strategy for the ETF. (provider: intrinio)
        hedge_fund_type : Optional[str]
            For ETFs where 'other_asset_types' is 'Hedge Fund Replication', this field provides detail on the type of hedge fund replication strategy. (provider: intrinio)
        excludes_financials : Optional[bool]
            For equity ETFs, identifies those ETFs where the underlying fund holdings will not hold financials stocks, based on the funds intended objective. (provider: intrinio)
        excludes_technology : Optional[bool]
            For equity ETFs, identifies those ETFs where the underlying fund holdings will not hold technology stocks, based on the funds intended objective. (provider: intrinio)
        holds_only_nyse_stocks : Optional[bool]
            If true, the ETF is an equity ETF and holds only stocks listed on NYSE. (provider: intrinio)
        holds_only_nasdaq_stocks : Optional[bool]
            If true, the ETF is an equity ETF and holds only stocks listed on Nasdaq. (provider: intrinio)
        holds_mlp : Optional[bool]
            If true, the ETF's investment objective explicitly specifies that it holds MLPs as an intended part of its investment strategy. (provider: intrinio)
        holds_preferred_stock : Optional[bool]
            If true, the ETF's investment objective explicitly specifies that it holds preferred stock as an intended part of its investment strategy. (provider: intrinio)
        holds_closed_end_funds : Optional[bool]
            If true, the ETF's investment objective explicitly specifies that it holds closed end funds as an intended part of its investment strategy. (provider: intrinio)
        holds_adr : Optional[bool]
            If true, he ETF's investment objective explicitly specifies that it holds American Depositary Receipts (ADRs) as an intended part of its investment strategy. (provider: intrinio)
        laddered : Optional[bool]
            For bond ETFs, this field identifies those ETFs that specifically hold bonds in a laddered structure, where the bonds are scheduled to mature in an annual, sequential structure. (provider: intrinio)
        zero_coupon : Optional[bool]
            For bond ETFs, this field identifies those ETFs that specifically hold zero coupon Treasury Bills. (provider: intrinio)
        floating_rate : Optional[bool]
            For bond ETFs, this field identifies those ETFs that specifically hold floating rate bonds. (provider: intrinio)
        build_america_bonds : Optional[bool]
            For municipal bond ETFs, this field identifies those ETFs that specifically hold Build America Bonds. (provider: intrinio)
        dynamic_futures_roll : Optional[bool]
            If the product holds futures contracts, this field identifies those products where the roll strategy is dynamic (rather than entirely rules based), so as to minimize roll costs. (provider: intrinio)
        currency_hedged : Optional[bool]
            This field is populated if the ETF's strategy involves hedging currency exposure. (provider: intrinio)
        includes_short_exposure : Optional[bool]
            This field is populated if the ETF has short exposure in any of its holdings e.g. in a long/short or inverse ETF. (provider: intrinio)
        ucits : Optional[bool]
            If true, the Exchange Traded Product (ETP) is Undertakings for the Collective Investment in Transferable Securities (UCITS) compliant (provider: intrinio)
        registered_countries : Optional[str]
            The list of countries where the ETF is legally registered for sale. This may differ from where the ETF is domiciled or traded, particularly in Europe. (provider: intrinio)
        issuer_country : Optional[str]
            2 letter ISO country code for the country where the issuer is located. (provider: intrinio)
        listing_country : Optional[str]
            2 letter ISO country code for the country of the primary listing. (provider: intrinio)
        listing_region : Optional[str]
            Geographic region in the country of the primary listing falls. (provider: intrinio)
        bond_currency_denomination : Optional[str]
            For all bond ETFs, this field provides additional detail on the currency denomination of the underlying securities. (provider: intrinio)
        base_currency : Optional[str]
            Base currency in which NAV is reported. (provider: intrinio)
        listing_currency : Optional[str]
            Listing currency of the Exchange Traded Product (ETP) in which it is traded. Reported using the 3-digit ISO currency code. (provider: intrinio)
        number_of_holdings : Optional[int]
            The number of holdings in the ETF. (provider: intrinio)
        month_end_assets : Optional[float]
            Net assets in millions of dollars as of the most recent month end. (provider: intrinio)
        net_expense_ratio : Optional[float]
            Gross expense net of Fee Waivers, as a percentage of net assets as published by the ETF issuer. (provider: intrinio)
        etf_portfolio_turnover : Optional[float]
            The percentage of positions turned over in the last 12 months. (provider: intrinio)
        fund_type : Optional[str]
            The legal type of fund. (provider: yfinance)
        category : Optional[str]
            The fund category. (provider: yfinance)
        exchange_timezone : Optional[str]
            The timezone of the exchange. (provider: yfinance)
        currency : Optional[str]
            The currency in which the fund is listed. (provider: yfinance)
        nav_price : Optional[float]
            The net asset value per unit of the fund. (provider: yfinance)
        total_assets : Optional[int]
            The total value of assets held by the fund. (provider: yfinance)
        trailing_pe : Optional[float]
            The trailing twelve month P/E ratio of the fund's assets. (provider: yfinance)
        dividend_yield : Optional[float]
            The dividend yield of the fund, as a normalized percent. (provider: yfinance)
        dividend_rate_ttm : Optional[float]
            The trailing twelve month annual dividend rate of the fund, in currency units. (provider: yfinance)
        dividend_yield_ttm : Optional[float]
            The trailing twelve month annual dividend yield of the fund, as a normalized percent. (provider: yfinance)
        year_high : Optional[float]
            The fifty-two week high price. (provider: yfinance)
        year_low : Optional[float]
            The fifty-two week low price. (provider: yfinance)
        ma_50d : Optional[float]
            50-day moving average price. (provider: yfinance)
        ma_200d : Optional[float]
            200-day moving average price. (provider: yfinance)
        return_ytd : Optional[float]
            The year-to-date return of the fund, as a normalized percent. (provider: yfinance)
        return_3y_avg : Optional[float]
            The three year average return of the fund, as a normalized percent. (provider: yfinance)
        return_5y_avg : Optional[float]
            The five year average return of the fund, as a normalized percent. (provider: yfinance)
        beta_3y_avg : Optional[float]
            The three year average beta of the fund. (provider: yfinance)
        volume_avg : Optional[float]
            The average daily trading volume of the fund. (provider: yfinance)
        volume_avg_10d : Optional[float]
            The average daily trading volume of the fund over the past ten days. (provider: yfinance)
        bid : Optional[float]
            The current bid price. (provider: yfinance)
        bid_size : Optional[float]
            The current bid size. (provider: yfinance)
        ask : Optional[float]
            The current ask price. (provider: yfinance)
        ask_size : Optional[float]
            The current ask size. (provider: yfinance)
        open : Optional[float]
            The open price of the most recent trading session. (provider: yfinance)
        high : Optional[float]
            The highest price of the most recent trading session. (provider: yfinance)
        low : Optional[float]
            The lowest price of the most recent trading session. (provider: yfinance)
        volume : Optional[int]
            The trading volume of the most recent trading session. (provider: yfinance)
        prev_close : Optional[float]
            The previous closing price. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.info(symbol='SPY', provider='fmp')
        >>> # This function accepts multiple tickers.
        >>> obb.etf.info(symbol='SPY,IWM,QQQ,DJIA', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/info",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/info",
                        ("fmp", "intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "multiple_items_allowed": ["fmp", "intrinio", "yfinance"]
                    }
                },
            )
        )

    @exception_handler
    @validate
    def price_performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp", "intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Price performance as a return, over different periods.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio.
        provider : Optional[Literal['fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        return_type : Literal['trailing', 'calendar']
            The type of returns to return, a trailing or calendar window. (provider: intrinio)
        adjustment : Literal['splits_only', 'splits_and_dividends']
            The adjustment factor, 'splits_only' will return pure price performance. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[EtfPricePerformance]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EtfPricePerformance
        -------------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
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
        two_year : Optional[float]
            Two-year return.
        three_year : Optional[float]
            Three-year return.
        four_year : Optional[float]
            Four-year
        five_year : Optional[float]
            Five-year return.
        ten_year : Optional[float]
            Ten-year return.
        max : Optional[float]
            Return from the beginning of the time series.
        max_annualized : Optional[float]
            Annualized rate of return from inception. (provider: intrinio)
        volatility_one_year : Optional[float]
            Trailing one-year annualized volatility. (provider: intrinio)
        volatility_three_year : Optional[float]
            Trailing three-year annualized volatility. (provider: intrinio)
        volatility_five_year : Optional[float]
            Trailing five-year annualized volatility. (provider: intrinio)
        volume : Optional[int]
            The trading volume. (provider: intrinio)
        volume_avg_30 : Optional[float]
            The one-month average daily volume. (provider: intrinio)
        volume_avg_90 : Optional[float]
            The three-month average daily volume. (provider: intrinio)
        volume_avg_180 : Optional[float]
            The six-month average daily volume. (provider: intrinio)
        beta : Optional[float]
            Beta compared to the S&P 500. (provider: intrinio)
        nav : Optional[float]
            Net asset value per share. (provider: intrinio)
        year_high : Optional[float]
            The 52-week high price. (provider: intrinio)
        year_low : Optional[float]
            The 52-week low price. (provider: intrinio)
        market_cap : Optional[float]
            The market capitalization. (provider: intrinio)
        shares_outstanding : Optional[int]
            The number of shares outstanding. (provider: intrinio)
        updated : Optional[date]
            The date of the data. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.price_performance(symbol='QQQ', provider='fmp')
        >>> obb.etf.price_performance(symbol='SPY,QQQ,IWM,DJIA', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/price_performance",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/price_performance",
                        ("fmp", "intrinio"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["fmp", "intrinio"]}},
            )
        )

    @exception_handler
    @validate
    def search(
        self,
        query: Annotated[Optional[str], OpenBBField(description="Search query.")] = "",
        provider: Annotated[
            Optional[Literal["fmp", "intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Search for ETFs.

        An empty query returns the full list of ETFs from the provider.


        Parameters
        ----------
        query : Optional[str]
            Search query.
        provider : Optional[Literal['fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        exchange : Optional[Union[Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT'], Literal['xnas', 'arcx', 'bats', 'xnys', 'bvmf', 'xshg', 'xshe', 'xhkg', 'xbom', 'xnse', 'xidx', 'tase', 'xkrx', 'xkls', 'xmex', 'xses', 'roco', 'xtai', 'xbkk', 'xist']]]
            The exchange code the ETF trades on. (provider: fmp);
            Target a specific exchange by providing the MIC code. (provider: intrinio)
        is_active : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[EtfSearch]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
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
            The exchange code the ETF trades on. (provider: fmp);
            The exchange MIC code. (provider: intrinio)
        exchange_name : Optional[str]
            The full name of the exchange the ETF trades on. (provider: fmp)
        country : Optional[str]
            The country the ETF is registered in. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        figi_ticker : Optional[str]
            The OpenFIGI ticker. (provider: intrinio)
        ric : Optional[str]
            The Reuters Instrument Code. (provider: intrinio)
        isin : Optional[str]
            The International Securities Identification Number. (provider: intrinio)
        sedol : Optional[str]
            The Stock Exchange Daily Official List. (provider: intrinio)
        intrinio_id : Optional[str]
            The unique Intrinio ID for the security. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> # An empty query returns the full list of ETFs from the provider.
        >>> obb.etf.search(provider='fmp')
        >>> # The query will return results from text-based fields containing the term.
        >>> obb.etf.search(query='commercial real estate', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/search",
                        ("fmp", "intrinio"),
                    )
                },
                standard_params={
                    "query": query,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def sectors(
        self,
        symbol: Annotated[
            str, OpenBBField(description="Symbol to get data for. (ETF)")
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
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
            extra : Dict[str, Any]
                Extra info.

        EtfSectors
        ----------
        sector : str
            Sector of exposure.
        weight : Optional[float]
            Exposure of the ETF to the sector in normalized percentage points.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.sectors(symbol='SPY', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/sectors",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/sectors",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
