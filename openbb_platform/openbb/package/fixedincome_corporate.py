### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_fixedincome_corporate(Container):
    """/fixedincome/corporate
    commercial_paper
    hqm
    ice_bofa
    moody
    spot_rates
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def commercial_paper(
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
            Literal["overnight", "7d", "15d", "30d", "60d", "90d"],
            OpenBBCustomParameter(description="The maturity."),
        ] = "30d",
        category: Annotated[
            Literal["asset_backed", "financial", "nonfinancial"],
            OpenBBCustomParameter(description="The category."),
        ] = "financial",
        grade: Annotated[
            Literal["aa", "a2_p2"], OpenBBCustomParameter(description="The grade.")
        ] = "aa",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Commercial Paper.

        Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations.
        Maturities range up to 270 days but average about 30 days.
        Many companies use CP to raise cash needed for current transactions,
        and many find it to be a lower-cost alternative to bank loans.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        maturity : Literal['overnight', '7d', '15d', '30d', '60d', '90d']
            The maturity.
        category : Literal['asset_backed', 'financial', 'nonfinancial']
            The category.
        grade : Literal['aa', 'a2_p2']
            The grade.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[CommercialPaper]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CommercialPaper
        ---------------
        date : date
            The date of the data.
        rate : Optional[float]
            Commercial Paper Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.commercial_paper(maturity="15d")
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/commercial_paper",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/corporate/commercial_paper",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "maturity": maturity,
                    "category": category,
                    "grade": grade,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def hqm(
        self,
        date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        yield_curve: Annotated[
            Literal["spot", "par"],
            OpenBBCustomParameter(description="The yield curve type."),
        ] = "spot",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """High Quality Market Corporate Bond.

        The HQM yield curve represents the high quality corporate bond market, i.e.,
        corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms.
        These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
        that is the market-weighted average (MWA) quality of high quality bonds.


        Parameters
        ----------
        date : Union[datetime.date, None, str]
            A specific date to get data for.
        yield_curve : Literal['spot', 'par']
            The yield curve type.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[HighQualityMarketCorporateBond]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HighQualityMarketCorporateBond
        ------------------------------
        date : date
            The date of the data.
        rate : Optional[float]
            HighQualityMarketCorporateBond Rate.
        maturity : str
            Maturity.
        yield_curve : Literal['spot', 'par']
            The yield curve type.
        series_id : Optional[str]
            FRED series id. (provider: fred)

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.hqm(yield_curve="par")
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/hqm",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/corporate/hqm",
                        ("fred",),
                    )
                },
                standard_params={
                    "date": date,
                    "yield_curve": yield_curve,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def ice_bofa(
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
        index_type: Annotated[
            Literal["yield", "yield_to_worst", "total_return", "spread"],
            OpenBBCustomParameter(description="The type of series."),
        ] = "yield",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """ICE BofA US Corporate Bond Indices.

        The ICE BofA US Corporate Index tracks the performance of US dollar denominated investment grade corporate debt
        publicly issued in the US domestic market. Qualifying securities must have an investment grade rating (based on an
        average of Moody’s, S&P and Fitch), at least 18 months to final maturity at the time of issuance, at least one year
        remaining term to final maturity as of the rebalance date, a fixed coupon schedule and a minimum amount
        outstanding of $250 million. The ICE BofA US Corporate Index is a component of the US Corporate Master Index.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['yield', 'yield_to_worst', 'total_return', 'spread']
            The type of series.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        category : Literal['all', 'duration', 'eur', 'usd']
            The type of category. (provider: fred)
        area : Literal['asia', 'emea', 'eu', 'ex_g10', 'latin_america', 'us']
            The type of area. (provider: fred)
        grade : Literal['a', 'aa', 'aaa', 'b', 'bb', 'bbb', 'ccc', 'crossover', 'high_grade', 'high_yield', 'non_financial', 'non_sovereign', 'private_sector', 'public_sector']
            The type of grade. (provider: fred)
        options : bool
            Whether to include options in the results. (provider: fred)

        Returns
        -------
        OBBject
            results : List[ICEBofA]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ICEBofA
        -------
        date : date
            The date of the data.
        rate : Optional[float]
            ICE BofA US Corporate Bond Indices Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.ice_bofa(index_type="yield_to_worst")
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/ice_bofa",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/corporate/ice_bofa",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "index_type": index_type,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def moody(
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
        index_type: Annotated[
            Literal["aaa", "baa"],
            OpenBBCustomParameter(description="The type of series."),
        ] = "aaa",
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Moody Corporate Bond Index.

        Moody's Aaa and Baa are investment bonds that acts as an index of
        the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively.
        These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year
        Treasury Bill as an indicator of the interest rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['aaa', 'baa']
            The type of series.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        spread : Optional[Literal['treasury', 'fed_funds']]
            The type of spread. (provider: fred)

        Returns
        -------
        OBBject
            results : List[MoodyCorporateBondIndex]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        MoodyCorporateBondIndex
        -----------------------
        date : date
            The date of the data.
        rate : Optional[float]
            Moody Corporate Bond Index Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.moody(index_type="baa")
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/moody",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/corporate/moody",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "index_type": index_type,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def spot_rates(
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
            List[float], OpenBBCustomParameter(description="The maturities in years.")
        ] = [10.0],
        category: Annotated[
            List[Literal["par_yield", "spot_rate"]],
            OpenBBCustomParameter(description="The category."),
        ] = ["spot_rate"],
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """Spot Rates.

        The spot rates for any maturity is the yield on a bond that provides a single payment at that maturity.
        This is a zero coupon bond.
        Because each spot rate pertains to a single cashflow, it is the relevant interest rate
        concept for discounting a pension liability at the same maturity.


        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        maturity : List[float]
            The maturities in years.
        category : List[Literal['par_yield', 'spot_rate']]
            The category.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SpotRate]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SpotRate
        --------
        date : date
            The date of the data.
        rate : Optional[float]
            Spot Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.spot_rates(maturity=[10,20,30,50])
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/spot_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/fixedincome/corporate/spot_rates",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "maturity": maturity,
                    "category": category,
                },
                extra_params=kwargs,
            )
        )
