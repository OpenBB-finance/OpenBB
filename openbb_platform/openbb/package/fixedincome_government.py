### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_fixedincome_government(Container):
    """/fixedincome/government
    treasury_rates
    us_yield_curve
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def treasury_rates(
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
        provider: Optional[Literal["federal_reserve", "fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Rates.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'federal_reserve' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[TreasuryRates]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fmp']]
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
            30 year treasury rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_rates(provider="federal_reserve")
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/government/treasury_rates",
                        ("federal_reserve", "fmp"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def us_yield_curve(
        self,
        date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="A specific date to get data for. Defaults to the most recent FRED entry."
            ),
        ] = None,
        inflation_adjusted: Annotated[
            Optional[bool],
            OpenBBCustomParameter(description="Get inflation adjusted rates."),
        ] = False,
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """US Yield Curve. Get United States yield curve.

        Parameters
        ----------
        date : Union[datetime.date, None, str]
            A specific date to get data for. Defaults to the most recent FRED entry.
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
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.government.us_yield_curve(inflation_adjusted=True)
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/us_yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/government/us_yield_curve",
                        ("fred",),
                    )
                },
                standard_params={
                    "date": date,
                    "inflation_adjusted": inflation_adjusted,
                },
                extra_params=kwargs,
            )
        )
