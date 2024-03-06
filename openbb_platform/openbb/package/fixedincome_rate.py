### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
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
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Ameribor.

        Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
        short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
        American Financial Exchange (AFX).


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        parameter : Literal['overnight', 'term_30', 'term_90', '1_week_term_structure', '1_month_term_structure', '3_month_term_structure', '6_month_term_structure', '1_year_term_structure', '2_year_term_structure', '30_day_ma', '90_day_ma']
            Period of AMERIBOR rate. (provider: fred)

        Returns
        -------
        OBBject
            results : List[AMERIBOR]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        AMERIBOR
        --------
        date : date
            The date of the data.
        rate : Optional[float]
            AMERIBOR rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.ameribor(parameter="30_day_ma").to_df()
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/ameribor",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/ameribor",
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
    def dpcredit(
        self,
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
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Discount Window Primary Credit Rate.

        A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
        The rates central banks charge are set to stabilize the economy.
        In the United States, the Federal Reserve System's Board of Governors set the bank rate,
        also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.dpcredit(start_date="2023-02-01", end_date="2023-05-01").to_df()
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/dpcredit",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/dpcredit",
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
        interest_rate_type: Annotated[
            Literal["deposit", "lending", "refinancing"],
            OpenBBCustomParameter(description="The type of interest rate."),
        ] = "lending",
        provider: Optional[Literal["fred"]] = None,
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
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        interest_rate_type : Literal['deposit', 'lending', 'refinancing']
            The type of interest rate.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

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

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.ecb(interest_rate_type="refinancing")
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/ecb",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/ecb",
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
        provider: Optional[Literal["federal_reserve", "fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Fed Funds Rate.

        Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
        domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
        United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'federal_reserve' if there is
            no default.
        parameter : Literal['monthly', 'daily', 'weekly', 'daily_excl_weekend', 'annual', 'biweekly', 'volume']
            Period of FED rate. (provider: fred)

        Returns
        -------
        OBBject
            results : List[FEDFUNDS]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FEDFUNDS
        --------
        date : date
            The date of the data.
        rate : Optional[float]
            FED rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.effr(parameter="daily", provider="fred").to_df()
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/effr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/effr",
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
        self, provider: Optional[Literal["fred"]] = None, **kwargs
    ) -> OBBject:
        """Fed Funds Rate Projections.

        The projections for the federal funds rate are the value of the midpoint of the
        projected appropriate target range for the federal funds rate or the projected
        appropriate target level for the federal funds rate at the end of the specified
        calendar year or over the longer run.


        Parameters
        ----------
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.effr_forecast(long_run=True)
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/effr_forecast",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/effr_forecast",
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
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Euro Short-Term Rate.

        The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
        the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
        the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
        executed at arm’s length and thus reflect market rates in an unbiased way.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        parameter : Literal['volume_weighted_trimmed_mean_rate', 'number_of_transactions', 'number_of_active_banks', 'total_volume', 'share_of_volume_of_the_5_largest_active_banks', 'rate_at_75th_percentile_of_volume', 'rate_at_25th_percentile_of_volume']
            Period of ESTR rate. (provider: fred)

        Returns
        -------
        OBBject
            results : List[ESTR]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ESTR
        ----
        date : date
            The date of the data.
        rate : Optional[float]
            ESTR rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.estr(parameter="number_of_active_banks")
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/estr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/estr",
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
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Interest on Reserve Balances.

        Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
        domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
        United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

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

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.iorb()
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/iorb",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/iorb",
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
    def sonia(
        self,
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
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Sterling Overnight Index Average.

        SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
        transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
        financial institutions and other institutional investors.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.rate.sonia(parameter="total_nominal_value")
        """  # noqa: E501

        return self._run(
            "/fixedincome/rate/sonia",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/rate/sonia",
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
