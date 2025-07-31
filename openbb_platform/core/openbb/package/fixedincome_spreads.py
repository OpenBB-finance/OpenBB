### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_fixedincome_spreads(Container):
    """/fixedincome/spreads
    tcm
    tcm_effr
    treasury_effr
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def tcm(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        maturity: Annotated[
            Optional[Literal["3m", "2y"]], OpenBBField(description="The maturity")
        ] = "3m",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Treasury Constant Maturity.

        Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.
        Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
        Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
        yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        maturity : Optional[Literal['3m', '2y']]
            The maturity

        Returns
        -------
        OBBject
            results : list[TreasuryConstantMaturity]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TreasuryConstantMaturity
        ------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            TreasuryConstantMaturity Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.spreads.tcm(provider='fred')
        >>> obb.fixedincome.spreads.tcm(maturity='2y', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/spreads/tcm",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.spreads.tcm",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "maturity": maturity,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def tcm_effr(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        maturity: Annotated[
            Optional[Literal["10y", "5y", "1y", "6m", "3m"]],
            OpenBBField(description="The maturity"),
        ] = "10y",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Select Treasury Constant Maturity.

        Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate
        Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
        Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
        yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        maturity : Optional[Literal['10y', '5y', '1y', '6m', '3m']]
            The maturity

        Returns
        -------
        OBBject
            results : list[SelectedTreasuryConstantMaturity]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SelectedTreasuryConstantMaturity
        --------------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            Selected Treasury Constant Maturity Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.spreads.tcm_effr(provider='fred')
        >>> obb.fixedincome.spreads.tcm_effr(maturity='10y', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/spreads/tcm_effr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.spreads.tcm_effr",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "maturity": maturity,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def treasury_effr(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        maturity: Annotated[
            Optional[Literal["3m", "6m"]], OpenBBField(description="The maturity")
        ] = "3m",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Select Treasury Bill.

        Get Selected Treasury Bill Minus Federal Funds Rate.
        Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of
        auctioned U.S. Treasuries.
        The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
        yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        maturity : Optional[Literal['3m', '6m']]
            The maturity

        Returns
        -------
        OBBject
            results : list[SelectedTreasuryBill]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SelectedTreasuryBill
        --------------------
        date : date
            The date of the data.
        rate : Optional[float]
            SelectedTreasuryBill Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.spreads.treasury_effr(provider='fred')
        >>> obb.fixedincome.spreads.treasury_effr(maturity='6m', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/spreads/treasury_effr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.spreads.treasury_effr",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "maturity": maturity,
                },
                extra_params=kwargs,
            )
        )
