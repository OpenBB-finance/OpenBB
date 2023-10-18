### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from openbb_core.app.static.container import Container
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
import openbb_provider
import pandas
import datetime
import pydantic
from pydantic import BaseModel
from inspect import Parameter
import typing
from typing import List, Dict, Union, Optional, Literal
from annotated_types import Ge, Le, Gt, Lt
from typing_extensions import Annotated
from openbb_core.app.utils import df_to_basemodel
from openbb_core.app.static.decorators import validate

from openbb_core.app.static.filters import filter_inputs

from openbb_provider.abstract.data import Data
import openbb_core.app.model.command_context
import openbb_core.app.model.obbject
import types


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
    ) -> OBBject[List[Data]]:
        """
            Ameribor.
            Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
            short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
            American Financial Exchange (AFX).

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
                Extra info.

        AMERIBOR
        --------
        date : date
            The date of the data.
        rate : Optional[float]
            AMERIBOR rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.ameribo)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/ameribor",
            **inputs,
        )

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
    ) -> OBBject[List[Data]]:
        """
            Euro Short-Term Rate.
            The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
            the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
            the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
            executed at arm’s length and thus reflect market rates in an unbiased way.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
                Extra info.

        ESTR
        ----
        date : date
            The date of the data.
        rate : Optional[float]
            ESTR rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.est)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/estr",
            **inputs,
        )

    @validate
    def fed(
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
    ) -> OBBject[List[Data]]:
        """
            Fed Funds Rate.
            Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
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
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FEDFUNDS
        --------
        date : date
            The date of the data.
        rate : Optional[float]
            FED rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.fe)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/fed",
            **inputs,
        )

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
    ) -> OBBject[List[Data]]:
        """
            Interest on Reserve Balances.
            Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
                Extra info.

        IORB
        ----
        date : date
            The date of the data.
        rate : Optional[float]
            IORB rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.ior)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/iorb",
            **inputs,
        )

    @validate
    def projections(
        self, provider: Optional[Literal["fred"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """
            Fed Funds Rate Projections.
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
            extra: Dict[str, Any]
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
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.projection)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/projections",
            **inputs,
        )

    @validate
    def sofr(
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
    ) -> OBBject[List[Data]]:
        """
            Secured Overnight Financing Rate.
            The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
            borrowing cash overnight collateralized by Treasury securities.


        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
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
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SOFR
        ----
        date : date
            The date of the data.
        rate : Optional[float]
            SOFR rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.sof)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/sofr",
            **inputs,
        )

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
    ) -> OBBject[List[Data]]:
        """
            Sterling Overnight Index Average.
            SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
            transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
            financial institutions and other institutional investors.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
                Extra info.

        SONIA
        -----
        date : date
            The date of the data.
        rate : Optional[float]
            SONIA rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.soni)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/sonia",
            **inputs,
        )

    @validate
    def treasury(
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
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Treasury Rates. Treasury rates data.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[TreasuryRates]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        TreasuryRates
        -------------
        date : date
            The date of the data.
        month_1 : float
            1 month treasury rate.
        month_2 : float
            2 month treasury rate.
        month_3 : float
            3 month treasury rate.
        month_6 : float
            6 month treasury rate.
        year_1 : float
            1 year treasury rate.
        year_2 : float
            2 year treasury rate.
        year_3 : float
            3 year treasury rate.
        year_5 : float
            5 year treasury rate.
        year_7 : float
            7 year treasury rate.
        year_10 : float
            10 year treasury rate.
        year_20 : float
            20 year treasury rate.
        year_30 : float
            30 year treasury rate.
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.treasur)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/treasury",
            **inputs,
        )

    @validate
    def ycrv(
        self,
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(
                description="Date to get Yield Curve data.  Defaults to the most recent FRED entry."
            ),
        ] = None,
        inflation_adjusted: Annotated[
            Optional[bool],
            OpenBBCustomParameter(description="Get inflation adjusted rates."),
        ] = False,
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """US Yield Curve. Get United States yield curve.

        Parameters
        ----------
        date : Optional[datetime.date]
            Date to get Yield Curve data.  Defaults to the most recent FRED entry.
        inflation_adjusted : Optional[bool]
            Get inflation adjusted rates.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[USYieldCurve]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        USYieldCurve
        ------------
        maturity : float
            Maturity of the treasury rate in years.
        rate : float
            Associated rate given in decimal form (0.05 is 5%)
        Example
        --------

        >>> from openbb import obb
        >>> obb.fixedincome.ycr)
        """  # noqa: E501

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

        return self._run(
            "/fixedincome/ycrv",
            **inputs,
        )
