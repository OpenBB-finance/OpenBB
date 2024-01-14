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
    eu_yield_curve
    treasury_auctions
    treasury_prices
    treasury_rates
    us_yield_curve
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def eu_yield_curve(
        self,
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        yield_curve_type: Annotated[
            Literal["spot_rate", "instantaneous_forward", "par_yield"],
            OpenBBCustomParameter(description="The yield curve type."),
        ] = "spot_rate",
        provider: Optional[Literal["ecb"]] = None,
        **kwargs
    ) -> OBBject:
        """Euro Area Yield Curve.

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
            date : Optional[datetime.date]
                A specific date to get data for.
            yield_curve_type : Literal['spot_rate', 'instantaneous_forward', 'par_yield']
                The yield curve type.
            provider : Optional[Literal['ecb']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'ecb' if there is
                no default.
            rating : Literal['A', 'C']
                The rating type. (provider: ecb)

            Returns
            -------
            OBBject
                results : List[EUYieldCurve]
                    Serializable results.
                provider : Optional[Literal['ecb']]
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
            rate : Optional[float]
                Yield curve rate.

            Example
            -------
            >>> from openbb import obb
            >>> obb.fixedincome.government.eu_yield_curve(yield_curve_type="spot_rate")
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/eu_yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "date": date,
                    "yield_curve_type": yield_curve_type,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def treasury_auctions(
        self,
        security_type: Annotated[
            Literal["Bill", "Note", "Bond", "CMB", "TIPS", "FRN", None],
            OpenBBCustomParameter(
                description="Used to only return securities of a particular type."
            ),
        ] = None,
        cusip: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Filter securities by CUSIP."),
        ] = None,
        page_size: Annotated[
            Optional[int],
            OpenBBCustomParameter(
                description="Maximum number of results to return; you must also include pagenum when using pagesize."
            ),
        ] = None,
        page_num: Annotated[
            Optional[int],
            OpenBBCustomParameter(
                description="The first page number to display results for; used in combination with page size."
            ),
        ] = None,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format. The default is 90 days ago."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format. The default is today."
            ),
        ] = None,
        provider: Optional[Literal["government_us"]] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Auctions.

        Parameters
        ----------
        security_type : Literal['Bill', 'Note', 'Bond', 'CMB', 'TIPS', 'FRN', None]
            Used to only return securities of a particular type.
        cusip : Optional[str]
            Filter securities by CUSIP.
        page_size : Optional[int]
            Maximum number of results to return; you must also include pagenum when using pagesize.
        page_num : Optional[int]
            The first page number to display results for; used in combination with page size.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format. The default is 90 days ago.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format. The default is today.
        provider : Optional[Literal['government_us']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'government_us' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[TreasuryAuctions]
                Serializable results.
            provider : Optional[Literal['government_us']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        TreasuryAuctions
        ----------------
        cusip : str
            CUSIP of the Security.
        issue_date : date
            The issue date of the security.
        security_type : Literal['Bill', 'Note', 'Bond', 'CMB', 'TIPS', 'FRN']
            The type of security.
        security_term : str
            The term of the security.
        maturity_date : date
            The maturity date of the security.
        interest_rate : Optional[float]
            The interest rate of the security.
        cpi_on_issue_date : Optional[float]
            Reference CPI rate on the issue date of the security.
        cpi_on_dated_date : Optional[float]
            Reference CPI rate on the dated date of the security.
        announcement_date : Optional[date]
            The announcement date of the security.
        auction_date : Optional[date]
            The auction date of the security.
        auction_date_year : Optional[int]
            The auction date year of the security.
        dated_date : Optional[date]
            The dated date of the security.
        first_payment_date : Optional[date]
            The first payment date of the security.
        accrued_interest_per_100 : Optional[float]
            Accrued interest per $100.
        accrued_interest_per_1000 : Optional[float]
            Accrued interest per $1000.
        adjusted_accrued_interest_per_100 : Optional[float]
            Adjusted accrued interest per $100.
        adjusted_accrued_interest_per_1000 : Optional[float]
            Adjusted accrued interest per $1000.
        adjusted_price : Optional[float]
            Adjusted price.
        allocation_percentage : Optional[float]
            Allocation percentage, as normalized percentage points.
        allocation_percentage_decimals : Optional[float]
            The number of decimals in the Allocation percentage.
        announced_cusip : Optional[str]
            The announced CUSIP of the security.
        auction_format : Optional[str]
            The auction format of the security.
        avg_median_discount_rate : Optional[float]
            The average median discount rate of the security.
        avg_median_investment_rate : Optional[float]
            The average median investment rate of the security.
        avg_median_price : Optional[float]
            The average median price paid for the security.
        avg_median_discount_margin : Optional[float]
            The average median discount margin of the security.
        avg_median_yield : Optional[float]
            The average median yield of the security.
        back_dated : Optional[Literal['Yes', 'No']]
            Whether the security is back dated.
        back_dated_date : Optional[date]
            The back dated date of the security.
        bid_to_cover_ratio : Optional[float]
            The bid to cover ratio of the security.
        call_date : Optional[date]
            The call date of the security.
        callable : Optional[Literal['Yes', 'No']]
            Whether the security is callable.
        called_date : Optional[date]
            The called date of the security.
        cash_management_bill : Optional[Literal['Yes', 'No']]
            Whether the security is a cash management bill.
        closing_time_competitive : Optional[str]
            The closing time for competitive bids on the security.
        closing_time_non_competitive : Optional[str]
            The closing time for non-competitive bids on the security.
        competitive_accepted : Optional[int]
            The accepted value for competitive bids on the security.
        competitive_accepted_decimals : Optional[int]
            The number of decimals in the Competitive Accepted.
        competitive_tendered : Optional[int]
            The tendered value for competitive bids on the security.
        competitive_tenders_accepted : Optional[Literal['Yes', 'No']]
            Whether competitive tenders are accepted on the security.
        corp_us_cusip : Optional[str]
            The CUSIP of the security.
        cpi_base_reference_period : Optional[str]
            The CPI base reference period of the security.
        currently_outstanding : Optional[int]
            The currently outstanding value on the security.
        direct_bidder_accepted : Optional[int]
            The accepted value from direct bidders on the security.
        direct_bidder_tendered : Optional[int]
            The tendered value from direct bidders on the security.
        est_amount_of_publicly_held_maturing_security : Optional[int]
            The estimated amount of publicly held maturing securities on the security.
        fima_included : Optional[Literal['Yes', 'No']]
            Whether the security is included in the FIMA (Foreign and International Money Authorities).
        fima_non_competitive_accepted : Optional[int]
            The non-competitive accepted value on the security from FIMAs.
        fima_non_competitive_tendered : Optional[int]
            The non-competitive tendered value on the security from FIMAs.
        first_interest_period : Optional[str]
            The first interest period of the security.
        first_interest_payment_date : Optional[date]
            The first interest payment date of the security.
        floating_rate : Optional[Literal['Yes', 'No']]
            Whether the security is a floating rate.
        frn_index_determination_date : Optional[date]
            The FRN index determination date of the security.
        frn_index_determination_rate : Optional[float]
            The FRN index determination rate of the security.
        high_discount_rate : Optional[float]
            The high discount rate of the security.
        high_investment_rate : Optional[float]
            The high investment rate of the security.
        high_price : Optional[float]
            The high price of the security at auction.
        high_discount_margin : Optional[float]
            The high discount margin of the security.
        high_yield : Optional[float]
            The high yield of the security at auction.
        index_ratio_on_issue_date : Optional[float]
            The index ratio on the issue date of the security.
        indirect_bidder_accepted : Optional[int]
            The accepted value from indirect bidders on the security.
        indirect_bidder_tendered : Optional[int]
            The tendered value from indirect bidders on the security.
        interest_payment_frequency : Optional[str]
            The interest payment frequency of the security.
        low_discount_rate : Optional[float]
            The low discount rate of the security.
        low_investment_rate : Optional[float]
            The low investment rate of the security.
        low_price : Optional[float]
            The low price of the security at auction.
        low_discount_margin : Optional[float]
            The low discount margin of the security.
        low_yield : Optional[float]
            The low yield of the security at auction.
        maturing_date : Optional[date]
            The maturing date of the security.
        max_competitive_award : Optional[int]
            The maximum competitive award at auction.
        max_non_competitive_award : Optional[int]
            The maximum non-competitive award at auction.
        max_single_bid : Optional[int]
            The maximum single bid at auction.
        min_bid_amount : Optional[int]
            The minimum bid amount at auction.
        min_strip_amount : Optional[int]
            The minimum strip amount at auction.
        min_to_issue : Optional[int]
            The minimum to issue at auction.
        multiples_to_bid : Optional[int]
            The multiples to bid at auction.
        multiples_to_issue : Optional[int]
            The multiples to issue at auction.
        nlp_exclusion_amount : Optional[int]
            The NLP exclusion amount at auction.
        nlp_reporting_threshold : Optional[int]
            The NLP reporting threshold at auction.
        non_competitive_accepted : Optional[int]
            The accepted value from non-competitive bidders on the security.
        non_competitive_tenders_accepted : Optional[Literal['Yes', 'No']]
            Whether or not the auction accepted non-competitive tenders.
        offering_amount : Optional[int]
            The offering amount at auction.
        original_cusip : Optional[str]
            The original CUSIP of the security.
        original_dated_date : Optional[date]
            The original dated date of the security.
        original_issue_date : Optional[date]
            The original issue date of the security.
        original_security_term : Optional[str]
            The original term of the security.
        pdf_announcement : Optional[str]
            The PDF filename for the announcement of the security.
        pdf_competitive_results : Optional[str]
            The PDF filename for the competitive results of the security.
        pdf_non_competitive_results : Optional[str]
            The PDF filename for the non-competitive results of the security.
        pdf_special_announcement : Optional[str]
            The PDF filename for the special announcements.
        price_per_100 : Optional[float]
            The price per 100 of the security.
        primary_dealer_accepted : Optional[int]
            The primary dealer accepted value on the security.
        primary_dealer_tendered : Optional[int]
            The primary dealer tendered value on the security.
        reopening : Optional[Literal['Yes', 'No']]
            Whether or not the auction was reopened.
        security_term_day_month : Optional[str]
            The security term in days or months.
        security_term_week_year : Optional[str]
            The security term in weeks or years.
        series : Optional[str]
            The series name of the security.
        soma_accepted : Optional[int]
            The SOMA accepted value on the security.
        soma_holdings : Optional[int]
            The SOMA holdings on the security.
        soma_included : Optional[Literal['Yes', 'No']]
            Whether or not the SOMA (System Open Market Account) was included on the security.
        soma_tendered : Optional[int]
            The SOMA tendered value on the security.
        spread : Optional[float]
            The spread on the security.
        standard_payment_per_1000 : Optional[float]
            The standard payment per 1000 of the security.
        strippable : Optional[Literal['Yes', 'No']]
            Whether or not the security is strippable.
        term : Optional[str]
            The term of the security.
        tiin_conversion_factor_per_1000 : Optional[float]
            The TIIN conversion factor per 1000 of the security.
        tips : Optional[Literal['Yes', 'No']]
            Whether or not the security is TIPS.
        total_accepted : Optional[int]
            The total accepted value at auction.
        total_tendered : Optional[int]
            The total tendered value at auction.
        treasury_retail_accepted : Optional[int]
            The accepted value on the security from retail.
        treasury_retail_tenders_accepted : Optional[Literal['Yes', 'No']]
            Whether or not the tender offers from retail are accepted
        type : Optional[str]
            The type of issuance.  This might be different than the security type.
        unadjusted_accrued_interest_per_1000 : Optional[float]
            The unadjusted accrued interest per 1000 of the security.
        unadjusted_price : Optional[float]
            The unadjusted price of the security.
        updated_timestamp : Optional[datetime]
            The updated timestamp of the security.
        xml_announcement : Optional[str]
            The XML filename for the announcement of the security.
        xml_competitive_results : Optional[str]
            The XML filename for the competitive results of the security.
        xml_special_announcement : Optional[str]
            The XML filename for special announcements.
        tint_cusip1 : Optional[str]
            Tint CUSIP 1.
        tint_cusip2 : Optional[str]
            Tint CUSIP 2.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_auctions()
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_auctions",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "security_type": security_type,
                    "cusip": cusip,
                    "page_size": page_size,
                    "page_num": page_num,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def treasury_prices(
        self,
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(
                description="A specific date to get data for. No date will return the current posted data."
            ),
        ] = None,
        provider: Optional[Literal["government_us"]] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Prices by date.

        Parameters
        ----------
        date : Optional[datetime.date]
            A specific date to get data for. No date will return the current posted data.
        provider : Optional[Literal['government_us']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'government_us' if there is
            no default.
        cusip : Optional[str]
            Filter by CUSIP. (provider: government_us)
        security_type : Literal[None, 'bill', 'note', 'bond', 'tips', 'frn']
            Filter by security type. (provider: government_us)

        Returns
        -------
        OBBject
            results : List[TreasuryPrices]
                Serializable results.
            provider : Optional[Literal['government_us']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        TreasuryPrices
        --------------
        date : date
            The date of the data.
        cusip : str
            CUSIP of the security.
        security_type : str
            The type of US Treasury security. Bill, Note, Bond, TIPS, FRN.
        rate : Optional[float]
            The annualized interest rate or coupon of the security.
        maturity_date : date
            The maturity date of the security.
        call_date : Optional[date]
            The call date of the security.
        bid : Optional[float]
            The bid price of the security.
        offer : Optional[float]
            The offer price of the security.
        eod_price : Optional[float]
            The end-of-day price of the security.

        Example
        -------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_prices()
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_prices",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
            )
        )

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
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
        >>> obb.fixedincome.government.treasury_rates()
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_rates",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
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
            Optional[datetime.date],
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
        date : Optional[datetime.date]
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
        >>> obb.fixedincome.government.us_yield_curve()
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/us_yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "date": date,
                    "inflation_adjusted": inflation_adjusted,
                },
                extra_params=kwargs,
            )
        )
