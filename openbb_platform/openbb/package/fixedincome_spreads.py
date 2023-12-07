### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_fixedincome_spreads(Container):
    """/fixedincome/spreads
    tmc
    tmc_effr
    treasury_effr
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def tmc(
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
        maturity: Annotated[
            Optional[Literal["3m", "2y"]],
            OpenBBCustomParameter(description="The maturity"),
        ] = "3m",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Treasury Constant Maturity.

            Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.
            Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
            Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
            yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        maturity : Optional[Literal['3m', '2y']]
            The maturity
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[TreasuryConstantMaturity]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        TreasuryConstantMaturity
        ------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            TreasuryConstantMaturity Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.spreads.tmc(maturity="3m")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "maturity": maturity,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/spreads/tmc",
            **inputs,
        )

    @validate
    def tmc_effr(
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
        maturity: Annotated[
            Optional[Literal["10y", "5y", "1y", "6m", "3m"]],
            OpenBBCustomParameter(description="The maturity"),
        ] = "10y",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Select Treasury Constant Maturity.

            Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate
            Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
            Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
            yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        maturity : Optional[Literal['10y', '5y', '1y', '6m', '3m']]
            The maturity
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SelectedTreasuryConstantMaturity]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SelectedTreasuryConstantMaturity
        --------------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            Selected Treasury Constant Maturity Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.spreads.tmc_effr(maturity="10y")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "maturity": maturity,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/spreads/tmc_effr",
            **inputs,
        )

    @validate
    def treasury_effr(
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
        maturity: Annotated[
            Optional[Literal["3m", "6m"]],
            OpenBBCustomParameter(description="The maturity"),
        ] = "3m",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Select Treasury Bill.

            Get Selected Treasury Bill Minus Federal Funds Rate.
            Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of
            auctioned U.S. Treasuries.
            The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
            yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        maturity : Optional[Literal['3m', '6m']]
            The maturity
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SelectedTreasuryBill]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SelectedTreasuryBill
        --------------------
        date : date
            The date of the data.
        rate : Optional[float]
            SelectedTreasuryBill Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.spreads.treasury_effr(maturity="3m")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "maturity": maturity,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/spreads/treasury_effr",
            **inputs,
        )
