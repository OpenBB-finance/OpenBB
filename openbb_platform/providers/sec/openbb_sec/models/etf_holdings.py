"""SEC ETF Holings Model."""

import warnings
from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests
import xmltodict
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_sec.utils.helpers import HEADERS, get_nport_candidates, sec_session_etf
from pydantic import Field

_warn = warnings.warn


class SecEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """SEC ETF Holdings Query.

    Source: https://www.sec.gov/Archives/edgar/data/
    """

    date: Optional[Union[str, dateType]] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + "  The date represents the period ending.  The date entered will return the closest filing.",
        default=None,
    )
    use_cache: bool = Field(
        description="Whether or not to use cache for the request.",
        default=True,
    )


class SecEtfHoldingsData(EtfHoldingsData):
    """SEC ETF Holdings Data."""

    __alias_dict__ = {"name": "title"}

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
        alias="pctVal",
        default=None,
    )
    value: Optional[float] = Field(
        description="The value of the holding in USD.", alias="valUSD", default=None
    )
    payoff_profile: Optional[str] = Field(
        description="The payoff profile of the holding.",
        alias="payoffProfile",
        default=None,
    )
    units: Optional[Union[float, str]] = Field(
        description="The units of the holding.", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the holding.", alias="curCd", default=None
    )
    asset_category: Optional[str] = Field(
        description="The asset category of the holding.", alias="assetCat", default=None
    )
    issuer_category: Optional[str] = Field(
        description="The issuer category of the holding.",
        alias="issuerCat",
        default=None,
    )
    country: Optional[str] = Field(
        description="The country of the holding.", alias="invCountry", default=None
    )
    is_restricted: Optional[str] = Field(
        description="Whether the holding is restricted.",
        alias="isRestrictedSec",
        default=None,
    )
    fair_value_level: Optional[int] = Field(
        description="The fair value level of the holding.",
        alias="fairValLevel",
        default=None,
    )
    is_cash_collateral: Optional[str] = Field(
        description="Whether the holding is cash collateral.",
        alias="isCashCollateral",
        default=None,
    )
    is_non_cash_collateral: Optional[str] = Field(
        description="Whether the holding is non-cash collateral.",
        alias="isNonCashCollateral",
        default=None,
    )
    is_loan_by_fund: Optional[str] = Field(
        description="Whether the holding is loan by fund.",
        alias="isLoanByFund",
        default=None,
    )
    loan_value: Optional[float] = Field(
        description="The loan value of the holding.",
        alias="loanVal",
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
        description="The annualized return on the debt security.", default=None
    )
    is_default: Optional[str] = Field(
        description="If the debt security is defaulted.", default=None
    )
    in_arrears: Optional[str] = Field(
        description="If the debt security is in arrears.", default=None
    )
    is_paid_kind: Optional[str] = Field(
        description="If the debt security payments are are paid in kind.", default=None
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
    unrealized_gain: Optional[float] = Field(
        description="The unrealized gain or loss on the derivative.", default=None
    )
    notional_amount: Optional[float] = Field(
        description="The notional amount of the derivative.", default=None
    )
    notional_currency: Optional[str] = Field(
        description="The currency of the derivative's notional amount.", default=None
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


class SecEtfHoldingsFetcher(
    Fetcher[
        SecEtfHoldingsQueryParams,
        List[SecEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecEtfHoldingsQueryParams:
        """Transform the query."""
        params["symbol"] = params["symbol"].upper()
        return SecEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the SEC endpoint."""

        filing_candidates = pd.DataFrame.from_records(
            get_nport_candidates(symbol=query.symbol, use_cache=query.use_cache)
        )
        if filing_candidates.empty:
            raise ValueError(f"No N-Port records found for {query.symbol}.")
        dates = filing_candidates["period_ending"].to_list()
        new_date: str = ""
        if query.date is not None:
            date = query.date
            # Gets the URL for the nearest date to the requested date.
            __dates = pd.Series(pd.to_datetime(dates))
            __date = pd.to_datetime(date)
            __nearest = pd.DataFrame(__dates - __date)
            __nearest_date = abs(__nearest[0].astype("int64")).idxmin()
            new_date = __dates[__nearest_date].strftime("%Y-%m-%d")
            date = new_date if new_date else date
            _warn(f"Closest filing date to, {query.date}, is the period ending: {date}")
            filing_url = filing_candidates[filing_candidates["period_ending"] == date][
                "primary_doc"
            ].values[0]
        else:
            filing_url = filing_candidates["primary_doc"].values[0]
            period_ending = filing_candidates["period_ending"].values[0]
            _warn(f"The latest filing is for the period ending: {period_ending}")
        _warn(f"Source Document: {filing_url}")
        r = (
            sec_session_etf.get(filing_url, headers=HEADERS, timeout=5)
            if query.use_cache
            else requests.get(filing_url, headers=HEADERS, timeout=5)
        )
        if r.status_code != 200:
            raise RuntimeError(f"Request failed with status code {r.status_code}")
        response = xmltodict.parse(r.content)

        return response

    @staticmethod
    def transform_data(  # noqa: PLR0912
        query: SecEtfHoldingsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[SecEtfHoldingsData]:
        """Transform the data."""
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
            df = pd.DataFrame.from_records(
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
                    if "loanByFundCondition" in df.iloc[i]["securityLending"]:
                        df.loc[i, "isLoanByFund"] = df.iloc[i]["securityLending"][
                            "loanByFundCondition"
                        ].get("@isLoanByFund")
                        df.loc[i, "loanVal"] = df.iloc[i]["securityLending"][
                            "loanByFundCondition"
                        ].get("@loanVal")
                    if "isCashCollateral" in df.iloc[i]["securityLending"]:
                        df.loc[i, "isCashCollateral"] = df.iloc[i][
                            "securityLending"
                        ].get("isCashCollateral")
                    if "isNonCashCollateral" in df.iloc[i]["securityLending"]:
                        df.loc[i, "isNonCashCollateral"] = df.iloc[i][
                            "securityLending"
                        ].get("isNonCashCollateral")
                if "debtSec" in df.iloc[i] and isinstance(df.loc[i]["debtSec"], dict):
                    df.loc[i, "maturity_date"] = df.iloc[i]["debtSec"].get("maturityDt")
                    df.loc[i, "coupon_kind"] = df.iloc[i]["debtSec"].get("couponKind")
                    df.loc[i, "annualized_return"] = df.iloc[i]["debtSec"].get(
                        "annualizedRt"
                    )
                    df.loc[i, "is_default"] = df.iloc[i]["debtSec"].get("isDefault")
                    df.loc[i, "in_arrears"] = df.iloc[i]["debtSec"].get(
                        "areIntrstPmntsInArrs"
                    )
                    df.loc[i, "is_paid_kind"] = df.iloc[i]["debtSec"].get("isPaidKind")
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
                    if "optionSwaptionWarrantDeriv" in df.iloc[i]["derivativeInfo"]:
                        df.loc[i, "derivative_category"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("@derivCat")
                        df.loc[i, "counterparty"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ]["counterparties"].get("counterpartyName")
                        if (
                            "otherRefInst"
                            in df.iloc[i]["derivativeInfo"][
                                "optionSwaptionWarrantDeriv"
                            ]["descRefInstrmnt"]
                        ):
                            df.loc[i, "underlying_name"] = df.iloc[i]["derivativeInfo"][
                                "optionSwaptionWarrantDeriv"
                            ]["descRefInstrmnt"]["otherRefInst"].get("issueTitle")
                        if (
                            "nestedDerivInfo"
                            in df.iloc[i]["derivativeInfo"][
                                "optionSwaptionWarrantDeriv"
                            ]["descRefInstrmnt"]
                        ):
                            df.loc[i, "underlying_name"] = df.iloc[i]["derivativeInfo"][
                                "optionSwaptionWarrantDeriv"
                            ]["descRefInstrmnt"]["nestedDerivInfo"]["fwdDeriv"][
                                "derivAddlInfo"
                            ].get(
                                "title"
                            )
                        df.loc[i, "option_type"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("putOrCall")
                        df.loc[i, "derivative_payoff"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("writtenOrPur")
                        df.loc[i, "expiry_date"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("expDt")
                        df.loc[i, "exercise_price"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("exercisePrice")
                        df.loc[i, "exercise_currency"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("exercisePriceCurCd")
                        df.loc[i, "shares_per_contract"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("shareNo")
                        df.loc[i, "delta"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("delta")
                        df.loc[i, "unrealized_gain"] = df.iloc[i]["derivativeInfo"][
                            "optionSwaptionWarrantDeriv"
                        ].get("unrealizedAppr")
                    if "futrDeriv" in df.iloc[i]["derivativeInfo"]:
                        df.loc[i, "derivative_category"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ].get("@derivCat")
                        df.loc[i, "counterparty"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ]["counterparties"].get("counterpartyName")
                        if (
                            "indexBasketInfo"
                            in df.iloc[i]["derivativeInfo"]["futrDeriv"][
                                "descRefInstrmnt"
                            ]
                        ):
                            df.loc[i, "underlying_name"] = df.iloc[i]["derivativeInfo"][
                                "futrDeriv"
                            ]["descRefInstrmnt"]["indexBasketInfo"].get("indexName")
                        df.loc[i, "derivative_payoff"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ].get("payOffProf")
                        df.loc[i, "expiry_date"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ].get("expDt") or df.iloc[i]["derivativeInfo"]["futrDeriv"].get(
                            "expDate"
                        )
                        df.loc[i, "notional_amount"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ].get("notionalAmt")
                        df.loc[i, "notional_currency"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ].get("curCd")
                        df.loc[i, "unrealized_gain"] = df.iloc[i]["derivativeInfo"][
                            "futrDeriv"
                        ].get("unrealizedAppr")
                    if "fwdDeriv" in df.iloc[i]["derivativeInfo"]:
                        df.loc[i, "derivative_category"] = df.iloc[i]["derivativeInfo"][
                            "fwdDeriv"
                        ].get("@derivCat")
                        df.loc[i, "counterparty"] = df.iloc[i]["derivativeInfo"][
                            "fwdDeriv"
                        ]["counterparties"].get("counterpartyName")
                        df.loc[i, "currency_sold"] = df.iloc[i]["derivativeInfo"][
                            "fwdDeriv"
                        ].get("curSold")
                        df.loc[i, "currency_amount_sold"] = df.iloc[i][
                            "derivativeInfo"
                        ]["fwdDeriv"].get("amtCurSold")
                        df.loc[i, "currency_bought"] = df.iloc[i]["derivativeInfo"][
                            "fwdDeriv"
                        ].get("curPur")
                        df.loc[i, "currency_amount_bought"] = df.iloc[i][
                            "derivativeInfo"
                        ]["fwdDeriv"].get("amtCurPur")
                        df.loc[i, "expiry_date"] = df.iloc[i]["derivativeInfo"][
                            "fwdDeriv"
                        ].get("settlementDt")
                        df.loc[i, "unrealized_gain"] = df.iloc[i]["derivativeInfo"][
                            "fwdDeriv"
                        ].get("unrealizedAppr")
                    if "swapDeriv" in df.iloc[i]["derivativeInfo"]:
                        df.loc[i, "derivative_category"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("@derivCat")
                        df.loc[i, "counterparty"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ]["counterparties"].get("counterpartyName")
                        df.loc[i, "underlying_name"] = (
                            df.iloc[i]["derivativeInfo"]["swapDeriv"][
                                "descRefInstrmnt"
                            ]["otherRefInst"].get("issueTitle")
                            if "otherRefInst"
                            in df.iloc[i]["derivativeInfo"]["swapDeriv"][
                                "descRefInstrmnt"
                            ]
                            else None
                        )
                        df.loc[i, "swap_description"] = (
                            df.iloc[i]["derivativeInfo"]["swapDeriv"][
                                "otherRecDesc"
                            ].get("#text")
                            if "otherRecDesc"
                            in df.iloc[i]["derivativeInfo"]["swapDeriv"][
                                "descRefInstrmnt"
                            ]
                            else None
                        )
                        df.loc[i, "rate_type"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ]["floatingPmntDesc"].get("@fixedOrFloating")
                        df.loc[i, "floating_rate_index"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ]["floatingPmntDesc"].get("@floatingRtIndex")
                        df.loc[i, "floating_rate_spread"] = df.iloc[i][
                            "derivativeInfo"
                        ]["swapDeriv"]["floatingPmntDesc"].get("@floatingRtSpread")
                        df.loc[i, "payment_amount"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ]["floatingPmntDesc"].get("@pmntAmt")
                        if "rtResetTenors" in df.loc[i]["derivativeInfo"]["swapDeriv"]:
                            df.loc[i, "rate_tenor"] = df.iloc[i]["derivativeInfo"][
                                "swapDeriv"
                            ]["rtResetTenors"]["rtResetTenor"].get("@rateTenor")
                            df.loc[i, "rate_tenor_unit"] = df.iloc[i]["derivativeInfo"][
                                "swapDeriv"
                            ]["rtResetTenors"]["rtResetTenor"].get("@rateTenorUnit")
                            df.loc[i, "reset_date"] = df.iloc[i]["derivativeInfo"][
                                "swapDeriv"
                            ]["rtResetTenors"]["rtResetTenor"].get("@resetDt")
                            df.loc[i, "reset_date_unit"] = df.iloc[i]["derivativeInfo"][
                                "swapDeriv"
                            ]["rtResetTenors"]["rtResetTenor"].get("@resetDtUnit")
                        df.loc[i, "expiry_date"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("terminationDt")
                        df.loc[i, "upfront_payment"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("upfrontPmnt")
                        df.loc[i, "payment_currency"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("pmntCurCd")
                        df.loc[i, "upfront_receipt"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("upfrontRcpt")
                        df.loc[i, "receipt_currency"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("rcptCurCd")
                        df.loc[i, "notional_amount"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("notionalAmt")
                        df.loc[i, "notional_currency"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("curCd")
                        df.loc[i, "unrealized_gain"] = df.iloc[i]["derivativeInfo"][
                            "swapDeriv"
                        ].get("unrealizedAppr")
                if "repurchaseAgrmt" in df.iloc[i] and isinstance(
                    df.iloc[i]["repurchaseAgrmt"], dict
                ):
                    df.loc[i, "repo_type"] = df.iloc[i]["repurchaseAgrmt"].get(
                        "transCat"
                    )
                    if "clearedCentCparty" in df.iloc[i][
                        "repurchaseAgrmt"
                    ] and isinstance(
                        df.iloc[i]["repurchaseAgrmt"]["clearedCentCparty"], dict
                    ):
                        df.loc[i, "is_cleared"] = df.iloc[i]["repurchaseAgrmt"][
                            "clearedCentCparty"
                        ].get("@isCleared")
                        df.loc[i, "counterparty"] = df.iloc[i]["repurchaseAgrmt"][
                            "clearedCentCparty"
                        ].get("@centralCounterparty")
                    df.loc[i, "is_tri_party"] = df.iloc[i]["repurchaseAgrmt"].get(
                        "isTriParty"
                    )
                    df.loc[i, "annualized_return"] = df.iloc[i]["repurchaseAgrmt"].get(
                        "repurchaseRt"
                    )
                    df.loc[i, "maturity_date"] = df.iloc[i]["repurchaseAgrmt"].get(
                        "maturityDt"
                    )
                    if (
                        "repurchaseCollaterals" in df.iloc[i]["repurchaseAgrmt"]
                        and "repurchaseCollateral"
                        in df.iloc[i]["repurchaseAgrmt"]["repurchaseCollaterals"]
                    ):
                        df.loc[i, "principal_amount"] = df.iloc[i]["repurchaseAgrmt"][
                            "repurchaseCollaterals"
                        ]["repurchaseCollateral"].get("principalAmt")
                        df.loc[i, "principal_currency"] = df.iloc[i]["repurchaseAgrmt"][
                            "repurchaseCollaterals"
                        ]["repurchaseCollateral"].get("@principalCd")
                        df.loc[i, "collateral_amount"] = df.iloc[i]["repurchaseAgrmt"][
                            "repurchaseCollaterals"
                        ]["repurchaseCollateral"].get("collateralVal")
                        df.loc[i, "collateral_currency"] = df.iloc[i][
                            "repurchaseAgrmt"
                        ]["repurchaseCollaterals"]["repurchaseCollateral"].get(
                            "@collateralCd"
                        )
                        df.loc[i, "collateral_type"] = df.iloc[i]["repurchaseAgrmt"][
                            "repurchaseCollaterals"
                        ]["repurchaseCollateral"].get("@invstCat")
                if "currencyConditional" in df.iloc[i] and isinstance(
                    df.iloc[i]["currencyConditional"], dict
                ):
                    df.loc[i, "exchange_currency"] = df.iloc[i][
                        "currencyConditional"
                    ].get("@curCd")
                    df.loc[i, "exchange_rate"] = df.iloc[i]["currencyConditional"].get(
                        "@exchangeRt"
                    )
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

            results = (
                df.fillna("N/A")
                .replace("N/A", None)
                .sort_values(by="pctVal", ascending=False)
                .to_dict(orient="records")
            )

        return [SecEtfHoldingsData.model_validate(d) for d in results]
