### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class ROUTER_fixedincome(Container):
    """/fixedincome
    ameribor
    estr
    fed
    iorb
    projections
    sofr
    sonia
    treasury
    ycrv
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def ameribor(
        self,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """
            Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
            short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
            American Financial Exchange (AFX).

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
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
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        AMERIBOR
        --------
        date : Optional[date]
            The date of the data.
        rate : Optional[float]
            AMERIBOR rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/ameribor",
            **inputs,
        )

    @validate_arguments
    def estr(
        self,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """
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
        provider : Union[Literal['fred'], None]
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
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        ESTR
        ----
        date : Optional[date]
            The date of the data.
        rate : Optional[float]
            ESTR rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/estr",
            **inputs,
        )

    @validate_arguments
    def fed(
        self,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """
            Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        parameter : Literal['monthly', 'daily', 'weekly', 'daily_excl_weekend', 'annual', 'biweekly', 'volume']
            Period of FED rate. (provider: fred)

        Returns
        -------
        OBBject
            results : List[FEDFUNDS]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        FEDFUNDS
        --------
        date : Optional[date]
            The date of the data.
        rate : Optional[float]
            FED rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/fed",
            **inputs,
        )

    @validate_arguments
    def iorb(
        self,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """
            Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[IORB]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        IORB
        ----
        date : Optional[date]
            The date of the data.
        rate : Optional[float]
            IORB rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/iorb",
            **inputs,
        )

    @validate_arguments
    def projections(
        self, provider: Union[Literal["fred"], None] = None, **kwargs
    ) -> OBBject[List]:
        """
            Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        provider : Union[Literal['fred'], None]
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
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        PROJECTIONS
        -----------
        date : Optional[date]
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
            Central tendency of low projection of rates."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/projections",
            **inputs,
        )

    @validate_arguments
    def sofr(
        self,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get United States yield curve.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        period : Literal['overnight', '30_day', '90_day', '180_day', 'index']
            Period of SOFR rate. (provider: fred)

        Returns
        -------
        OBBject
            results : List[SOFR]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        SOFR
        ----
        date : Optional[date]
            The date of the data.
        rate : Optional[float]
            SOFR rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/sofr",
            **inputs,
        )

    @validate_arguments
    def sonia(
        self,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """
            SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
            transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
            financial institutions and other institutional investors.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
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
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        SONIA
        -----
        date : Optional[date]
            The date of the data.
        rate : Optional[float]
            SONIA rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/sonia",
            **inputs,
        )

    @validate_arguments
    def treasury(
        self,
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
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get treasury rates.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[TreasuryRates]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        TreasuryRates
        -------------
        date : Optional[date]
            The date of the data.
        month_1 : Optional[float]
            1 month treasury rate.
        month_2 : Optional[float]
            2 month treasury rate.
        month_3 : Optional[float]
            3 month treasury rate.
        month_6 : Optional[float]
            6 month treasury rate.
        year_1 : Optional[float]
            1 year treasury rate.
        year_2 : Optional[float]
            2 year treasury rate.
        year_3 : Optional[float]
            3 year treasury rate.
        year_5 : Optional[float]
            5 year treasury rate.
        year_7 : Optional[float]
            7 year treasury rate.
        year_10 : Optional[float]
            10 year treasury rate.
        year_20 : Optional[float]
            20 year treasury rate.
        year_30 : Optional[float]
            30 year treasury rate."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/treasury",
            **inputs,
        )

    @validate_arguments
    def ycrv(
        self,
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(
                description="Date to get Yield Curve data.  Defaults to the most recent FRED entry."
            ),
        ] = None,
        inflation_adjusted: typing_extensions.Annotated[
            Union[bool, None],
            OpenBBCustomParameter(description="Get inflation adjusted rates."),
        ] = False,
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get United States yield curve.

        Parameters
        ----------
        date : Union[datetime.date, None]
            Date to get Yield Curve data.  Defaults to the most recent FRED entry.
        inflation_adjusted : Union[bool, None]
            Get inflation adjusted rates.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[USYieldCurve]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        USYieldCurve
        ------------
        maturity : Optional[float]
            Maturity of the treasury rate in years.
        rate : Optional[float]
            Associated rate given in decimal form (0.05 is 5%)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "date": date,
                "inflation_adjusted": inflation_adjusted,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/fixedincome/ycrv",
            **inputs,
        )
