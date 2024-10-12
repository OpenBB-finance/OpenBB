### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union
from warnings import simplefilter, warn

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_fixedincome_government(Container):
    """/fixedincome/government
    eu_yield_curve
    tips_yields
    treasury_auctions
    treasury_prices
    treasury_rates
    us_yield_curve
    yield_curve
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    @deprecated(
        "This endpoint will be removed in a future version. Use, `/fixedincome/government/yield_curve`, instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.4.",
        category=OpenBBDeprecationWarning,
    )
    def eu_yield_curve(
        self,
        date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="A specific date to get data for."),
        ] = None,
        provider: Annotated[
            Optional[Literal["ecb"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: ecb."
            ),
        ] = None,
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
        date : Union[date, None, str]
            A specific date to get data for.
        provider : Optional[Literal['ecb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: ecb.
        rating : Literal['aaa', 'all_ratings']
            The rating type, either 'aaa' or 'all_ratings'. (provider: ecb)
        yield_curve_type : Literal['spot_rate', 'instantaneous_forward', 'par_yield']
            The yield curve type. (provider: ecb)

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
            extra : Dict[str, Any]
                Extra info.

        EUYieldCurve
        ------------
        maturity : Optional[float]
            Maturity, in years.
        rate : Optional[float]
            Yield curve rate, as a normalized percent.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.eu_yield_curve(provider='ecb')
        >>> obb.fixedincome.government.eu_yield_curve(yield_curve_type='spot_rate', provider='ecb')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint will be removed in a future version. Use, `/fixedincome/government/yield_curve`, instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.4.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/fixedincome/government/eu_yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.eu_yield_curve",
                        ("ecb",),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def tips_yields(
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
        """Get current Treasury inflation-protected securities yields.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        maturity : Optional[Literal[5, 10, 20, 30]]
            The maturity of the security in years - 5, 10, 20, 30 - defaults to all. Note that the maturity is the tenor of the security, not the time to maturity. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]
            Frequency aggregation to convert high frequency data to lower frequency.
                    None = No change
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
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca']]
            Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[TipsYields]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TipsYields
        ----------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        due : Optional[date]
            The due date (maturation date) of the security.
        name : Optional[str]
            The name of the security.
        value : Optional[float]
            The yield value.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.tips_yields(provider='fred')
        >>> obb.fixedincome.government.tips_yields(maturity=10, provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/tips_yields",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.tips_yields",
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
    def treasury_auctions(
        self,
        security_type: Annotated[
            Optional[Literal["bill", "note", "bond", "cmb", "tips", "frn"]],
            OpenBBField(
                description="Used to only return securities of a particular type."
            ),
        ] = None,
        cusip: Annotated[
            Optional[str], OpenBBField(description="Filter securities by CUSIP.")
        ] = None,
        page_size: Annotated[
            Optional[int],
            OpenBBField(
                description="Maximum number of results to return; you must also include pagenum when using pagesize."
            ),
        ] = None,
        page_num: Annotated[
            Optional[int],
            OpenBBField(
                description="The first page number to display results for; used in combination with page size."
            ),
        ] = None,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(
                description="Start date of the data, in YYYY-MM-DD format. The default is 90 days ago."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(
                description="End date of the data, in YYYY-MM-DD format. The default is today."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["government_us"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: government_us."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Auctions.

        Parameters
        ----------
        security_type : Optional[Literal['bill', 'note', 'bond', 'cmb', 'tips', 'frn']]
            Used to only return securities of a particular type.
        cusip : Optional[str]
            Filter securities by CUSIP.
        page_size : Optional[int]
            Maximum number of results to return; you must also include pagenum when using pagesize.
        page_num : Optional[int]
            The first page number to display results for; used in combination with page size.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format. The default is 90 days ago.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format. The default is today.
        provider : Optional[Literal['government_us']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: government_us.

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
            extra : Dict[str, Any]
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

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_auctions(provider='government_us')
        >>> obb.fixedincome.government.treasury_auctions(security_type='Bill', start_date='2022-01-01', end_date='2023-01-01', provider='government_us')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_auctions",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.treasury_auctions",
                        ("government_us",),
                    )
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
                info={
                    "security_type": {
                        "government_us": {
                            "multiple_items_allowed": False,
                            "choices": ["bill", "note", "bond", "cmb", "tips", "frn"],
                        }
                    }
                },
            )
        )

    @exception_handler
    @validate
    def treasury_prices(
        self,
        date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(
                description="A specific date to get data for. Defaults to the last business day."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["government_us", "tmx"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: government_us, tmx."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Prices by date.

        Parameters
        ----------
        date : Union[date, None, str]
            A specific date to get data for. Defaults to the last business day.
        provider : Optional[Literal['government_us', 'tmx']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: government_us, tmx.
        cusip : Optional[str]
            Filter by CUSIP. (provider: government_us)
        security_type : Optional[Literal['bill', 'note', 'bond', 'tips', 'frn']]
            Filter by security type. (provider: government_us)
        govt_type : Literal['federal', 'provincial', 'municipal']
            The level of government issuer. (provider: tmx)
        issue_date_min : Optional[datetime.date]
            Filter by the minimum original issue date. (provider: tmx)
        issue_date_max : Optional[datetime.date]
            Filter by the maximum original issue date. (provider: tmx)
        last_traded_min : Optional[datetime.date]
            Filter by the minimum last trade date. (provider: tmx)
        maturity_date_min : Optional[datetime.date]
            Filter by the minimum maturity date. (provider: tmx)
        maturity_date_max : Optional[datetime.date]
            Filter by the maximum maturity date. (provider: tmx)
        use_cache : bool
            All bond data is sourced from a single JSON file that is updated daily. The file is cached for one day to eliminate downloading more than once. Caching will significantly speed up subsequent queries. To bypass, set to False. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[TreasuryPrices]
                Serializable results.
            provider : Optional[Literal['government_us', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TreasuryPrices
        --------------
        issuer_name : Optional[str]
            Name of the issuing entity.
        cusip : Optional[str]
            CUSIP of the security.
        isin : Optional[str]
            ISIN of the security.
        security_type : Optional[str]
            The type of Treasury security - i.e., Bill, Note, Bond, TIPS, FRN.
        issue_date : Optional[date]
            The original issue date of the security.
        maturity_date : Optional[date]
            The maturity date of the security.
        call_date : Optional[date]
            The call date of the security.
        bid : Optional[float]
            The bid price of the security.
        offer : Optional[float]
            The offer price of the security.
        eod_price : Optional[float]
            The end-of-day price of the security.
        last_traded_date : Optional[date]
            The last trade date of the security.
        total_trades : Optional[int]
            Total number of trades on the last traded date.
        last_price : Optional[float]
            The last price of the security.
        highest_price : Optional[float]
            The highest price for the bond on the last traded date.
        lowest_price : Optional[float]
            The lowest price for the bond on the last traded date.
        rate : Optional[float]
            The annualized interest rate or coupon of the security.
        ytm : Optional[float]
            Yield to maturity (YTM) is the rate of return anticipated on a bond if it is held until the maturity date. It takes into account the current market price, par value, coupon rate and time to maturity. It is assumed that all coupons are reinvested at the same rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_prices(provider='government_us')
        >>> obb.fixedincome.government.treasury_prices(date='2019-02-05', provider='government_us')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_prices",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.treasury_prices",
                        ("government_us", "tmx"),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def treasury_rates(
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
            Optional[Literal["federal_reserve", "fmp"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fmp."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Rates.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fmp']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fmp.

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
            extra : Dict[str, Any]
                Extra info.

        TreasuryRates
        -------------
        date : date
            The date of the data.
        week_4 : Optional[float]
            4 week Treasury bills rate (secondary market).
        month_1 : Optional[float]
            1 month Treasury rate.
        month_2 : Optional[float]
            2 month Treasury rate.
        month_3 : Optional[float]
            3 month Treasury rate.
        month_6 : Optional[float]
            6 month Treasury rate.
        year_1 : Optional[float]
            1 year Treasury rate.
        year_2 : Optional[float]
            2 year Treasury rate.
        year_3 : Optional[float]
            3 year Treasury rate.
        year_5 : Optional[float]
            5 year Treasury rate.
        year_7 : Optional[float]
            7 year Treasury rate.
        year_10 : Optional[float]
            10 year Treasury rate.
        year_20 : Optional[float]
            20 year Treasury rate.
        year_30 : Optional[float]
            30 year Treasury rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_rates(provider='fmp')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.treasury_rates",
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

    @exception_handler
    @validate
    @deprecated(
        "This endpoint will be removed in a future version. Use, `/fixedincome/government/yield_curve`, instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.4.",
        category=OpenBBDeprecationWarning,
    )
    def us_yield_curve(
        self,
        date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(
                description="A specific date to get data for. Defaults to the most recent FRED entry."
            ),
        ] = None,
        inflation_adjusted: Annotated[
            Optional[bool], OpenBBField(description="Get inflation adjusted rates.")
        ] = False,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """US Yield Curve. Get United States yield curve.

        Parameters
        ----------
        date : Union[date, None, str]
            A specific date to get data for. Defaults to the most recent FRED entry.
        inflation_adjusted : Optional[bool]
            Get inflation adjusted rates.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.

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
            extra : Dict[str, Any]
                Extra info.

        USYieldCurve
        ------------
        maturity : float
            Maturity of the treasury rate in years.
        rate : float
            Associated rate given in decimal form (0.05 is 5%)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.us_yield_curve(provider='fred')
        >>> obb.fixedincome.government.us_yield_curve(inflation_adjusted=True, provider='fred')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint will be removed in a future version. Use, `/fixedincome/government/yield_curve`, instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.4.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/fixedincome/government/us_yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.us_yield_curve",
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

    @exception_handler
    @validate
    def yield_curve(
        self,
        date: Annotated[
            Union[datetime.date, str, None, List[Union[datetime.date, str, None]]],
            OpenBBField(
                description="A specific date to get data for. By default is the current data. Multiple comma separated items allowed for provider(s): ecb, econdb, federal_reserve, fmp, fred."
            ),
        ] = None,
        chart: Annotated[
            bool,
            OpenBBField(
                description="Whether to create a chart or not, by default False."
            ),
        ] = False,
        provider: Annotated[
            Optional[Literal["ecb", "econdb", "federal_reserve", "fmp", "fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: ecb, econdb, federal_reserve, fmp, fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get yield curve data by country and date.

        Parameters
        ----------
        date : Union[date, str, None, List[Union[date, str, None]]]
            A specific date to get data for. By default is the current data. Multiple comma separated items allowed for provider(s): ecb, econdb, federal_reserve, fmp, fred.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['ecb', 'econdb', 'federal_reserve', 'fmp', 'fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: ecb, econdb, federal_reserve, fmp, fred.
        rating : Literal['aaa', 'all_ratings']
            The rating type, either 'aaa' or 'all_ratings'. (provider: ecb)
        yield_curve_type : Union[Literal['spot_rate', 'instantaneous_forward', 'par_yield'], Literal['nominal', 'real', 'breakeven', 'treasury_minus_fed_funds', 'corporate_spot', 'corporate_par']]
            The yield curve type. (provider: ecb);
            Yield curve type. Nominal and Real Rates are available daily, others are monthly. The closest date to the requested date will be returned. (provider: fred)
        use_cache : bool
            If true, cache the request for four hours. (provider: ecb, econdb)
        country : Literal['australia', 'canada', 'china', 'hong_kong', 'india', 'japan', 'mexico', 'new_zealand', 'russia', 'saudi_arabia', 'singapore', 'south_africa', 'south_korea', 'taiwan', 'thailand', 'united_kingdom', 'united_states']
            The country to get data. New Zealand, Mexico, Singapore, and Thailand have only monthly data. The nearest date to the requested one will be used. (provider: econdb)

        Returns
        -------
        OBBject
            results : List[YieldCurve]
                Serializable results.
            provider : Optional[Literal['ecb', 'econdb', 'federal_reserve', 'fmp', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        YieldCurve
        ----------
        date : Optional[date]
            The date of the data.
        maturity : str
            Maturity length of the security.
        rate : float
            The yield as a normalized percent (0.05 is 5%)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.yield_curve(provider='federal_reserve')
        >>> obb.fixedincome.government.yield_curve(date='2023-05-01,2024-05-01', provider='fmp')
        >>> obb.fixedincome.government.yield_curve(date='2023-05-01', country='united_kingdom', provider='econdb')
        >>> obb.fixedincome.government.yield_curve(provider='ecb', yield_curve_type='par_yield')
        >>> obb.fixedincome.government.yield_curve(provider='fred', yield_curve_type='real', date='2023-05-01,2024-05-01')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.yield_curve",
                        ("ecb", "econdb", "federal_reserve", "fmp", "fred"),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
                chart=chart,
                info={
                    "date": {
                        "ecb": {"multiple_items_allowed": True, "choices": None},
                        "econdb": {"multiple_items_allowed": True, "choices": None},
                        "federal_reserve": {
                            "multiple_items_allowed": True,
                            "choices": None,
                        },
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "fred": {"multiple_items_allowed": True, "choices": None},
                    }
                },
            )
        )
