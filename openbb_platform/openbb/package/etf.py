### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_etf(Container):
    """/etf
    countries
    /discovery
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
            OpenBBCustomParameter(
                description="Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx."
            ),
        ],
        provider: Optional[Literal["fmp", "tmx"]] = None,
        **kwargs
    ) -> OBBject:
        """ETF Country weighting.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx.
        provider : Optional[Literal['fmp', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        use_cache : bool
            Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfCountries]
                Serializable results.
            provider : Optional[Literal['fmp', 'tmx']]
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
        >>> obb.etf.countries(symbol='VT')
        """  # noqa: E501

        return self._run(
            "/etf/countries",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/countries",
                        ("fmp", "tmx"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["fmp", "tmx"]}},
            )
        )

    @property
    def discovery(self):
        # pylint: disable=import-outside-toplevel
        from . import etf_discovery

        return etf_discovery.ROUTER_etf_discovery(command_runner=self._command_runner)

    @exception_handler
    @validate
    def equity_exposure(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. (Stock) Multiple items allowed for provider(s): fmp."
            ),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the exposure to ETFs for a specific stock.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. (Stock) Multiple items allowed for provider(s): fmp.
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
        shares : Optional[int]
            The number of shares held in the ETF.
        weight : Optional[float]
            The weight of the equity in the ETF, as a normalized percent.
        market_value : Optional[Union[int, float]]
            The market value of the equity position in the ETF.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.equity_exposure(symbol='MSFT')
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
                extra_info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, yfinance."
            ),
        ],
        interval: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Time interval of the data to return."),
        ] = "1d",
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
        provider: Optional[
            Literal[
                "alpha_vantage",
                "cboe",
                "fmp",
                "intrinio",
                "polygon",
                "tiingo",
                "tmx",
                "yfinance",
            ]
        ] = None,
        **kwargs
    ) -> OBBject:
        """ETF Historical Market Price.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, yfinance.
        interval : Optional[str]
            Time interval of the data to return.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'pol...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'alpha_vantage' if there is
            no default.
        adjustment : Union[Literal['splits_only', 'splits_and_dividends', 'unadjusted'], Literal['splits_only', 'unadjusted'], Literal['splits_only', 'splits_and_dividends']]
            The adjustment factor to apply. 'splits_only' is not supported for intraday data. (provider: alpha_vantage);
            The adjustment factor to apply. Default is splits only. (provider: polygon);
            The adjustment factor to apply. Only valid for daily data. (provider: tmx);
            The adjustment factor to apply. Default is splits only. (provider: yfinance)
        extended_hours : Optional[bool]
            Include Pre and Post market data. (provider: alpha_vantage, polygon, yfinance)
        adjusted : bool
            This field is deprecated (4.1.5) and will be removed in a future version. Use 'adjustment' set as 'splits_and_dividends' instead. (provider: alpha_vantage, yfinance)
        use_cache : bool
            When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. (provider: cboe)
        start_time : Optional[datetime.time]
            Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        end_time : Optional[datetime.time]
            Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        timezone : Optional[str]
            Timezone of the data, in the IANA format (Continent/City). (provider: intrinio)
        source : Literal['realtime', 'delayed', 'nasdaq_basic']
            The source of the data. (provider: intrinio)
        sort : Literal['asc', 'desc']
            Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date. (provider: polygon)
        limit : int
            The number of data entries to return. (provider: polygon)
        include_actions : bool
            Include dividends and stock splits in results. (provider: yfinance)
        prepost : bool
            This field is deprecated (4.1.5) and will be removed in a future version. Use 'extended_hours' as True instead. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EtfHistorical]
                Serializable results.
            provider : Optional[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'tmx', 'yfinance']]
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
        adj_close : Optional[Union[Annotated[float, Gt(gt=0)], float]]
            The adjusted close price. (provider: alpha_vantage, fmp, intrinio, tiingo)
        dividend : Optional[Union[Annotated[float, Ge(ge=0)], float]]
            Dividend amount, if a dividend was paid. (provider: alpha_vantage, intrinio, tiingo, yfinance)
        split_ratio : Optional[Union[Annotated[float, Ge(ge=0)], float]]
            Split coefficient, if a split occurred. (provider: alpha_vantage);
            Ratio of the equity split, if a split occurred. (provider: intrinio);
            Ratio of the equity split, if a split occurred. (provider: tiingo);
            Ratio of the equity split, if a split occurred. (provider: yfinance)
        calls_volume : Optional[int]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[int]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[int]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price from the previous close. (provider: fmp);
            Change in the price of the symbol from the previous day. (provider: intrinio);
            Change in price. (provider: tmx)
        change_percent : Optional[float]
            Change in the price from the previous close, as a normalized percent. (provider: fmp);
            Percent change in the price of the symbol from the previous day. (provider: intrinio);
            Change in price, as a normalized percentage. (provider: tmx)
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
        close_time : Optional[datetime]
            The timestamp that represents the end of the interval span. (provider: intrinio)
        interval : Optional[str]
            The data time frequency. (provider: intrinio)
        intra_period : Optional[bool]
            If true, the equity price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period (provider: intrinio)
        transactions : Optional[Union[Annotated[int, Gt(gt=0)], int]]
            Number of transactions for the symbol in the time period. (provider: polygon);
            Total number of transactions recorded. (provider: tmx)
        transactions_value : Optional[float]
            Nominal value of recorded transactions. (provider: tmx)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.historical(symbol='SPY')
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
                        (
                            "alpha_vantage",
                            "cboe",
                            "fmp",
                            "intrinio",
                            "polygon",
                            "tiingo",
                            "tmx",
                            "yfinance",
                        ),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "interval": interval,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {
                        "multiple_items_allowed": [
                            "alpha_vantage",
                            "cboe",
                            "fmp",
                            "polygon",
                            "tiingo",
                            "tmx",
                            "yfinance",
                        ]
                    }
                },
            )
        )

    @exception_handler
    @validate
    def holdings(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for. (ETF)")
        ],
        provider: Optional[Literal["fmp", "sec", "tmx"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the holdings for an individual ETF.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp', 'sec', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        date : Optional[Union[str, datetime.date]]
            A specific date to get data for. Entering a date will attempt to return the NPORT-P filing for the entered date. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. (provider: fmp);
            A specific date to get data for.  The date represents the period ending. The date entered will return the closest filing. (provider: sec)
        cik : Optional[str]
            The CIK of the filing entity. Overrides symbol. (provider: fmp)
        use_cache : bool
            Whether or not to use cache for the request. (provider: sec);
            Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfHoldings]
                Serializable results.
            provider : Optional[Literal['fmp', 'sec', 'tmx']]
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
            The ISIN of the holding. (provider: fmp, sec)
        balance : Optional[int]
            The balance of the holding, in shares or units. (provider: fmp);
            The balance of the holding. (provider: sec)
        units : Optional[Union[str, float]]
            The type of units. (provider: fmp);
            The units of the holding. (provider: sec)
        currency : Optional[str]
            The currency of the holding. (provider: fmp, sec, tmx)
        value : Optional[float]
            The value of the holding, in dollars. (provider: fmp, sec)
        weight : Optional[float]
            The weight of the holding, as a normalized percent. (provider: fmp);
            The weight of the holding in ETF in %. (provider: sec);
            The weight of the asset in the portfolio, as a normalized percentage. (provider: tmx)
        payoff_profile : Optional[str]
            The payoff profile of the holding. (provider: fmp, sec)
        asset_category : Optional[str]
            The asset category of the holding. (provider: fmp, sec)
        issuer_category : Optional[str]
            The issuer category of the holding. (provider: fmp, sec)
        country : Optional[str]
            The country of the holding. (provider: fmp, sec, tmx)
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
            The date the data was updated. (provider: fmp)
        other_id : Optional[str]
            Internal identifier for the holding. (provider: sec)
        loan_value : Optional[float]
            The loan value of the holding. (provider: sec)
        issuer_conditional : Optional[str]
            The issuer conditions of the holding. (provider: sec)
        asset_conditional : Optional[str]
            The asset conditions of the holding. (provider: sec)
        maturity_date : Optional[date]
            The maturity date of the debt security. (provider: sec)
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
            The type of rate for reveivable portion of the swap. (provider: sec)
        receive_currency : Optional[str]
            The receive currency of the swap. (provider: sec)
        upfront_receive : Optional[float]
            The upfront amount received of the swap. (provider: sec)
        floating_rate_index_rec : Optional[str]
            The floating rate index for reveivable portion of the swap. (provider: sec)
        floating_rate_spread_rec : Optional[float]
            The floating rate spread for reveivable portion of the swap. (provider: sec)
        rate_tenor_rec : Optional[str]
            The rate tenor for reveivable portion of the swap. (provider: sec)
        rate_tenor_unit_rec : Optional[Union[int, str]]
            The rate tenor unit for reveivable portion of the swap. (provider: sec)
        reset_date_rec : Optional[str]
            The reset date for reveivable portion of the swap. (provider: sec)
        reset_date_unit_rec : Optional[Union[int, str]]
            The reset date unit for reveivable portion of the swap. (provider: sec)
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
        rate_tenor_unit_pmnt : Optional[Union[int, str]]
            The rate tenor unit for payment portion of the swap. (provider: sec)
        reset_date_pmnt : Optional[str]
            The reset date for payment portion of the swap. (provider: sec)
        reset_date_unit_pmnt : Optional[Union[int, str]]
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
        shares : Optional[Union[int, str]]
            The value of the assets under management. (provider: tmx)
        market_value : Optional[Union[str, float]]
            The market value of the holding. (provider: tmx)
        share_percentage : Optional[float]
            The share percentage of the holding, as a normalized percentage. (provider: tmx)
        share_change : Optional[Union[str, float]]
            The change in shares of the holding. (provider: tmx)
        exchange : Optional[str]
            The exchange code of the holding. (provider: tmx)
        type_id : Optional[str]
            The holding type ID of the asset. (provider: tmx)
        fund_id : Optional[str]
            The fund ID of the asset. (provider: tmx)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.holdings(symbol='XLK')
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
                        ("fmp", "sec", "tmx"),
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
            str, OpenBBCustomParameter(description="Symbol to get data for. (ETF)")
        ],
        provider: Optional[Literal["fmp"]] = None,
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
        >>> obb.etf.holdings_date(symbol='XLK')
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
    def holdings_performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp."
            ),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the recent price performance of each ticker held in the ETF.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp.
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

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.holdings_performance(symbol='XLK')
        """  # noqa: E501

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
                extra_info={"symbol": {"multiple_items_allowed": ["finviz", "fmp"]}},
            )
        )

    @exception_handler
    @validate
    def info(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx, yfinance."
            ),
        ],
        provider: Optional[Literal["fmp", "tmx", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """ETF Information Overview.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx, yfinance.
        provider : Optional[Literal['fmp', 'tmx', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        use_cache : bool
            Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfInfo]
                Serializable results.
            provider : Optional[Literal['fmp', 'tmx', 'yfinance']]
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
            The issuer of the ETF. (provider: tmx)
        cusip : Optional[str]
            CUSIP of the ETF. (provider: fmp)
        isin : Optional[str]
            ISIN of the ETF. (provider: fmp)
        domicile : Optional[str]
            Domicile of the ETF. (provider: fmp)
        asset_class : Optional[str]
            Asset class of the ETF. (provider: fmp)
        aum : Optional[float]
            Assets under management. (provider: fmp);
            The AUM of the ETF. (provider: tmx)
        nav : Optional[float]
            Net asset value of the ETF. (provider: fmp)
        nav_currency : Optional[str]
            Currency of the ETF's net asset value. (provider: fmp)
        expense_ratio : Optional[float]
            The expense ratio, as a normalized percent. (provider: fmp)
        holdings_count : Optional[int]
            Number of holdings. (provider: fmp)
        avg_volume : Optional[Union[float, int]]
            Average daily trading volume. (provider: fmp);
            The average daily volume of the ETF. (provider: tmx)
        website : Optional[str]
            Website of the issuer. (provider: fmp);
            The website of the ETF. (provider: tmx)
        investment_style : Optional[str]
            The investment style of the ETF. (provider: tmx)
        esg : Optional[bool]
            Whether the ETF qualifies as an ESG fund. (provider: tmx)
        currency : Optional[str]
            The currency of the ETF. (provider: tmx);
            The currency in which the fund is listed. (provider: yfinance)
        unit_price : Optional[float]
            The unit price of the ETF. (provider: tmx)
        close : Optional[float]
            The closing price of the ETF. (provider: tmx)
        prev_close : Optional[float]
            The previous closing price of the ETF. (provider: tmx, yfinance)
        return_1m : Optional[float]
            The one-month return of the ETF, as a normalized percent (provider: tmx)
        return_3m : Optional[float]
            The three-month return of the ETF, as a normalized percent. (provider: tmx)
        return_6m : Optional[float]
            The six-month return of the ETF, as a normalized percent. (provider: tmx)
        return_ytd : Optional[float]
            The year-to-date return of the ETF, as a normalized percent. (provider: tmx, yfinance)
        return_1y : Optional[float]
            The one-year return of the ETF, as a normalized percent. (provider: tmx)
        return_3y : Optional[float]
            The three-year return of the ETF, as a normalized percent. (provider: tmx)
        return_5y : Optional[float]
            The five-year return of the ETF, as a normalized percent. (provider: tmx)
        return_10y : Optional[float]
            The ten-year return of the ETF, as a normalized percent. (provider: tmx)
        return_from_inception : Optional[float]
            The return from inception of the ETF, as a normalized percent. (provider: tmx)
        avg_volume_30d : Optional[int]
            The 30-day average volume of the ETF. (provider: tmx)
        pe_ratio : Optional[float]
            The price-to-earnings ratio of the ETF. (provider: tmx)
        pb_ratio : Optional[float]
            The price-to-book ratio of the ETF. (provider: tmx)
        management_fee : Optional[float]
            The management fee of the ETF, as a normalized percent. (provider: tmx)
        mer : Optional[float]
            The management expense ratio of the ETF, as a normalized percent. (provider: tmx)
        distribution_yield : Optional[float]
            The distribution yield of the ETF, as a normalized percent. (provider: tmx)
        dividend_frequency : Optional[str]
            The dividend payment frequency of the ETF. (provider: tmx)
        fund_type : Optional[str]
            The legal type of fund. (provider: yfinance)
        fund_family : Optional[str]
            The fund family. (provider: yfinance)
        category : Optional[str]
            The fund category. (provider: yfinance)
        exchange : Optional[str]
            The exchange the fund is listed on. (provider: yfinance)
        exchange_timezone : Optional[str]
            The timezone of the exchange. (provider: yfinance)
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

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.info(symbol='SPY')
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
                        ("fmp", "tmx", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {"multiple_items_allowed": ["fmp", "tmx", "yfinance"]}
                },
            )
        )

    @exception_handler
    @validate
    def price_performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp."
            ),
        ],
        provider: Optional[Literal["finviz", "fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Price performance as a return, over different periods. This is a proxy for `equity.price.performance`.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp.
        provider : Optional[Literal['finviz', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'finviz' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[PricePerformance]
                Serializable results.
            provider : Optional[Literal['finviz', 'fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
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
        volatility_week : Optional[float]
            One-week realized volatility, as a normalized percent. (provider: finviz)
        volatility_month : Optional[float]
            One-month realized volatility, as a normalized percent. (provider: finviz)
        price : Optional[float]
            Last Price. (provider: finviz)
        volume : Optional[float]
            Current volume. (provider: finviz)
        average_volume : Optional[float]
            Average daily volume. (provider: finviz)
        relative_volume : Optional[float]
            Relative volume as a ratio of current volume to average volume. (provider: finviz)
        analyst_recommendation : Optional[float]
            The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell. (provider: finviz)
        symbol : Optional[str]
            The ticker symbol. (provider: finviz, fmp)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.price_performance(symbol='QQQ')
        >>> obb.etf.price_performance(symbol='SPY,QQQ,IWM,DJIA', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/etf/price_performance",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/price_performance",
                        ("finviz", "fmp"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["finviz", "fmp"]}},
            )
        )

    @exception_handler
    @validate
    def search(
        self,
        query: Annotated[
            Optional[str], OpenBBCustomParameter(description="Search query.")
        ] = "",
        provider: Optional[Literal["fmp", "tmx"]] = None,
        **kwargs
    ) -> OBBject:
        """Search for ETFs.

        An empty query returns the full list of ETFs from the provider.


        Parameters
        ----------
        query : Optional[str]
            Search query.
        provider : Optional[Literal['fmp', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        exchange : Optional[Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT']]
            The exchange code the ETF trades on. (provider: fmp)
        is_active : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        div_freq : Optional[Literal['monthly', 'annually', 'quarterly']]
            The dividend payment frequency. (provider: tmx)
        sort_by : Optional[Literal['nav', 'return_1m', 'return_3m', 'return_6m', 'return_1y', 'return_3y', 'return_ytd', 'beta_1y', 'volume_avg_daily', 'management_fee', 'distribution_yield', 'pb_ratio', 'pe_ratio']]
            The column to sort by. (provider: tmx)
        use_cache : bool
            Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfSearch]
                Serializable results.
            provider : Optional[Literal['fmp', 'tmx']]
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
            The exchange code the ETF trades on. (provider: fmp)
        exchange_name : Optional[str]
            The full name of the exchange the ETF trades on. (provider: fmp)
        country : Optional[str]
            The country the ETF is registered in. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        short_name : Optional[str]
            The short name of the ETF. (provider: tmx)
        inception_date : Optional[str]
            The inception date of the ETF. (provider: tmx)
        issuer : Optional[str]
            The issuer of the ETF. (provider: tmx)
        investment_style : Optional[str]
            The investment style of the ETF. (provider: tmx)
        esg : Optional[bool]
            Whether the ETF qualifies as an ESG fund. (provider: tmx)
        currency : Optional[str]
            The currency of the ETF. (provider: tmx)
        unit_price : Optional[float]
            The unit price of the ETF. (provider: tmx)
        close : Optional[float]
            The closing price of the ETF. (provider: tmx)
        prev_close : Optional[float]
            The previous closing price of the ETF. (provider: tmx)
        return_1m : Optional[float]
            The one-month return of the ETF, as a normalized percent. (provider: tmx)
        return_3m : Optional[float]
            The three-month return of the ETF, as a normalized percent. (provider: tmx)
        return_6m : Optional[float]
            The six-month return of the ETF, as a normalized percent. (provider: tmx)
        return_ytd : Optional[float]
            The year-to-date return of the ETF, as a normalized percent. (provider: tmx)
        return_1y : Optional[float]
            The one-year return of the ETF, as a normalized percent. (provider: tmx)
        beta_1y : Optional[float]
            The one-year beta of the ETF, as a normalized percent. (provider: tmx)
        return_3y : Optional[float]
            The three-year return of the ETF, as a normalized percent. (provider: tmx)
        beta_3y : Optional[float]
            The three-year beta of the ETF, as a normalized percent. (provider: tmx)
        return_5y : Optional[float]
            The five-year return of the ETF, as a normalized percent. (provider: tmx)
        beta_5y : Optional[float]
            The five-year beta of the ETF, as a normalized percent. (provider: tmx)
        return_10y : Optional[float]
            The ten-year return of the ETF, as a normalized percent. (provider: tmx)
        beta_10y : Optional[float]
            The ten-year beta of the ETF. (provider: tmx)
        beta_15y : Optional[float]
            The fifteen-year beta of the ETF. (provider: tmx)
        return_from_inception : Optional[float]
            The return from inception of the ETF, as a normalized percent. (provider: tmx)
        avg_volume : Optional[int]
            The average daily volume of the ETF. (provider: tmx)
        avg_volume_30d : Optional[int]
            The 30-day average volume of the ETF. (provider: tmx)
        aum : Optional[float]
            The AUM of the ETF. (provider: tmx)
        pe_ratio : Optional[float]
            The price-to-earnings ratio of the ETF. (provider: tmx)
        pb_ratio : Optional[float]
            The price-to-book ratio of the ETF. (provider: tmx)
        management_fee : Optional[float]
            The management fee of the ETF, as a normalized percent. (provider: tmx)
        mer : Optional[float]
            The management expense ratio of the ETF, as a normalized percent. (provider: tmx)
        distribution_yield : Optional[float]
            The distribution yield of the ETF, as a normalized percent. (provider: tmx)
        dividend_frequency : Optional[str]
            The dividend payment frequency of the ETF. (provider: tmx)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.etf.search()
        >>> # An empty query returns the full list of ETFs from the provider.
        >>> obb.etf.search()
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
                        ("fmp", "tmx"),
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
            str, OpenBBCustomParameter(description="Symbol to get data for. (ETF)")
        ],
        provider: Optional[Literal["fmp", "tmx"]] = None,
        **kwargs
    ) -> OBBject:
        """ETF Sector weighting.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. (ETF)
        provider : Optional[Literal['fmp', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        use_cache : bool
            Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfSectors]
                Serializable results.
            provider : Optional[Literal['fmp', 'tmx']]
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
        >>> obb.etf.sectors(symbol='SPY')
        """  # noqa: E501

        return self._run(
            "/etf/sectors",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/etf/sectors",
                        ("fmp", "tmx"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
