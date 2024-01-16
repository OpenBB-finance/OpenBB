"""FMP Cash Flow Statements As Reported Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements_as_reported import (
    FinancialStatementsAsReportedData,
    FinancialStatementsAsReportedQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, model_validator


class FMPCashFlowAsReportedQueryParams(FinancialStatementsAsReportedQueryParams):
    """
    FMP Financial Cash Flow Statements As Reported Query.

    Source: https://site.financialmodelingprep.com/developer/docs#full-financial-as-reported-financial-statements
    """

    period: Literal["annual", "quarter"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )


class FMPCashFlowAsReportedData(FinancialStatementsAsReportedData):
    """FMP Cash Flow Statements As Reported Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_period": "period",
        "cash_cash_equivalents_restricted_cash_and_restricted_cash_equivalents": "cashcashequivalentsrestrictedcashandrestrictedcashequivalents",  # noqa: E501
        "net_income_loss": "netincomeloss",
        "profit_loss": "profitloss",
        "income_loss_from_discontinued_operations_net_of_tax": "incomelossfromdiscontinuedoperationsnetoftax",
        "provision_for_loan_lease_and_other_losses": "provisionforloanleaseandotherlosses",
        "provision_for_loan_lease_and_other_losses_excluding_accounting_policy_conformity": "provisionforloanleaseandotherlossesexcludingaccountingpolicyconformity",  # noqa: E501
        "depreciation": "depreciation",
        "depreciation_depletion_and_amortization": "depreciationdepletionandamortization",
        "depreciation_amortization_and_accretion_net": "depreciationamortizationandaccretionnet",
        "amortization_of_intangible_assets": "amortizationofintangibleassets",
        "non_cash_portion_of_asset_impairment_and_related_items": "noncashportionofassetimpairmentandrelateditems",  # noqa: E501
        "deferred_income_tax_expense_benefit": "deferredincometaxexpensebenefit",
        "gain_on_sale_of_equity_investments_and_other_assets": "gainonsaleofequityinvestmentsandotherassets",
        "gain_loss_on_investments": "gainlossoninvestments",
        "share_based_compensation": "sharebasedcompensation",
        "employee_service_share_based_compensation_cash_flow_effect_cash_used_to_settle_awards": "employeeservicesharebasedcompensationcashfloweffectcashusedtosettleawards",  # noqa: E501
        "other_non_cash_income_expense": "othernoncashincomeexpense",
        "payments_to_acquire_productive_assets": "paymentstoacquireproductiveassets",
        "payments_for_origination_and_purchase_of_loans_held_for_sale": "paymentsfororiginationandpurchasesofloansheldforsale",  # noqa: E501
        "proceeds_from_sales_securitizations_and_pay_downs_of_loans_held_for_sale": "proceedsfromsalessecuritizationsandpaydownsofloansheldforsale",  # noqa: E501
        "increase_decrease_in_loss_and_loss_adjustment_expense_reserve": "increasedecreaseinlossandlossadjustmentexpensereserve",  # noqa: E501
        "increase_decrease_in_deferred_charges_reinsurance_assumed": "increasedecreaseindeferredchargesreinsuranceassumed",  # noqa: E501
        "increase_decrease_in_liability_for_claims_and_claims_adjustment_expense_reserve": "increasedecreaseinliabilityforclaimsandclaimsadjustmentexpensereserve",  # noqa: E501"
        "increase_decrease_in_deferred_charges_retroactive_insurance": "increasedecreaseindeferredchargesretroactivereinsurance",  # noqa: E501
        "increase_decrease_in_insurance_premiums": "increasedecreaseininsurancepremiums",
        "increase_decrease_in_unearned_premiums": "increasedecreaseinunearnedpremiums",
        "increase_decrease_in_nontrade_receivables": "increasedecreaseinnontradereceivables",
        "increase_decrease_in_accounts_receivable": "increasedecreaseinaccountsreceivable",
        "increase_decrease_in_other_receivables": "increasedecreaseinotherreceivables",
        "increase_decrease_in_receivables": "increasedecreaseinreceivables",
        "increase_decrease_in_derivative_contracts_assets_and_liabilities": "increasedecreaseinderivativecontractassetsandliabilities",  # noqa: E501
        "increase_decrease_in_inventories": "increasedecreaseininventories",
        "increase_decrease_in_other_operating_assets": "increasedecreaseinotheroperatingassets",
        "increase_decrease_in_other_current_assets": "increasedecreaseinothercurrentassets",
        "increase_decrease_in_accounts_payable": "increasedecreaseinaccountspayable",
        "increase_decrease_in_deferred_revenue": "increasedecreaseindeferredrevenue",
        "increase_decrease_in_contract_with_customer_liability": "increasedecreaseincontractwithcustomerliability",
        "increase_decrease_in_other_operating_liabilities": "increasedecreaseinotheroperatingliabilities",
        "increase_decrease_in_income_taxes": "increasedecreaseinincometaxes",
        "increase_decrease_in_financial_instruments_used_in_operating_activities": "increasedecreaseinfinancialinstrumentsusedinoperatingactivities",  # noqa: E501
        "increase_decrease_in_cash_collateral_for_borrowed_securities": "increasedecreaseincashcollateralforborrowedsecurities",  # noqa: E501
        "increase_decrease_in_accrued_interest_and_accounts_receivable": "increasedecreaseinaccruedinterestsandaccountsreceivable",  # noqa: E501
        "increase_decrease_in_prepaid_deferred_expense_and_other_assets": "increasedecreaseinprepaiddeferredexpenseandotherassets",  # noqa: E501
        "increase_decrease_in_trading_liabilities": "increasedecreaseintradingliabilities",
        "increase_decrease_in_accounts_payable_and_accrued_liabilities": "increasedecreaseinaccountspayableandaccruedliabilities",  # noqa: E501
        "increase_decrease_in_accrued_income_taxes_payable": "increasedecreaseinaccruedincometaxespayable",
        "increase_decrease_in_accounts_payable_and_other_liabilities": "increasedecreaseinaccountspayableandotherliabilities",  # noqa: E501
        "all_other_operating_activities": "allotheroperatingactivities",
        "other_operating_activities_cash_flow_statement": "otheroperatingactivitiescashflowstatement",
        "net_cash_provided_by_used_in_operating_activities_continuing_operations": "netcashprovidedbyusedinoperatingactivitiescontinuingoperations",  # noqa: E501
        "cash_provided_by_used_in_operating_activities_discontinued_operations": "cashprovidedbyusedinoperatingactivitiesdiscontinuedoperations",  # noqa: E501
        "net_cash_provided_by_used_in_operating_activities": "netcashprovidedbyusedinoperatingactivities",
        "proceeds_from_payments_for_interest_bearing_deposits_in_banks": "proceedsfrompaymentsforininterestbearingdepositsinbanks",  # noqa: E501
        "payments_to_acquire_equity_securities": "paymentstoacquireequitysecurities",
        "proceeds_from_sales_of_equity_securities": "proceedsfromsalesofequitysecurities",
        "payments_to_acquire_us_treasury_bills_and_available_for_sale_securities_debt": "paymentstoacquireustreasurybillsandavailableforsalesecuritiesdebt",  # noqa: E501
        "proceeds_from_sale_of_us_treasury_bills_and_available_for_sale_securities_debt": "proceedsfromsaleofustreasurybillsandavailableforsalesecuritiesdebt",  # noqa: E501
        "proceeds_from_redemptions_and_maturities_of_us_treasury_bills_and_available_for_sale_securities_debt": "proceedsfromredemptionsandmaturitiesofustreasurybillsandavailableforsalesecuritiesdebt",  # noqa: E501
        "payments_to_acquire_available_for_sale_securities": "paymentstoacquireavailableforsalesecurities",
        "payments_to_acquire_available_for_sale_securities_equity": "paymentstoacquireavailableforsalesecuritiesequity",  # noqa: E501
        "proceeds_from_sale_of_available_for_sale_securities": "proceedsfromsaleofavailableforsalesecurities",
        "payments_to_acquire_available_for_sale_securities_debt": "paymentstoacquireavailableforsalesecuritiesdebt",
        "proceeds_from_sale_of_available_for_sale_securities_debt": "proceedsfromsaleofavailableforsalesecuritiesdebt",
        "payments_to_acquire_held_to_maturity_securities": "paymentstoacquireheldtomaturitysecurities",
        "proceeds_from_sale_of_loans_and_leases_held_for_investment": "proceedsfromsaleofloansandleasesheldforinvestment",
        "proceeds_from_sale_of_finance_receivables": "proceedsfromsaleoffinancereceivables",
        "proceeds_from_payments_for_other_loans_and_leases": "proceedsfrompaymentsforotherloansandleases",
        "proceeds_from_payments_for_federal_funds_sold_and_securities_purchased_under_agreements_to_resell_net": "proceedsfrompaymentsforfederalfundssoldandsecuritiespurchasedunderagreementstoresellnet",  # noqa: E501
        "proceeds_from_maturities_prepayments_and_calls_of_available_for_sale_securities": "proceedsfrommaturitiesprepaymentsandcallsofavailableforsalesecurities",  # noqa: E501
        "proceeds_from_maturities_prepayments_and_calls_of_held_to_maturity_securities": "proceedsfrommaturitiesprepaymentsandcallsofheldtomaturitysecurities",  # noqa: E501
        "proceeds_from_sale_of_available_for_sale_securities_equity": "proceedsfromsaleofavailableforsalesecuritiesequity",  # noqa: E501
        "proceeds_from_sale_of_asset_and_equity_method_investments_net": "proceedsfromsaleofassetsandequitymethodinvestmentsnet",  # noqa: E501
        "payments_for_proceeds_from_equity_investments_and_other_net": "paymentsforproceedsfromequityinvestmentsandothernet",  # noqa: E501
        "redemption_of_other_investments": "redemptionofotherinvestments",
        "payments_to_acquire_loans_receivable": "paymentstoacquireloansreceivable",
        "proceeds_from_collection_of_loans_receivable": "proceedsfromcollectionofloansreceivable",
        "payments_to_acquire_businesses_and_interest_in_affiliates": "paymentstoacquirebusinessesandinterestinaffiliates",  # noqa: E501
        "proceeds_from_sale_and_maturity_of_other_investments": "proceedsfromsaleandmaturityofotherinvestments",
        "payments_to_acquire_property_plant_and_equipment": "paymentstoacquirepropertyplantandequipment",
        "gain_loss_on_sale_of_property_plant_equipment": "gainlossonsaleofpropertyplantequipment",
        "increase_decrease_in_capital_accrual": "increasedecreaseincapitalaccrual",
        "payments_for_purchases_of_assets_and_businesses": "paymentsforpurchasesofassetsandbusinesses",
        "payments_to_acquire_business_net_of_cash_acquired": "paymentstoacquirebusinessesnetofcashacquired",
        "payments_to_acquire_intangible_assets": "paymentstoacquireintangibleassets",
        "payments_to_acquire_other_investments": "paymentstoacquireotherinvestments",
        "payments_for_proceeds_from_loans_and_leases": "paymentsforproceedsfromloansandleases",
        "payments_for_proceeds_from_business_and_interest_in_affiliates": "paymentsforproceedsfrombusinessesandinterestinaffiliates",  # noqa: E501
        "increase_decrease_in_asset_backed_commercial_paper": "increasedecreaseinassetbackedcommercialpaper",
        "payments_for_proceeds_from_other_investing_activities": "paymentsforproceedsfromotherinvestingactivities",
        "net_cash_provided_by_used_in_investing_activities_continuing_operations": "netcashprovidedbyusedininvestingactivitiescontinuingoperations",  # noqa: E501
        "cash_provided_by_used_in_investing_activities_discontinued_operations": "cashprovidedbyusedininvestingactivitiesdiscontinuedoperations",  # noqa: E501
        "net_cash_provided_by_used_in_investing_activities": "netcashprovidedbyusedininvestingactivities",
        "increase_decrease_in_deposits": "increasedecreaseindeposits",
        "increase_decrease_in_federal_funds_purchased_and_securities_sold_under_agreements_to_repurchase_net": "increasedecreaseinfederalfundspurchasedandsecuritiessoldunderagreementstorepurchasenet",  # noqa: E501
        "repayments_of_short_term_debt": "repaymentsofshorttermdebt",
        "proceeds_from_repayments_of_other_debt": "proceedsfromrepaymentsofotherdebt",
        "beneficial_interests_issued_by_consolidated_variable_interest_entities": "beneficialinterestsissuedbyconsolidatedvariableinterestentities",  # noqa: E501
        "increase_decrease_in_beneficial_interests_issued_by_consolidated_variable_interest_entities": "increasedecreaseinbeneficialinterestsissuedbyconsolidatedvariableinterestentities",  # noqa: E501
        "proceeds_from_issuance_of_long_term_debt_and_capital_securities_net": "proceedsfromissuanceoflongtermdebtandcapitalsecuritiesnet",  # noqa: E501
        "repayments_of_long_term_debt_and_capital_securities": "repaymentsoflongtermdebtandcapitalsecurities",
        "payments_for_repurchase_of_redeemable_preferred_stock": "paymentsforrepurchaseofredeemablepreferredstock",
        "payments_related_to_tax_withholding_for_share_based_compensation": "paymentsrelatedtotaxwithholdingforsharebasedcompensation",  # noqa: E501
        "employee_services_share_based_compensation_cash_used_to_pay_taxes_for_equity_net_share_settlement": "employeeservicesharebasedcompensationcashusedtopaytaxesforequitynetsharesettlement",  # noqa: E501
        "excess_tax_benefit_from_share_based_compensation_financing_activities": "excesstaxbenefitfromsharebasedcompensationfinancingactivities",  # noqa: E501
        "proceeds_from_issuance_of_preferred_stock_and_preference_stock": "proceedsfromissuanceofpreferredstockandpreferencestock",  # noqa: E501
        "proceeds_from_issuance_of_common_stock": "proceedsfromissuanceofcommonstock",
        "proceeds_from_issuace_or_sale_of_equity": "proceedsfromissuaceorsaleofequity",
        "proceeds_from_issuance_of_long_term_debt": "proceedsfromissuanceoflongtermdebt",
        "repayments_of_long_term_debt": "repaymentsoflongtermdebt",
        "proceeds_from_repayments_of_short_term_debt": "proceedsfromrepaymentsofshorttermdebt",
        "payments_for_repurchase_of_common_stock": "paymentsforrepurchaseofcommonstock",
        "payments_for_repurchase_of_common_stock_and_warrants": "paymentsforrepurchaseofcommonstockandwarrants",
        "payments_to_minority_shareholders_and_proceeds_from_payments_for_other_financing_activities": "paymentstominorityshareholdersandproceedsfrompaymentsforotherfinancingactivities",  # noqa: E501
        "payments_of_dividends": "paymentsofdividends",
        "payments_of_dividends_common_stock": "paymentsofdividendscommonstock",
        "payments_of_dividends_and_dividend_equivalents_on_common_stock_and_restricted_stock_units": "paymentsofdividendsanddividendequivalentsoncommonstockandrestrictedstockunits",  # noqa: E501
        "proceeds_from_repayments_of_commercial_paper": "proceedsfromrepaymentsofcommercialpaper",
        "proceeds_from_payments_for_other_financing_activities": "proceedsfrompaymentsforotherfinancingactivities",
        "net_cash_provided_by_used_in_financing_activities_continuing_operations": "netcashprovidedbyusedinfinancingactivitiescontinuingoperations",  # noqa: E501
        "cash_provided_by_used_in_financing_activities_discontinued_operations": "cashprovidedbyusedinfinancingactivitiesdiscontinuedoperations",  # noqa: E501
        "net_cash_provided_by_used_in_financing_activities": "netcashprovidedbyusedinfinancingactivities",
        "effect_of_exchange_rate_on_cash_and_cash_equivalents": "effectofexchangerateoncashandcashequivalents",
        "effect_of_exchange_rate_on_cash_cash_equivalents_restricted_cash_and_restricted_cash_equivalents": "effectofexchangerateoncashcashequivalentsrestrictedcashandrestrictedcashequivalents",  # noqa: E501
        "cash_and_cash_equivalents_period_increase_decrease": "cashandcashequivalentsperiodincreasedecrease",
        "cash_and_due_from_banks": "cashandduefrombanks",
        "restricted_cash_and_cash_equivalents": "restrictedcashandcashequivalents",
        "restricted_cash_and_cash_equivalents_asset_statement_of_financial_position_extensible_list": "restrictedcashandcashequivalentsassetstatementoffinancialpositionextensiblelist",  # noqa: E501
        "cash_and_cash_equivalents_at_carrying_value": "cashandcashequivalentsatcarryingvalue",
        "cash_cash_equivalents_restricted_cash_and_restricted_cash_equivalents_period_increase_decrease_including_exchange_rate_effect": "cashcashequivalentsrestrictedcashandrestrictedcashequivalentsperiodincreasedecreaseincludingexchangerateeffect",  # noqa: E501
        "income_taxes_paid_net": "incometaxespaidnet",
        "income_taxes_paid": "incometaxespaid",
        "interest_paid": "interestpaid",
        "interest_paid_net": "interestpaidnet",
    }

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return {k: None if v == 0 else v for k, v in values.items()}


class FMPCashFlowStatementAsReportedFetcher(
    Fetcher[
        FMPCashFlowAsReportedQueryParams,
        List[FMPCashFlowAsReportedData],
    ]
):
    """FMP Financial Statements As Reported Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCashFlowAsReportedQueryParams:
        """Transform the query params."""
        return FMPCashFlowAsReportedQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCashFlowAsReportedQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3/"
        data: List[Dict] = []

        url = (
            base_url
            + f"cash-flow-statement-as-reported/{query.symbol}"
            + f"?period={query.period}&limit={query.limit}"
            + f"&apikey={api_key}"
        )

        data = get_data_many(url)

        return data

    @staticmethod
    def transform_data(
        query: FMPCashFlowAsReportedQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCashFlowAsReportedData]:
        """Return the transformed data."""
        return [FMPCashFlowAsReportedData.model_validate(d) for d in data]
