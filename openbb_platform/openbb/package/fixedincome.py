### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_fixedincome(Container):
    """/fixedincome
    ameribor
    cp
    dwpcr
    ecb_interest_rates
    estr
    eu_ycrv
    fed
    ffrmc
    hqm
    ice_bofa
    iorb
    moody
    projections
    sofr
    sonia
    spot
    tbffr
    tmc
    treasury
    ycrv
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
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
    ) -> OBBject[List[Data]]:
        """
            Ameribor.
            Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
            short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
            American Financial Exchange (AFX).

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
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
            results : Union[List[AMERIBOR]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            AMERIBOR rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.ameribor()
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
    def cp(
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
        maturity: typing_extensions.Annotated[
            Literal["overnight", "7d", "15d", "30d", "60d", "90d"],
            OpenBBCustomParameter(description="The maturity."),
        ] = "30d",
        category: typing_extensions.Annotated[
            Literal["asset_backed", "financial", "nonfinancial"],
            OpenBBCustomParameter(description="The category."),
        ] = "financial",
        grade: typing_extensions.Annotated[
            Literal["aa", "a2_p2"], OpenBBCustomParameter(description="The grade.")
        ] = "aa",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Commercial Paper.
            Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations.
            Maturities range up to 270 days but average about 30 days.
            Many companies use CP to raise cash needed for current transactions,
            and many find it to be a lower-cost alternative to bank loans.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        maturity : Literal['overnight', '7d', '15d', '30d', '60d', '90d']
            The maturity.
        category : Literal['asset_backed', 'financial', 'nonfinancial']
            The category.
        grade : Literal['aa', 'a2_p2']
            The grade.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[CommercialPaper]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CommercialPaper
        ---------------
        date : date
            The date of the data.
        rate : Union[float]
            Commercial Paper Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.cp(maturity="30d", category="financial", grade="aa")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
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

        return self._run(
            "/fixedincome/cp",
            **inputs,
        )

    @validate
    def dwpcr(
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
    ) -> OBBject[List[Data]]:
        """
            Discount Window Primary Credit Rate.
            A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
            The rates central banks charge are set to stabilize the economy.
            In the United States, the Federal Reserve System's Board of Governors set the bank rate,
            also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        parameter : Literal['daily_excl_weekend', 'monthly', 'weekly', 'daily', 'annual']
            FRED series ID of DWPCR data. (provider: fred)

        Returns
        -------
        OBBject
            results : Union[List[DiscountWindowPrimaryCreditRate]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        DiscountWindowPrimaryCreditRate
        -------------------------------
        date : date
            The date of the data.
        rate : Union[float]
            Discount Window Primary Credit Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.dwpcr()
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
            "/fixedincome/dwpcr",
            **inputs,
        )

    @validate
    def ecb_interest_rates(
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
        interest_rate_type: typing_extensions.Annotated[
            Literal["deposit", "lending", "refinancing"],
            OpenBBCustomParameter(description="The type of interest rate."),
        ] = "lending",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            European Central Bank Interest Rates.
            The Governing Council of the ECB sets the key interest rates for the euro area:

            - The interest rate on the main refinancing operations (MRO), which provide
            the bulk of liquidity to the banking system.
            - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
            - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        interest_rate_type : Literal['deposit', 'lending', 'refinancing']
            The type of interest rate.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[EuropeanCentralBankInterestRates]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EuropeanCentralBankInterestRates
        --------------------------------
        date : date
            The date of the data.
        rate : Union[float]
            European Central Bank Interest Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.ecb_interest_rates(interest_rate_type="lending")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "interest_rate_type": interest_rate_type,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/ecb_interest_rates",
            **inputs,
        )

    @validate
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
    ) -> OBBject[List[Data]]:
        """
            Euro Short-Term Rate.
            The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
            the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
            the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
            executed at arm’s length and thus reflect market rates in an unbiased way.

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
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
            results : Union[List[ESTR]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            ESTR rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.estr()
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
    def eu_ycrv(
        self,
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        yield_curve_type: typing_extensions.Annotated[
            Literal["spot_rate", "instantaneous_forward", "par_yield"],
            OpenBBCustomParameter(description="The yield curve type."),
        ] = "spot_rate",
        provider: Union[Literal["ecb"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Euro Area Yield Curve.

            Gets euro area yield curve data from ECB.

            The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
            maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
            the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
            Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
            estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
            or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
            and setting yields in other sectors of the debt market.

            It is clear that the market’s expectations of future rate changes are one important determinant of the
            yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
            tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
            bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
            hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
            have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
            activity of risk-neutral traders removes all expected return differentials across bonds.


        Parameters
        ----------
        date : Union[datetime.date, None]
            A specific date to get data for.
        yield_curve_type : Literal['spot_rate', 'instantaneous_forward', 'par_yield']
            The yield curve type.
        provider : Union[Literal['ecb'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'ecb' if there is
            no default.
        rating : Literal['A', 'C']
            The rating type. (provider: ecb)

        Returns
        -------
        OBBject
            results : Union[List[EUYieldCurve]]
                Serializable results.
            provider : Union[Literal['ecb'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EUYieldCurve
        ------------
        maturity : str
            Yield curve rate maturity.
        rate : Optional[Union[float]]
            Yield curve rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.eu_ycrv(yield_curve_type="spot_rate")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "date": date,
                "yield_curve_type": yield_curve_type,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/eu_ycrv",
            **inputs,
        )

    @validate
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
    ) -> OBBject[List[Data]]:
        """
            Fed Funds Rate.
            Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
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
            results : Union[List[FEDFUNDS]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            FED rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.fed()
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
    def ffrmc(
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
        maturity: typing_extensions.Annotated[
            Union[Literal["10y", "5y", "1y", "6m", "3m"], None],
            OpenBBCustomParameter(description="The maturity"),
        ] = "10y",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Selected Treasury Constant Maturity.
            Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate
            Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
            Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
            yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        maturity : Union[Literal['10y', '5y', '1y', '6m', '3m'], None]
            The maturity
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[SelectedTreasuryConstantMaturity]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            Selected Treasury Constant Maturity Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.ffrmc(maturity="10y")
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
            "/fixedincome/ffrmc",
            **inputs,
        )

    @validate
    def hqm(
        self,
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(description="The date of the data."),
        ] = None,
        yield_curve: typing_extensions.Annotated[
            List[Literal["spot", "par"]],
            OpenBBCustomParameter(description="The yield curve type."),
        ] = ["spot"],
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            High Quality Market Corporate Bond.
            The HQM yield curve represents the high quality corporate bond market, i.e.,
            corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms.
            These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
            that is the market-weighted average (MWA) quality of high quality bonds.


        Parameters
        ----------
        date : Union[datetime.date, None]
            The date of the data.
        yield_curve : List[Literal['spot', 'par']]
            The yield curve type.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[HighQualityMarketCorporateBond]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        HighQualityMarketCorporateBond
        ------------------------------
        date : date
            The date of the data.
        rate : Union[float]
            HighQualityMarketCorporateBond Rate.
        maturity : str
            Maturity.
        yield_curve : Literal['spot', 'par']
            The yield curve type.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.hqm(yield_curve=['spot'])
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "date": date,
                "yield_curve": yield_curve,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/hqm",
            **inputs,
        )

    @validate
    def ice_bofa(
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
        index_type: typing_extensions.Annotated[
            Literal["yield", "yield_to_worst", "total_return", "spread"],
            OpenBBCustomParameter(description="The type of series."),
        ] = "yield",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            ICE BofA US Corporate Bond Indices.
            The ICE BofA US Corporate Index tracks the performance of US dollar denominated investment grade corporate debt
            publicly issued in the US domestic market. Qualifying securities must have an investment grade rating (based on an
            average of Moody’s, S&P and Fitch), at least 18 months to final maturity at the time of issuance, at least one year
            remaining term to final maturity as of the rebalancing date, a fixed coupon schedule and a minimum amount
            outstanding of $250 million. The ICE BofA US Corporate Index is a component of the US Corporate Master Index.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['yield', 'yield_to_worst', 'total_return', 'spread']
            The type of series.
        provider : Union[Literal['fred'], None]
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
            results : Union[List[ICEBofA]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ICEBofA
        -------
        date : date
            The date of the data.
        rate : Union[float]
            ICE BofA US Corporate Bond Indices Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.ice_bofa(index_type="yield")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "index_type": index_type,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/ice_bofa",
            **inputs,
        )

    @validate
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
    ) -> OBBject[List[Data]]:
        """
            Interest on Reserve Balances.
            Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
            domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
            United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[IORB]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            IORB rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.iorb()
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
    def moody(
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
        index_type: typing_extensions.Annotated[
            Literal["aaa", "baa"],
            OpenBBCustomParameter(description="The type of series."),
        ] = "aaa",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Moody Corporate Bond Index.
            Moody's Aaa and Baa are investment bonds that acts as an index of
            the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively.
            These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year
            Treasury Bill as an indicator of the interest rate.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['aaa', 'baa']
            The type of series.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        spread : Optional[Union[Literal['treasury', 'fed_funds']]]
            The type of spread. (provider: fred)

        Returns
        -------
        OBBject
            results : Union[List[MoodyCorporateBondIndex]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MoodyCorporateBondIndex
        -----------------------
        date : date
            The date of the data.
        rate : Union[float]
            Moody Corporate Bond Index Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.moody(index_type="aaa")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "index_type": index_type,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/moody",
            **inputs,
        )

    @validate
    def projections(
        self, provider: Union[Literal["fred"], None] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """
            Fed Funds Rate Projections.
            The projections for the federal funds rate are the value of the midpoint of the
            projected appropriate target range for the federal funds rate or the projected
            appropriate target level for the federal funds rate at the end of the specified
            calendar year or over the longer run.


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
            results : Union[List[PROJECTIONS]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        range_high : Union[float]
            High projection of rates.
        central_tendency_high : Union[float]
            Central tendency of high projection of rates.
        median : Union[float]
            Median projection of rates.
        range_midpoint : Union[float]
            Midpoint projection of rates.
        central_tendency_midpoint : Union[float]
            Central tendency of midpoint projection of rates.
        range_low : Union[float]
            Low projection of rates.
        central_tendency_low : Union[float]
            Central tendency of low projection of rates.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.projections()
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
    ) -> OBBject[List[Data]]:
        """
            Secured Overnight Financing Rate.
            The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
            borrowing cash overnight collateralized by Treasury securities.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
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
            results : Union[List[SOFR]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            SOFR rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.sofr()
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
    ) -> OBBject[List[Data]]:
        """
            Sterling Overnight Index Average.
            SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
            transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
            financial institutions and other institutional investors.

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
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
            results : Union[List[SONIA]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            SONIA rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.sonia()
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
    def spot(
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
        maturity: typing_extensions.Annotated[
            List[float], OpenBBCustomParameter(description="The maturities in years.")
        ] = [10.0],
        category: typing_extensions.Annotated[
            List[Literal["par_yield", "spot_rate"]],
            OpenBBCustomParameter(description="The category."),
        ] = ["spot_rate"],
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Spot Rate.
            The spot rate for any maturity is the yield on a bond that provides a single payment at that maturity.
            This is a zero coupon bond.
            Because each spot rate pertains to a single cashflow, it is the relevant interest rate
            concept for discounting a pension liability at the same maturity.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        maturity : List[float]
            The maturities in years.
        category : List[Literal['par_yield', 'spot_rate']]
            The category.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[SpotRate]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SpotRate
        --------
        date : date
            The date of the data.
        rate : Union[float]
            Spot Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.spot(maturity=[10.0], category=['spot_rate'])
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "maturity": maturity,
                "category": category,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/fixedincome/spot",
            **inputs,
        )

    @validate
    def tbffr(
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
        maturity: typing_extensions.Annotated[
            Union[Literal["3m", "6m"], None],
            OpenBBCustomParameter(description="The maturity"),
        ] = "3m",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Selected Treasury Bill.
            Get Selected Treasury Bill Minus Federal Funds Rate.
            Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of
            auctioned U.S. Treasuries.
            The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
            yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        maturity : Union[Literal['3m', '6m'], None]
            The maturity
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[SelectedTreasuryBill]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            SelectedTreasuryBill Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.tbffr(maturity="3m")
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
            "/fixedincome/tbffr",
            **inputs,
        )

    @validate
    def tmc(
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
        maturity: typing_extensions.Annotated[
            Union[Literal["3m", "2y"], None],
            OpenBBCustomParameter(description="The maturity"),
        ] = "3m",
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Treasury Constant Maturity.
            Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.
            Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
            Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
            yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.


        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        maturity : Union[Literal['3m', '2y'], None]
            The maturity
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[TreasuryConstantMaturity]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        rate : Union[float]
            TreasuryConstantMaturity Rate.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.tmc(maturity="3m")
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
            "/fixedincome/tmc",
            **inputs,
        )

    @validate
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
    ) -> OBBject[List[Data]]:
        """Treasury Rates. Treasury rates data.

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[TreasuryRates]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.treasury()
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
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(
                description="A specific date to get data for. Defaults to the most recent FRED entry."
            ),
        ] = None,
        inflation_adjusted: typing_extensions.Annotated[
            Union[bool, None],
            OpenBBCustomParameter(description="Get inflation adjusted rates."),
        ] = False,
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """US Yield Curve. Get United States yield curve.

        Parameters
        ----------
        date : Union[datetime.date, None]
            A specific date to get data for. Defaults to the most recent FRED entry.
        inflation_adjusted : Union[bool, None]
            Get inflation adjusted rates.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[USYieldCurve]]
                Serializable results.
            provider : Union[Literal['fred'], None]
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
        >>> obb.fixedincome.ycrv()
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
