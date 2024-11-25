"""SEC ETF Holings Model."""

# pylint: disable =[unused-argument,too-many-locals,too-many-branches]

from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator


class SecEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """SEC ETF Holdings Query.

    Source: https://www.sec.gov/Archives/edgar/data/
    """

    date: Optional[Union[str, dateType]] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + "  The date represents the period ending."
        + " The date entered will return the closest filing.",
        default=None,
    )
    use_cache: bool = Field(
        description="Whether or not to use cache for the request.",
        default=True,
    )


class SecEtfHoldingsData(EtfHoldingsData):
    """SEC ETF Holdings Data."""

    __alias_dict__ = {
        "name": "title",
        "weight": "pctVal",
        "value": "valUSD",
        "payoff_profile": "payoffProfile",
        "currency": "curCd",
        "asset_category": "assetCat",
        "issuer_category": "issuerCat",
        "country": "invCountry",
        "is_restricted": "isRestrictedSec",
        "fair_value_level": "fairValLevel",
        "is_cash_collateral": "isCashCollateral",
        "is_non_cash_collateral": "isNonCashCollateral",
        "is_loan_by_fund": "isLoanByFund",
        "loan_value": "loanVal",
    }

    lei: Optional[str] = Field(description="The LEI of the holding.", default=None)
    cusip: Optional[str] = Field(description="The CUSIP of the holding.", default=None)
    isin: Optional[str] = Field(description="The ISIN of the holding.", default=None)
    other_id: Optional[str] = Field(
        description="Internal identifier for the holding.", default=None
    )
    balance: Optional[float] = Field(
        description="The balance of the holding.", default=None
    )
    weight: Optional[float] = Field(
        description="The weight of the holding in ETF in %.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    value: Optional[float] = Field(
        description="The value of the holding in USD.", default=None
    )
    payoff_profile: Optional[str] = Field(
        description="The payoff profile of the holding.",
        default=None,
    )
    units: Optional[Union[float, str]] = Field(
        description="The units of the holding.", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the holding.", default=None
    )
    asset_category: Optional[str] = Field(
        description="The asset category of the holding.", default=None
    )
    issuer_category: Optional[str] = Field(
        description="The issuer category of the holding.",
        default=None,
    )
    country: Optional[str] = Field(
        description="The country of the holding.", default=None
    )
    is_restricted: Optional[str] = Field(
        description="Whether the holding is restricted.",
        default=None,
    )
    fair_value_level: Optional[int] = Field(
        description="The fair value level of the holding.",
        default=None,
    )
    is_cash_collateral: Optional[str] = Field(
        description="Whether the holding is cash collateral.",
        default=None,
    )
    is_non_cash_collateral: Optional[str] = Field(
        description="Whether the holding is non-cash collateral.",
        default=None,
    )
    is_loan_by_fund: Optional[str] = Field(
        description="Whether the holding is loan by fund.",
        default=None,
    )
    loan_value: Optional[float] = Field(
        description="The loan value of the holding.",
        default=None,
    )
    issuer_conditional: Optional[str] = Field(
        description="The issuer conditions of the holding.", default=None
    )
    asset_conditional: Optional[str] = Field(
        description="The asset conditions of the holding.", default=None
    )
    maturity_date: Optional[dateType] = Field(
        description="The maturity date of the debt security.", default=None
    )
    coupon_kind: Optional[str] = Field(
        description="The type of coupon for the debt security.", default=None
    )
    rate_type: Optional[str] = Field(
        description="The type of rate for the debt security, floating or fixed.",
        default=None,
    )
    annualized_return: Optional[float] = Field(
        description="The annualized return on the debt security.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    is_default: Optional[str] = Field(
        description="If the debt security is defaulted.", default=None
    )
    in_arrears: Optional[str] = Field(
        description="If the debt security is in arrears.", default=None
    )
    is_paid_kind: Optional[str] = Field(
        description="If the debt security payments are paid in kind.", default=None
    )
    derivative_category: Optional[str] = Field(
        description="The derivative category of the holding.", default=None
    )
    counterparty: Optional[str] = Field(
        description="The counterparty of the derivative.", default=None
    )
    underlying_name: Optional[str] = Field(
        description="The name of the underlying asset associated with the derivative.",
        default=None,
    )
    option_type: Optional[str] = Field(description="The type of option.", default=None)
    derivative_payoff: Optional[str] = Field(
        description="The payoff profile of the derivative.", default=None
    )
    expiry_date: Optional[dateType] = Field(
        description="The expiry or termination date of the derivative.", default=None
    )
    exercise_price: Optional[float] = Field(
        description="The exercise price of the option.", default=None
    )
    exercise_currency: Optional[str] = Field(
        description="The currency of the option exercise price.", default=None
    )
    shares_per_contract: Optional[float] = Field(
        description="The number of shares per contract.", default=None
    )
    delta: Optional[Union[str, float]] = Field(
        description="The delta of the option.", default=None
    )
    rate_type_rec: Optional[str] = Field(
        description="The type of rate for receivable portion of the swap.", default=None
    )
    receive_currency: Optional[str] = Field(
        description="The receive currency of the swap.", default=None
    )
    upfront_receive: Optional[float] = Field(
        description="The upfront amount received of the swap.", default=None
    )
    floating_rate_index_rec: Optional[str] = Field(
        description="The floating rate index for receivable portion of the swap.",
        default=None,
    )
    floating_rate_spread_rec: Optional[float] = Field(
        description="The floating rate spread for reveivable portion of the swap.",
        default=None,
    )
    rate_tenor_rec: Optional[str] = Field(
        description="The rate tenor for receivable portion of the swap.", default=None
    )
    rate_tenor_unit_rec: Optional[Union[str, int]] = Field(
        description="The rate tenor unit for receivable portion of the swap.",
        default=None,
    )
    reset_date_rec: Optional[str] = Field(
        description="The reset date for receivable portion of the swap.", default=None
    )
    reset_date_unit_rec: Optional[Union[str, int]] = Field(
        description="The reset date unit for receivable portion of the swap.",
        default=None,
    )
    rate_type_pmnt: Optional[str] = Field(
        description="The type of rate for payment portion of the swap.", default=None
    )
    payment_currency: Optional[str] = Field(
        description="The payment currency of the swap.", default=None
    )
    upfront_payment: Optional[float] = Field(
        description="The upfront amount received of the swap.", default=None
    )
    floating_rate_index_pmnt: Optional[str] = Field(
        description="The floating rate index for payment portion of the swap.",
        default=None,
    )
    floating_rate_spread_pmnt: Optional[float] = Field(
        description="The floating rate spread for payment portion of the swap.",
        default=None,
    )
    rate_tenor_pmnt: Optional[str] = Field(
        description="The rate tenor for payment portion of the swap.", default=None
    )
    rate_tenor_unit_pmnt: Optional[Union[str, int]] = Field(
        description="The rate tenor unit for payment portion of the swap.", default=None
    )
    reset_date_pmnt: Optional[str] = Field(
        description="The reset date for payment portion of the swap.", default=None
    )
    reset_date_unit_pmnt: Optional[Union[str, int]] = Field(
        description="The reset date unit for payment portion of the swap.", default=None
    )
    repo_type: Optional[str] = Field(description="The type of repo.", default=None)
    is_cleared: Optional[str] = Field(
        description="If the repo is cleared.", default=None
    )
    is_tri_party: Optional[str] = Field(
        description="If the repo is tri party.", default=None
    )
    principal_amount: Optional[float] = Field(
        description="The principal amount of the repo.", default=None
    )
    principal_currency: Optional[str] = Field(
        description="The currency of the principal amount.", default=None
    )
    collateral_type: Optional[str] = Field(
        description="The collateral type of the repo.", default=None
    )
    collateral_amount: Optional[float] = Field(
        description="The collateral amount of the repo.", default=None
    )
    collateral_currency: Optional[str] = Field(
        description="The currency of the collateral amount.", default=None
    )
    exchange_currency: Optional[str] = Field(
        description="The currency of the exchange rate.", default=None
    )
    exchange_rate: Optional[float] = Field(
        description="The exchange rate.", default=None
    )
    currency_sold: Optional[str] = Field(
        description="The currency sold in a Forward Derivative.",
        default=None,
    )
    currency_amount_sold: Optional[float] = Field(
        description="The amount of currency sold in a Forward Derivative.",
        default=None,
    )
    currency_bought: Optional[str] = Field(
        description="The currency bought in a Forward Derivative.",
        default=None,
    )
    currency_amount_bought: Optional[float] = Field(
        description="The amount of currency bought in a Forward Derivative.",
        default=None,
    )
    notional_amount: Optional[float] = Field(
        description="The notional amount of the derivative.", default=None
    )
    notional_currency: Optional[str] = Field(
        description="The currency of the derivative's notional amount.", default=None
    )
    unrealized_gain: Optional[float] = Field(
        description="The unrealized gain or loss on the derivative.", default=None
    )

    @field_validator("weight", "annualized_return", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent values."""
        return float(v) / 100 if v else None

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class SecEtfHoldingsFetcher(
    Fetcher[
        SecEtfHoldingsQueryParams,
        List[SecEtfHoldingsData],
    ]
):
    """SEC ETF Holdings."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecEtfHoldingsQueryParams:
        """Transform the query."""
        params["symbol"] = params["symbol"].upper()
        return SecEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import xmltodict  # noqa
        from aiohttp_client_cache import SQLiteBackend  # noqa
        from aiohttp_client_cache.session import CachedSession  # noqa
        from openbb_core.app.utils import get_user_cache_directory  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa
        from openbb_sec.utils.helpers import HEADERS, get_nport_candidates  # noqa
        from pandas import DataFrame, Series, to_datetime  # noqa

        # Implement a retry mechanism in case of RemoteDisconnected Error.
        retries = 3
        for i in range(retries):
            filings = []
            try:
                filings = await get_nport_candidates(
                    symbol=query.symbol, use_cache=query.use_cache
                )
                if filings:
                    break
            except Exception as e:
                if i < retries - 1:
                    warn(f"Error: {e}. Retrying...")
                    await asyncio.sleep(1)
                    continue
                raise e
        filing_candidates = DataFrame.from_records(filings)
        if filing_candidates.empty:
            raise OpenBBError(f"No N-Port records found for {query.symbol}.")
        dates = filing_candidates.period_ending.to_list()
        new_date: str = ""
        if query.date is not None:
            date = query.date
            # Gets the URL for the nearest date to the requested date.
            __dates = Series(to_datetime(dates))
            __date = to_datetime(date)
            __nearest = DataFrame(__dates - __date)
            __nearest_date = abs(__nearest[0].astype("int64")).idxmin()
            new_date = __dates[__nearest_date].strftime("%Y-%m-%d")
            date = new_date if new_date else date
            warn(f"Closest filing date to, {query.date}, is the period ending: {date}")
            filing_url = filing_candidates[filing_candidates["period_ending"] == date][
                "primary_doc"
            ].values[0]
        else:
            filing_url = filing_candidates["primary_doc"].values[0]

        async def callback(response, session):
            """Response callback for the request."""
            return await response.read()

        response: Union[dict, List[dict]] = []
        if query.use_cache is True:
            cache_dir = f"{get_user_cache_directory()}/http/sec_etf"
            async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
                try:
                    response = await amake_request(
                        filing_url, headers=HEADERS, session=session, response_callback=callback  # type: ignore
                    )
                finally:
                    await session.close()
        else:
            response = await amake_request(
                filing_url, headers=HEADERS, response_callback=callback  # type: ignore
            )
        results = xmltodict.parse(response)

        return results

    # pylint: disable=too-many-statements
    @staticmethod
    def transform_data(  # noqa: PLR0912
        query: SecEtfHoldingsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[SecEtfHoldingsData]]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, to_datetime
        from pandas.tseries.offsets import MonthEnd

        if not data:
            raise EmptyDataError(f"No data was returned for the symbol, {query.symbol}")
        results = []

        response = data

        # Parse the response if it is a NPORT-P filing.
        if (
            "edgarSubmission" in response
            and "formData" in response["edgarSubmission"]
            and response["edgarSubmission"]["headerData"]["submissionType"] == "NPORT-P"
            and "invstOrSecs" in response["edgarSubmission"]["formData"]
            and "invstOrSec" in response["edgarSubmission"]["formData"]["invstOrSecs"]
        ):
            df = DataFrame.from_records(
                response["edgarSubmission"]["formData"]["invstOrSecs"]["invstOrSec"]
            )
            # Conditionally flatten deeply nested values.
            for i in df.index:
                if "isin" in df.iloc[i]["identifiers"]:
                    df.loc[i, "isin"] = df.iloc[i]["identifiers"]["isin"].get("@value")

                if (
                    "other" in df.iloc[i]["identifiers"]
                    and "@value" in df.iloc[i]["identifiers"]["other"]
                ):
                    df.loc[i, "other_id"] = df.iloc[i]["identifiers"]["other"].get(
                        "@value"
                    )

                if "securityLending" in df.iloc[i]:
                    security_lending = df.iloc[i]["securityLending"]
                    if "loanByFundCondition" in security_lending:
                        loan_by_fund_condition = security_lending["loanByFundCondition"]
                        df.loc[i, "isLoanByFund"] = loan_by_fund_condition.get(
                            "@isLoanByFund"
                        )
                        df.loc[i, "loanVal"] = loan_by_fund_condition.get("@loanVal")
                    if "isCashCollateral" in security_lending:
                        df.loc[i, "isCashCollateral"] = security_lending.get(
                            "isCashCollateral"
                        )
                    if "isNonCashCollateral" in security_lending:
                        df.loc[i, "isNonCashCollateral"] = security_lending.get(
                            "isNonCashCollateral"
                        )

                if "debtSec" in df.iloc[i] and isinstance(df.loc[i]["debtSec"], dict):
                    debt_sec = df.iloc[i]["debtSec"]
                    df.loc[i, "maturity_date"] = debt_sec.get("maturityDt")
                    df.loc[i, "coupon_kind"] = debt_sec.get("couponKind")
                    df.loc[i, "annualized_return"] = debt_sec.get("annualizedRt")
                    df.loc[i, "is_default"] = debt_sec.get("isDefault")
                    df.loc[i, "in_arrears"] = debt_sec.get("areIntrstPmntsInArrs")
                    df.loc[i, "is_paid_kind"] = debt_sec.get("isPaidKind")

                if "issuerConditional" in df.iloc[i] and isinstance(
                    df.iloc[i]["issuerConditional"], dict
                ):
                    df.loc[i, "issuer_conditional"] = df.iloc[i][
                        "issuerConditional"
                    ].get("@desc")

                if "assetConditional" in df.iloc[i] and isinstance(
                    df.iloc[i]["assetConditional"], dict
                ):
                    df.loc[i, "asset_conditional"] = df.iloc[i]["assetConditional"].get(
                        "@desc"
                    )

                if "derivativeInfo" in df.iloc[i] and isinstance(
                    df.iloc[i]["derivativeInfo"], dict
                ):
                    derivative_info = df.iloc[i]["derivativeInfo"]

                    if "optionSwaptionWarrantDeriv" in derivative_info:
                        option_swaption_warrant_deriv = derivative_info[
                            "optionSwaptionWarrantDeriv"
                        ]
                        df.loc[i, "derivative_category"] = (
                            option_swaption_warrant_deriv.get("@derivCat")
                        )
                        df.loc[i, "counterparty"] = option_swaption_warrant_deriv[
                            "counterparties"
                        ].get("counterpartyName")
                        df.loc[i, "lei"] = option_swaption_warrant_deriv[
                            "counterparties"
                        ].get("counterpartyLei")
                        df.loc[i, "underlying_name"] = (
                            option_swaption_warrant_deriv["descRefInstrmnt"]
                            .get("otherRefInst", {})
                            .get("issueTitle")
                        )
                        df.loc[i, "underlying_name"] = option_swaption_warrant_deriv[
                            "descRefInstrmnt"
                        ].get("nestedDerivInfo", {}).get("fwdDeriv", {}).get(
                            "derivAddlInfo", {}
                        ).get(
                            "title"
                        ) or option_swaption_warrant_deriv[
                            "descRefInstrmnt"
                        ].get(
                            "otherRefInst", {}
                        ).get(
                            "issueTitle"
                        )
                        df.loc[i, "option_type"] = option_swaption_warrant_deriv.get(
                            "putOrCall"
                        )
                        df.loc[i, "derivative_payoff"] = (
                            option_swaption_warrant_deriv.get("writtenOrPur")
                        )
                        df.loc[i, "expiry_date"] = option_swaption_warrant_deriv.get(
                            "expDt"
                        )
                        df.loc[i, "exercise_price"] = option_swaption_warrant_deriv.get(
                            "exercisePrice"
                        )
                        df.loc[i, "exercise_currency"] = (
                            option_swaption_warrant_deriv.get("exercisePriceCurCd")
                        )
                        df.loc[i, "shares_per_contract"] = (
                            option_swaption_warrant_deriv.get("shareNo")
                        )
                        if option_swaption_warrant_deriv.get("delta") != "XXXX":
                            df.loc[i, "delta"] = option_swaption_warrant_deriv.get(
                                "delta"
                            )
                        df.loc[i, "unrealized_gain"] = float(
                            option_swaption_warrant_deriv.get("unrealizedAppr")
                        )

                    if "futrDeriv" in derivative_info:
                        futr_deriv = derivative_info["futrDeriv"]
                        df.loc[i, "derivative_category"] = futr_deriv.get("@derivCat")
                        if isinstance(futr_deriv.get("counterparties"), dict):
                            df.loc[i, "counterparty"] = futr_deriv[
                                "counterparties"
                            ].get("counterpartyName")
                            df.loc[i, "lei"] = futr_deriv["counterparties"].get(
                                "counterpartyLei"
                            )
                        df.loc[i, "underlying_name"] = (
                            futr_deriv["descRefInstrmnt"]
                            .get("indexBasketInfo", {})
                            .get("indexName")
                        )
                        df.loc[i, "other_id"] = (
                            futr_deriv["descRefInstrmnt"]
                            .get("indexBasketInfo", {})
                            .get("indexIdentifier")
                        )
                        df.loc[i, "derivative_payoff"] = futr_deriv.get("payOffProf")
                        df.loc[i, "expiry_date"] = futr_deriv.get(
                            "expDt"
                        ) or futr_deriv.get("expDate")
                        df.loc[i, "notional_amount"] = float(
                            futr_deriv.get("notionalAmt")
                        )
                        df.loc[i, "notional_currency"] = futr_deriv.get("curCd")
                        df.loc[i, "unrealized_gain"] = float(
                            futr_deriv.get("unrealizedAppr")
                        )

                    if "fwdDeriv" in derivative_info:
                        fwd_deriv = derivative_info["fwdDeriv"]
                        df.loc[i, "derivative_category"] = fwd_deriv.get("@derivCat")
                        df.loc[i, "counterparty"] = fwd_deriv["counterparties"].get(
                            "counterpartyName"
                        )
                        df.loc[i, "currency_sold"] = fwd_deriv.get("curSold")
                        df.loc[i, "currency_amount_sold"] = float(
                            fwd_deriv.get("amtCurSold")
                        )
                        df.loc[i, "currency_bought"] = fwd_deriv.get("curPur")
                        df.loc[i, "currency_amount_bought"] = float(
                            fwd_deriv.get("amtCurPur")
                        )
                        df.loc[i, "expiry_date"] = fwd_deriv.get("settlementDt")
                        df.loc[i, "unrealized_gain"] = float(
                            fwd_deriv.get("unrealizedAppr")
                        )

                    if "swapDeriv" in df.iloc[i]["derivativeInfo"]:
                        swap_deriv = df.iloc[i]["derivativeInfo"]["swapDeriv"]
                        df.loc[i, "derivative_category"] = swap_deriv.get("@derivCat")
                        df.loc[i, "counterparty"] = swap_deriv["counterparties"].get(
                            "counterpartyName"
                        )
                        df.loc[i, "lei"] = swap_deriv["counterparties"].get(
                            "counterpartyLei"
                        )
                        if "otherRefInst" in swap_deriv["descRefInstrmnt"]:
                            df.loc[i, "underlying_name"] = swap_deriv[
                                "descRefInstrmnt"
                            ]["otherRefInst"].get("issueTitle")
                        if "indexBasketInfo" in swap_deriv["descRefInstrmnt"]:
                            df.loc[i, "underlying_name"] = swap_deriv[
                                "descRefInstrmnt"
                            ]["indexBasketInfo"].get("indexName")
                            df.loc[i, "other_id"] = swap_deriv["descRefInstrmnt"][
                                "indexBasketInfo"
                            ].get("indexIdentifier")
                        df.loc[i, "swap_description"] = (
                            swap_deriv["otherRecDesc"].get("#text")
                            if "otherRecDesc" in swap_deriv["descRefInstrmnt"]
                            else None
                        )
                        if "floatingRecDesc" in swap_deriv:
                            df.loc[i, "rate_type_rec"] = swap_deriv[
                                "floatingRecDesc"
                            ].get("@fixedOrFloating")
                            df.loc[i, "floating_rate_index_rec"] = swap_deriv[
                                "floatingRecDesc"
                            ].get("@floatingRtIndex")
                            df.loc[i, "floating_rate_spread_rec"] = float(
                                swap_deriv["floatingRecDesc"].get("@floatingRtSpread")
                            )
                            df.loc[i, "payment_amount_rec"] = float(
                                swap_deriv["floatingRecDesc"].get("@pmntAmt")
                            )
                            df.loc[i, "rate_tenor_rec"] = swap_deriv["floatingRecDesc"][
                                "rtResetTenors"
                            ]["rtResetTenor"].get("@rateTenor")
                            df.loc[i, "rate_tenor_unit_rec"] = swap_deriv[
                                "floatingRecDesc"
                            ]["rtResetTenors"]["rtResetTenor"].get("@rateTenorUnit")
                            df.loc[i, "reset_date_rec"] = swap_deriv["floatingRecDesc"][
                                "rtResetTenors"
                            ]["rtResetTenor"].get("@resetDt")
                            df.loc[i, "reset_date_unit_rec"] = swap_deriv[
                                "floatingRecDesc"
                            ]["rtResetTenors"]["rtResetTenor"].get("@resetDtUnit")
                        if "floatingPmntDesc" in swap_deriv:
                            df.loc[i, "rate_type_pmnt"] = swap_deriv[
                                "floatingPmntDesc"
                            ].get("@fixedOrFloating")
                            df.loc[i, "floating_rate_index_pmnt"] = swap_deriv[
                                "floatingPmntDesc"
                            ].get("@floatingRtIndex")
                            df.loc[i, "floating_rate_spread_pmnt"] = float(
                                swap_deriv["floatingPmntDesc"].get("@floatingRtSpread")
                            )
                            df.loc[i, "payment_amount_pmnt"] = float(
                                swap_deriv["floatingPmntDesc"].get("@pmntAmt")
                            )
                            df.loc[i, "rate_tenor_pmnt"] = swap_deriv[
                                "floatingPmntDesc"
                            ]["rtResetTenors"]["rtResetTenor"].get("@rateTenor")
                            df.loc[i, "rate_tenor_unit_pmnt"] = swap_deriv[
                                "floatingPmntDesc"
                            ]["rtResetTenors"]["rtResetTenor"].get("@rateTenorUnit")
                            df.loc[i, "reset_date_pmnt"] = swap_deriv[
                                "floatingPmntDesc"
                            ]["rtResetTenors"]["rtResetTenor"].get("@resetDt")
                            df.loc[i, "reset_date_unit_rec"] = swap_deriv[
                                "floatingPmntDesc"
                            ]["rtResetTenors"]["rtResetTenor"].get("@resetDtUnit")
                        df.loc[i, "expiry_date"] = swap_deriv.get("terminationDt")
                        df.loc[i, "upfront_payment"] = float(
                            swap_deriv.get("upfrontPmnt")
                        )
                        df.loc[i, "payment_currency"] = swap_deriv.get("pmntCurCd")
                        df.loc[i, "upfront_receive"] = float(
                            swap_deriv.get("upfrontRcpt")
                        )
                        df.loc[i, "receive_currency"] = swap_deriv.get("rcptCurCd")
                        df.loc[i, "notional_amount"] = float(
                            swap_deriv.get("notionalAmt")
                        )
                        df.loc[i, "notional_currency"] = swap_deriv.get("curCd")
                        df.loc[i, "unrealized_gain"] = float(
                            swap_deriv.get("unrealizedAppr")
                        )

                if "repurchaseAgrmt" in df.iloc[i] and isinstance(
                    df.iloc[i]["repurchaseAgrmt"], dict
                ):
                    repurchase_agrmt = df.iloc[i]["repurchaseAgrmt"]
                    df.loc[i, "repo_type"] = repurchase_agrmt.get("transCat")

                    if "clearedCentCparty" in repurchase_agrmt and isinstance(
                        repurchase_agrmt["clearedCentCparty"], dict
                    ):
                        cleared_cent_cparty = repurchase_agrmt["clearedCentCparty"]
                        df.loc[i, "is_cleared"] = cleared_cent_cparty.get("@isCleared")
                        df.loc[i, "counterparty"] = cleared_cent_cparty.get(
                            "@centralCounterparty"
                        )
                    df.loc[i, "is_tri_party"] = repurchase_agrmt.get("isTriParty")
                    df.loc[i, "annualized_return"] = repurchase_agrmt.get(
                        "repurchaseRt"
                    )
                    df.loc[i, "maturity_date"] = repurchase_agrmt.get("maturityDt")

                    if (
                        "repurchaseCollaterals" in repurchase_agrmt
                        and "repurchaseCollateral"
                        in repurchase_agrmt["repurchaseCollaterals"]
                    ):
                        repurchase_collateral = repurchase_agrmt[
                            "repurchaseCollaterals"
                        ]["repurchaseCollateral"]
                        df.loc[i, "principal_amount"] = float(
                            repurchase_collateral.get("principalAmt")
                        )
                        df.loc[i, "principal_currency"] = repurchase_collateral.get(
                            "@principalCd"
                        )
                        df.loc[i, "collateral_amount"] = float(
                            repurchase_collateral.get("collateralVal")
                        )
                        df.loc[i, "collateral_currency"] = repurchase_collateral.get(
                            "@collateralCd"
                        )
                        df.loc[i, "collateral_type"] = repurchase_collateral.get(
                            "@invstCat"
                        )

                if "currencyConditional" in df.iloc[i] and isinstance(
                    df.iloc[i]["currencyConditional"], dict
                ):
                    currency_conditional = df.iloc[i]["currencyConditional"]
                    df.loc[i, "exchange_currency"] = currency_conditional.get("@curCd")
                    df.loc[i, "exchange_rate"] = currency_conditional.get("@exchangeRt")

            # Drop the flattened columns
            to_drop = [
                "identifiers",
                "securityLending",
                "issuerConditional",
                "assetConditional",
                "debtSec",
                "currencyConditional",
                "derivativeInfo",
                "repurchaseAgrmt",
            ]
            for col in to_drop:
                if col in df.columns:
                    df = df.drop(col, axis=1)

            df["pctVal"] = df["pctVal"].astype(float)
            results = (
                df.fillna("N/A")
                .replace("N/A", None)
                .sort_values(by="pctVal", ascending=False)
                .to_dict(orient="records")
            )
        # Extract additional information from the form that doesn't belong in the holdings table.
        metadata = {}
        month_1: str = ""
        month_2: str = ""
        month_3: str = ""
        try:
            gen_info = response["edgarSubmission"]["formData"].get("genInfo", {})  # type: ignore
            if gen_info:
                metadata["fund_name"] = gen_info.get("seriesName")
                metadata["series_id"] = gen_info.get("seriesId")
                metadata["lei"] = gen_info.get("seriesLei")
                metadata["period_ending"] = gen_info.get("repPdDate")
                metadata["fiscal_year_end"] = gen_info.get("repPdEnd")
                current_month = to_datetime(metadata["period_ending"])
                month_1 = (current_month - MonthEnd(2)).date().strftime("%Y-%m-%d")
                month_2 = (current_month - MonthEnd(1)).date().strftime("%Y-%m-%d")
                month_3 = current_month.strftime("%Y-%m-%d")
            fund_info = response["edgarSubmission"]["formData"].get("fundInfo", {})  # type: ignore
            if fund_info:
                metadata["total_assets"] = float(fund_info.pop("totAssets", None))
                metadata["total_liabilities"] = float(fund_info.pop("totLiabs", None))
                metadata["net_assets"] = float(fund_info.pop("netAssets", None))
                metadata["cash_and_equivalents"] = fund_info.pop(
                    "cshNotRptdInCorD", None
                )
                return_info = fund_info["returnInfo"]["monthlyTotReturns"].get(
                    "monthlyTotReturn", {}
                )
                returns = {
                    month_1: float(return_info.get("@rtn1")) / 100,
                    month_2: float(return_info.get("@rtn2")) / 100,
                    month_3: float(return_info.get("@rtn3")) / 100,
                }
                metadata["returns"] = returns
                flow = {
                    month_1: {
                        "creation": float(fund_info["mon1Flow"].get("@sales", None)),
                        "redemption": float(
                            fund_info["mon1Flow"].get("@redemption", None)
                        ),
                    },
                    month_2: {
                        "creation": float(fund_info["mon2Flow"].get("@sales", None)),
                        "redemption": float(
                            fund_info["mon2Flow"].get("@redemption", None)
                        ),
                    },
                    month_3: {
                        "creation": float(fund_info["mon3Flow"].get("@sales")),
                        "redemption": float(
                            fund_info["mon3Flow"].get("@redemption", None)
                        ),
                    },
                }
                metadata["flow"] = flow
                gains = {
                    month_1: {
                        "realized": float(
                            fund_info["returnInfo"]["othMon1"].get(
                                "@netRealizedGain", None
                            )
                        ),
                        "unrealized": float(
                            fund_info["returnInfo"]["othMon1"].get(
                                "@netUnrealizedAppr", None
                            )
                        ),
                    },
                    month_2: {
                        "realized": float(
                            fund_info["returnInfo"]["othMon2"].get(
                                "@netRealizedGain", None
                            )
                        ),
                        "unrealized": float(
                            fund_info["returnInfo"]["othMon2"].get(
                                "@netUnrealizedAppr", None
                            )
                        ),
                    },
                    month_3: {
                        "realized": float(
                            fund_info["returnInfo"]["othMon3"].get(
                                "@netRealizedGain", None
                            )
                        ),
                        "unrealized": float(
                            fund_info["returnInfo"]["othMon3"].get(
                                "@netUnrealizedAppr", None
                            )
                        ),
                    },
                }
                metadata["gains"] = gains
                _borrowers = fund_info["borrowers"].get("borrower", [])
                if _borrowers:
                    borrowers = [
                        {
                            "name": d["@name"],
                            "lei": d["@lei"],
                            "value": float(d["@aggrVal"]),
                        }
                        for d in _borrowers
                    ]
                    metadata["borrowers"] = borrowers
        except Exception as e:  # pylint: disable=W0718
            warn(f"Error extracting metadata: {e}")
        return AnnotatedResult(
            result=[SecEtfHoldingsData.model_validate(d) for d in results],
            metadata=metadata,
        )
