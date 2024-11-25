### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_fixedincome_rate(Container):
    """/fixedincome/rate
    ameribor
    dpcredit
    ecb
    effr
    effr_forecast
    estr
    iorb
    overnight_bank_funding
    sofr
    sonia
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def ameribor(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """AMERIBOR.

        AMERIBOR (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
        short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
        American Financial Exchange (AFX).


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        maturity : Union[Literal['all', 'overnight', 'average_30d', 'average_90d', 'term_30d', 'term_90d'], str]
            Period of AMERIBOR rate. Multiple comma separated items allowed. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
                    wef = Weekly, Ending Friday
                    weth = Weekly, Ending Thursday
                    wew = Weekly, Ending Wednesday
                    wetu = Weekly, Ending Tuesday
                    wem = Weekly, Ending Monday
                    wesu = Weekly, Ending Sunday
                    wesa = Weekly, Ending Saturday
                    bwew = Biweekly, Ending Wednesday
                    bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]

                A key that indicates the aggregation method used for frequency aggregation.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[Ameribor]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        Ameribor
        --------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        maturity : str
            Maturity length of the item.
        rate : float
            Interest rate.
        title : Optional[str]
            Title of the series.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.ameribor(provider='fred')
        >>> # The change from one year ago is applied with the transform parameter.
        >>> obb.fixedincome.rate.ameribor(maturity='all', transform='pc1', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/ameribor",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.ameribor",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "maturity": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "all",
                                "overnight",
                                "average_30d",
                                "average_90d",
                                "term_30d",
                                "term_90d",
                            ],
                        }
                    }
                },
            )
        )

    @exception_handler
    @validate
    def dpcredit(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Discount Window Primary Credit Rate.

        A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
        The rates central banks charge are set to stabilize the economy.
        In the United States, the Federal Reserve System's Board of Governors set the bank rate,
        also known as the discount rate.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        parameter : Literal['daily_excl_weekend', 'monthly', 'weekly', 'daily', 'annual']
            FRED series ID of DWPCR data. (provider: fred)

        Returns
        -------
        OBBject
            results : List[DiscountWindowPrimaryCreditRate]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        DiscountWindowPrimaryCreditRate
        -------------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            Discount Window Primary Credit Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.dpcredit(provider='fred')
        >>> obb.fixedincome.rate.dpcredit(start_date='2023-02-01', end_date='2023-05-01', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/dpcredit",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.dpcredit",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def ecb(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        interest_rate_type: Annotated[
            Literal["deposit", "lending", "refinancing"],
            OpenBBField(description="The type of interest rate."),
        ] = "lending",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """European Central Bank Interest Rates.

        The Governing Council of the ECB sets the key interest rates for the euro area:

        - The interest rate on the main refinancing operations (MRO), which provide
        the bulk of liquidity to the banking system.
        - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
        - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        interest_rate_type : Literal['deposit', 'lending', 'refinancing']
            The type of interest rate.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.

        Returns
        -------
        OBBject
            results : List[EuropeanCentralBankInterestRates]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EuropeanCentralBankInterestRates
        --------------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            European Central Bank Interest Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.ecb(provider='fred')
        >>> obb.fixedincome.rate.ecb(interest_rate_type='refinancing', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/ecb",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.ecb",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "interest_rate_type": interest_rate_type,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def effr(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["federal_reserve", "fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Fed Funds Rate.

        Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
        domestic banks to borrow money. The rates central banks charge are set to stabilize the economy.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred.
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
                    wef = Weekly, Ending Friday
                    weth = Weekly, Ending Thursday
                    wew = Weekly, Ending Wednesday
                    wetu = Weekly, Ending Tuesday
                    wem = Weekly, Ending Monday
                    wesu = Weekly, Ending Sunday
                    wesa = Weekly, Ending Saturday
                    bwew = Biweekly, Ending Wednesday
                    bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]

                A key that indicates the aggregation method used for frequency aggregation.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)
        effr_only : bool
            Return data without quantiles, target ranges, and volume. (provider: fred)

        Returns
        -------
        OBBject
            results : List[FederalFundsRate]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FederalFundsRate
        ----------------
        date : date
            The date of the data.
        rate : float
            Effective federal funds rate.
        target_range_upper : Optional[float]
            Upper bound of the target range.
        target_range_lower : Optional[float]
            Lower bound of the target range.
        percentile_1 : Optional[float]
            1st percentile of the distribution.
        percentile_25 : Optional[float]
            25th percentile of the distribution.
        percentile_75 : Optional[float]
            75th percentile of the distribution.
        percentile_99 : Optional[float]
            99th percentile of the distribution.
        volume : Optional[float]
            The trading volume.The notional volume of transactions (Billions of $).
        intraday_low : Optional[float]
            Intraday low. This field is only present for data before 2016. (provider: federal_reserve)
        intraday_high : Optional[float]
            Intraday high. This field is only present for data before 2016. (provider: federal_reserve)
        standard_deviation : Optional[float]
            Standard deviation. This field is only present for data before 2016. (provider: federal_reserve)
        revision_indicator : Optional[str]
            Indicates a revision of the data for that date. (provider: federal_reserve)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.effr(provider='fred')
        >>> obb.fixedincome.rate.effr(effr_only=True, provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/effr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.effr",
                        ("federal_reserve", "fred"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def effr_forecast(
        self,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Fed Funds Rate Projections.

        The projections for the federal funds rate are the value of the midpoint of the
        projected appropriate target range for the federal funds rate or the projected
        appropriate target level for the federal funds rate at the end of the specified
        calendar year or over the longer run.


        Parameters
        ----------
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        long_run : bool
            Flag to show long run projections (provider: fred)

        Returns
        -------
        OBBject
            results : List[PROJECTIONS]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PROJECTIONS
        -----------
        date : date
            The date of the data.
        range_high : Optional[float]
            High projection of rates.
        central_tendency_high : Optional[float]
            Central tendency of high projection of rates.
        median : Optional[float]
            Median projection of rates.
        range_midpoint : Optional[float]
            Midpoint projection of rates.
        central_tendency_midpoint : Optional[float]
            Central tendency of midpoint projection of rates.
        range_low : Optional[float]
            Low projection of rates.
        central_tendency_low : Optional[float]
            Central tendency of low projection of rates.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.effr_forecast(provider='fred')
        >>> obb.fixedincome.rate.effr_forecast(long_run=True, provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/effr_forecast",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.effr_forecast",
                        ("fred",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def estr(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Euro Short-Term Rate.

        The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
        the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
        the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
        executed at arm's length and thus reflect market rates in an unbiased way.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]
            Frequency aggregation to convert daily data to lower frequency.

            a = Annual

            q = Quarterly

            m = Monthly

            w = Weekly

            d = Daily

            wef = Weekly, Ending Friday

            weth = Weekly, Ending Thursday

            wew = Weekly, Ending Wednesday

            wetu = Weekly, Ending Tuesday

            wem = Weekly, Ending Monday

            wesu = Weekly, Ending Sunday

            wesa = Weekly, Ending Saturday

            bwew = Biweekly, Ending Wednesday

            bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]
            A key that indicates the aggregation method used for frequency aggregation.

            avg = Average

            sum = Sum

            eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]
            Transformation type

            None = No transformation

            chg = Change

            ch1 = Change from Year Ago

            pch = Percent Change

            pc1 = Percent Change from Year Ago

            pca = Compounded Annual Rate of Change

            cch = Continuously Compounded Rate of Change

            cca = Continuously Compounded Annual Rate of Change

            log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[EuroShortTermRate]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EuroShortTermRate
        -----------------
        date : date
            The date of the data.
        rate : float
            Volume-weighted trimmed mean rate.
        percentile_25 : Optional[float]
            Rate at 25th percentile of volume.
        percentile_75 : Optional[float]
            Rate at 75th percentile of volume.
        volume : Optional[float]
            The trading volume. (Millions of €EUR).
        transactions : Optional[int]
            Number of transactions.
        number_of_banks : Optional[int]
            Number of active banks.
        large_bank_share_of_volume : Optional[float]
            The percent of volume attributable to the 5 largest active banks.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.estr(provider='fred')
        >>> obb.fixedincome.rate.estr(transform='ch1', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/estr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.estr",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def iorb(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Interest on Reserve Balances.

        Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
        domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
        United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.

        Returns
        -------
        OBBject
            results : List[IORB]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        IORB
        ----
        date : date
            The date of the data.
        rate : Optional[float]
            IORB rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.iorb(provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/iorb",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.iorb",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def overnight_bank_funding(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["federal_reserve", "fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Overnight Bank Funding.

        For the United States, the overnight bank funding rate (OBFR) is calculated as a volume-weighted median of
        overnight federal funds transactions and Eurodollar transactions reported in the
        FR 2420 Report of Selected Money Market Rates.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred.
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
                    wef = Weekly, Ending Friday
                    weth = Weekly, Ending Thursday
                    wew = Weekly, Ending Wednesday
                    wetu = Weekly, Ending Tuesday
                    wem = Weekly, Ending Monday
                    wesu = Weekly, Ending Sunday
                    wesa = Weekly, Ending Saturday
                    bwew = Biweekly, Ending Wednesday
                    bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]

                A key that indicates the aggregation method used for frequency aggregation.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[OvernightBankFundingRate]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OvernightBankFundingRate
        ------------------------
        date : date
            The date of the data.
        rate : float
            Overnight Bank Funding Rate.
        percentile_1 : Optional[float]
            1st percentile of the distribution.
        percentile_25 : Optional[float]
            25th percentile of the distribution.
        percentile_75 : Optional[float]
            75th percentile of the distribution.
        percentile_99 : Optional[float]
            99th percentile of the distribution.
        volume : Optional[float]
            The trading volume.The notional volume of transactions (Billions of $).
        revision_indicator : Optional[str]
            Indicates a revision of the data for that date. (provider: federal_reserve)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.overnight_bank_funding(provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/overnight_bank_funding",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.overnight_bank_funding",
                        ("federal_reserve", "fred"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def sofr(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["federal_reserve", "fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Secured Overnight Financing Rate.

        The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
        borrowing cash overnight collateralizing by Treasury securities.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred.
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
                    wef = Weekly, Ending Friday
                    weth = Weekly, Ending Thursday
                    wew = Weekly, Ending Wednesday
                    wetu = Weekly, Ending Tuesday
                    wem = Weekly, Ending Monday
                    wesu = Weekly, Ending Sunday
                    wesa = Weekly, Ending Saturday
                    bwew = Biweekly, Ending Wednesday
                    bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]

                A key that indicates the aggregation method used for frequency aggregation.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[SOFR]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SOFR
        ----
        date : date
            The date of the data.
        rate : float
            Effective federal funds rate.
        percentile_1 : Optional[float]
            1st percentile of the distribution.
        percentile_25 : Optional[float]
            25th percentile of the distribution.
        percentile_75 : Optional[float]
            75th percentile of the distribution.
        percentile_99 : Optional[float]
            99th percentile of the distribution.
        volume : Optional[float]
            The trading volume.The notional volume of transactions (Billions of $).
        average_30d : Optional[float]
            30-Day Average SOFR (provider: fred)
        average_90d : Optional[float]
            90-Day Average SOFR (provider: fred)
        average_180d : Optional[float]
            180-Day Average SOFR (provider: fred)
        index : Optional[float]
            SOFR index as 2018-04-02 = 1 (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.sofr(provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/sofr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.sofr",
                        ("federal_reserve", "fred"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def sonia(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Sterling Overnight Index Average.

        SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
        transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
        financial institutions and other institutional investors.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        parameter : Literal['rate', 'index', '10th_percentile', '25th_percentile', '75th_percentile', '90th_percentile', 'total_nominal_value']
            Period of SONIA rate. (provider: fred)

        Returns
        -------
        OBBject
            results : List[SONIA]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SONIA
        -----
        date : date
            The date of the data.
        rate : Optional[float]
            SONIA rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.sonia(provider='fred')
        >>> obb.fixedincome.rate.sonia(parameter='total_nominal_value', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/sonia",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.rate.sonia",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )
