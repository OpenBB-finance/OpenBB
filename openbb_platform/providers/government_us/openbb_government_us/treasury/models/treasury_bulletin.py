"""Treasury Bulletin Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field

from openbb_government_us.utils.serializers import OmitNoneMixin

BulletinTable = Literal[
    "pdo1",
    "pdo2",
    "ofs1",
    "ofs2",
    "uscc1",
    "uscc2",
    "fcp1",
    "fcp2",
    "fcp3",
    "esf1",
    "esf2",
    "ffo5",
    "ffo6",
]

TABLE_LABELS: dict[str, str] = {
    "ofs2": "Estimated ownership of U.S. Treasury securities",
    "ofs1": "Federal securities by class of investor and type of issue",
    "pdo1": "Auction results - regular weekly Treasury bills",
    "pdo2": "Auction results - other marketable securities",
    "uscc1": "Currency and coin outstanding and in circulation",
    "uscc2": "Currency in circulation by denomination",
    "fcp1": "Foreign currency positions - weekly, major participants",
    "fcp2": "Foreign currency positions - monthly, major participants",
    "fcp3": "Foreign currency positions - quarterly, large participants",
    "esf1": "Exchange Stabilization Fund balances",
    "esf2": "Exchange Stabilization Fund statement of net cost",
    "ffo5": "Internal revenue receipts by state",
    "ffo6": "Customs and Border Protection collections by district and port",
}

ENDPOINTS: dict[str, str] = {
    "pdo1": "v1/accounting/tb/pdo1_offerings_regular_weekly_treasury_bills",
    "pdo2": "v1/accounting/tb/pdo2_offerings_marketable_securities_other_regular_weekly_treasury_bills",
    "ofs1": "v1/accounting/tb/ofs1_distribution_federal_securities_class_investors_type_issues",
    "ofs2": "v1/accounting/tb/ofs2_estimated_ownership_treasury_securities",
    "uscc1": "v1/accounting/tb/uscc1_amounts_outstanding_circulation",
    "uscc2": "v1/accounting/tb/uscc2_amounts_outstanding_circulation",
    "fcp1": "v1/accounting/tb/fcp1_weekly_report_major_market_participants",
    "fcp2": "v1/accounting/tb/fcp2_monthly_report_major_market_participants",
    "fcp3": "v1/accounting/tb/fcp3_quarterly_report_large_market_participants",
    "esf1": "v1/accounting/tb/esf1_balances",
    "esf2": "v1/accounting/tb/esf2_statement_net_cost",
    "ffo5": "v1/accounting/tb/ffo5_internal_revenue_by_state",
    "ffo6": "v1/accounting/tb/ffo6_customs_border_protection_collections",
}

TABLE_CODES = {slug: f"{slug[:-1].upper()}-{slug[-1]}" for slug in ENDPOINTS}

PIVOT_TABLES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "ofs2": (("classification",), ("securities_amount",)),
    "ofs1": (
        ("classification", "sub_classification", "issue_type"),
        ("securities_amount",),
    ),
    "esf1": (("classification",), ("activity", "balance")),
    "esf2": (
        ("classification",),
        ("current_quarter_amount", "fiscal_year_to_date_amount"),
    ),
}

VALUE_LABELS: dict[str, str] = {
    "activity": "Activity",
    "balance": "Balance",
    "current_quarter_amount": "Current Quarter",
    "fiscal_year_to_date_amount": "Fiscal Year to Date",
}

COMMON_FIELDS = {
    "record_date": "record_date",
    "src_line_nbr": "line_number",
}

FCP_COMMON_FIELDS = {
    **COMMON_FIELDS,
    "report_date": "report_date",
    "foreign_currency_desc": "currency",
    "spot_fwd_future_purch_amt": "spot_forward_futures_purchased",
    "spot_fwd_future_sold_amt": "spot_forward_futures_sold",
    "exchange_rate": "exchange_rate",
}

FCP_MONTHLY_QUARTERLY_FIELDS = {
    **FCP_COMMON_FIELDS,
    "assets_amt": "assets",
    "liabilities_amt": "liabilities",
    "call_options_bought_amt": "call_options_bought",
    "call_options_written_amt": "call_options_written",
    "put_options_bought_amt": "put_options_bought",
    "put_options_written_amt": "put_options_written",
    "options_net_delta_amt": "options_net_delta",
}

FIELD_MAP: dict[str, dict[str, str]] = {
    "pdo1": {
        **COMMON_FIELDS,
        "issue_date": "issue_date",
        "maturity_date": "maturity_date",
        "days_to_maturity": "days_to_maturity",
        "bids_tendered_mil_amt": "bids_tendered",
        "bids_acc_total_mil_amt": "bids_accepted",
        "bids_acc_comp_basis_mil_amt": "bids_accepted_competitive",
        "bids_acc_noncomp_basis_mil_amt": "bids_accepted_noncompetitive",
        "high_price_per_hundred": "high_price_per_hundred",
        "high_discount_rate": "high_discount_rate",
        "high_investment_rate": "high_investment_rate",
    },
    "pdo2": {
        **COMMON_FIELDS,
        "auction_date": "auction_date",
        "issue_date": "issue_date",
        "securities_desc": "security_description",
        "period_to_final_maturity": "period_to_final_maturity",
        "tendered_mil_amt": "bids_tendered",
        "acc_mil_amt": "bids_accepted",
        "acc_yield_discount_margin": "accepted_yield_discount_margin",
        "eq_price_for_notes_bonds": "equivalent_price",
    },
    "ofs1": {
        **COMMON_FIELDS,
        "end_fiscal_year_or_month": "report_date",
        "securities_classification": "classification",
        "investors_classification": "sub_classification",
        "issues_type": "issue_type",
        "securities_mil_amt": "securities_amount",
    },
    "ofs2": {
        "record_date": "record_date",
        "end_of_month": "report_date",
        "securities_owner": "classification",
        "securities_bil_amt": "securities_amount",
    },
    "uscc1": {
        **COMMON_FIELDS,
        "currency_coins_as_of_date": "report_date",
        "currency_coins_category_desc": "classification",
        "total_currency_coins_amt": "total_currency_and_coins",
        "total_currency_amt": "total_currency",
        "federal_reserve_notes_amt": "federal_reserve_notes",
        "us_notes_amt": "us_notes",
        "currency_no_longer_issued_amt": "currency_no_longer_issued",
        "total_coins_amt": "total_coins",
        "dollar_coins_amt": "dollar_coins",
        "fractional_coins_amt": "fractional_coins",
    },
    "uscc2": {
        **COMMON_FIELDS,
        "currency_as_of_date": "report_date",
        "currency_denom": "denomination",
        "total_currency_amt": "total_currency",
        "federal_reserve_notes_amt": "federal_reserve_notes",
        "us_notes_amt": "us_notes",
        "currency_no_longer_issued_amt": "currency_no_longer_issued",
        "per_capita_amt": "per_capita",
    },
    "fcp1": {
        **FCP_COMMON_FIELDS,
        "net_options_positions_amt": "net_options_position",
    },
    "fcp2": FCP_MONTHLY_QUARTERLY_FIELDS,
    "fcp3": FCP_MONTHLY_QUARTERLY_FIELDS,
    "esf1": {
        **COMMON_FIELDS,
        "report_date": "report_date",
        "classification_desc": "classification",
        "activity_thous_amt": "activity",
        "balance_thous_amt": "balance",
    },
    "esf2": {
        **COMMON_FIELDS,
        "report_date": "report_date",
        "classification_desc": "classification",
        "current_quarter_thous_amt": "current_quarter_amount",
        "fytd_thous_amt": "fiscal_year_to_date_amount",
    },
    "ffo5": {
        **COMMON_FIELDS,
        "revenue_fiscal_year": "fiscal_year",
        "state_nm": "state",
        "total_rev_collect_thous_amt": "total_collections",
        "business_income_tax_thous_amt": "business_income_taxes",
        "total_indv_tax_thous_amt": "total_individual_taxes",
        "withheld_fica_thous_amt": "withheld_income_and_fica_taxes",
        "not_withheld_seca_thous_amt": "not_withheld_income_and_seca_taxes",
        "unemployment_ins_tax_thous_amt": "unemployment_insurance_taxes",
        "railroad_retire_tax_thous_amt": "railroad_retirement_taxes",
        "estate_trust_tax_thous_amt": "estate_and_trust_income_taxes",
        "estate_tax_thous_amt": "estate_taxes",
        "gift_tax_thous_amt": "gift_taxes",
        "excise_tax_thous_amt": "excise_taxes",
    },
    "ffo6": {
        **COMMON_FIELDS,
        "collection_fiscal_year": "fiscal_year",
        "district_nm": "district",
        "port_nm": "port",
        "port_cd": "port_code",
        "collection_amt": "total_collections",
    },
}

SCALE_MAP: dict[str, dict[str, int]] = {
    "pdo1": {
        "bids_tendered": 1_000_000,
        "bids_accepted": 1_000_000,
        "bids_accepted_competitive": 1_000_000,
        "bids_accepted_noncompetitive": 1_000_000,
    },
    "pdo2": {
        "bids_tendered": 1_000_000,
        "bids_accepted": 1_000_000,
    },
    "ofs1": {"securities_amount": 1_000_000},
    "ofs2": {"securities_amount": 1_000_000_000},
    "esf1": {"activity": 1_000, "balance": 1_000},
    "esf2": {
        "current_quarter_amount": 1_000,
        "fiscal_year_to_date_amount": 1_000,
    },
    "ffo5": {
        "total_collections": 1_000,
        "business_income_taxes": 1_000,
        "total_individual_taxes": 1_000,
        "withheld_income_and_fica_taxes": 1_000,
        "not_withheld_income_and_seca_taxes": 1_000,
        "unemployment_insurance_taxes": 1_000,
        "railroad_retirement_taxes": 1_000,
        "estate_and_trust_income_taxes": 1_000,
        "estate_taxes": 1_000,
        "gift_taxes": 1_000,
        "excise_taxes": 1_000,
    },
}

PERCENT_FIELDS = {
    "accepted_yield_discount_margin",
    "high_discount_rate",
    "high_investment_rate",
}

FOREIGN_CURRENCY_TABLES = {"fcp1", "fcp2", "fcp3"}

FOREIGN_CURRENCY_UNITS = {"Millions": 1_000_000, "Billions": 1_000_000_000}

FOREIGN_CURRENCY_AMOUNT_FIELDS = {
    "spot_forward_futures_purchased",
    "spot_forward_futures_sold",
    "net_options_position",
    "assets",
    "liabilities",
    "call_options_bought",
    "call_options_written",
    "put_options_bought",
    "put_options_written",
    "options_net_delta",
}

ESF2_ARTIFACT_ROWS = {
    "check",
    "from Dec 24 FS",
    "Cumulative Income and Expense is equal to Q",
}


class TreasuryBulletinQueryParams(QueryParams):
    """Treasury Bulletin Query Parameters.

    Source: https://fiscaldata.treasury.gov/datasets/treasury-bulletin/
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": code}
                    for code, label in TABLE_LABELS.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
    }

    table: BulletinTable = Field(
        default="ofs2",
        description="The Treasury Bulletin table to query."
        + " pdo1: auction results of regular weekly Treasury bills;"
        + " pdo2: auction results of other marketable securities"
        + " (CMBs, notes, bonds, TIPS, FRNs);"
        + " ofs1: distribution of federal securities by class of investors"
        + " and type of issues;"
        + " ofs2: estimated ownership of U.S. Treasury securities;"
        + " uscc1: currency and coin outstanding and in circulation;"
        + " uscc2: currency in circulation by denomination;"
        + " fcp1: weekly foreign currency positions of major market"
        + " participants;"
        + " fcp2: monthly foreign currency positions of major market"
        + " participants;"
        + " fcp3: quarterly foreign currency positions of large market"
        + " participants;"
        + " esf1: Exchange Stabilization Fund balances;"
        + " esf2: Exchange Stabilization Fund statement of net cost;"
        + " ffo5: internal revenue receipts by state;"
        + " ffo6: Customs and Border Protection collections of duties,"
        + " taxes, and fees by district and port.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters on record_date, the bulletin edition date:"
        + " PDO, USCC, FCP, and ESF editions fall on the 1st of"
        + " Mar/Jun/Sep/Dec, FFO editions on Dec 1, and OFS tables use"
        + " quarter-end dates; for ofs2, record_date is only the date the"
        + " series was last restated. Editions begin 2021."
        + " When None, defaults to the trailing 365 days rather than the full history; set it explicitly to reach further back.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters on record_date, the bulletin edition date.",
    )


class TreasuryBulletinData(OmitNoneMixin, Data):
    """Treasury Bulletin Data.

    A normalized union of the thirteen Treasury Bulletin tables. Dimension
    and measure fields are populated according to the table requested;
    per-table source keys are mapped to unified names, amounts reported by
    the source in thousands, millions, or billions are expanded to whole
    units, and percentages are normalized to decimal fractions.
    """

    table_code: str = Field(
        description="Treasury Bulletin table code of the row, e.g. 'OFS-2'.",
    )
    report_date: dateType | None = Field(
        default=None,
        description="Date the figures are as of - the observation axis for"
        + " the OFS, USCC, FCP, and ESF tables. Declared first so it leads the"
        + " served columns, which this model orders by field declaration"
        + " because its omit-None serializer carries no column config.",
    )
    record_date: dateType = Field(
        description="Publication date of the bulletin edition reporting the"
        + " row; for ofs2, the date the series was last restated. This is"
        + " edition metadata, not the observation axis.",
    )
    auction_date: dateType | None = Field(
        default=None,
        description="Date of the auction. (pdo2)",
    )
    issue_date: dateType | None = Field(
        default=None,
        description="Date the security was issued. (pdo1, pdo2)",
    )
    maturity_date: dateType | None = Field(
        default=None,
        description="Date the bills mature. (pdo1)",
    )
    days_to_maturity: int | None = Field(
        default=None,
        description="Number of days from issue to maturity, identifying the"
        + " bill tenor. (pdo1)",
    )
    fiscal_year: int | None = Field(
        default=None,
        description="Fiscal year the collections were received in." + " (ffo5, ffo6)",
    )
    line_number: int | None = Field(
        default=None,
        description="Line number of the row in the published bulletin table;"
        + " not present for ofs2.",
    )
    classification: str | None = Field(
        default=None,
        description="Primary classification of the row - securities"
        + " classification (ofs1), securities owner (ofs2), holder category"
        + " (uscc1), or statement line item (esf1, esf2).",
    )
    sub_classification: str | None = Field(
        default=None,
        description="Class of investors holding the securities. (ofs1)",
    )
    issue_type: str | None = Field(
        default=None,
        description="Type of issues held - Marketable, Nonmarketable, or"
        + " Total. (ofs1)",
    )
    security_description: str | None = Field(
        default=None,
        description="Description of the security auctioned, including the"
        + " rate, type, and maturity. (pdo2)",
    )
    period_to_final_maturity: str | None = Field(
        default=None,
        description="Period from the issue date to final maturity, e.g."
        + " '42d' or '9y 10m'. (pdo2)",
    )
    denomination: str | None = Field(
        default=None,
        description="Currency denomination, e.g. '$100', or"
        + " 'Total Currency'. (uscc2)",
    )
    currency: str | None = Field(
        default=None,
        description="Foreign currency of the reported positions."
        + " (fcp1, fcp2, fcp3)",
    )
    state: str | None = Field(
        default=None,
        description="U.S. state, or aggregate area, of the collections." + " (ffo5)",
    )
    district: str | None = Field(
        default=None,
        description="Customs district of the collection port. (ffo6)",
    )
    port: str | None = Field(
        default=None,
        description="Collection port name, or 'Total' for the district"
        + " roll-up. (ffo6)",
    )
    port_code: str | None = Field(
        default=None,
        description="Five-digit CBP port code; not present on district"
        + " roll-up rows. (ffo6)",
    )
    bids_tendered: float | None = Field(
        default=None,
        description="Amount of bids tendered at auction, in dollars." + " (pdo1, pdo2)",
    )
    bids_accepted: float | None = Field(
        default=None,
        description="Total amount of bids accepted at auction, in dollars."
        + " (pdo1, pdo2)",
    )
    bids_accepted_competitive: float | None = Field(
        default=None,
        description="Amount of bids accepted on a competitive basis, in"
        + " dollars. (pdo1)",
    )
    bids_accepted_noncompetitive: float | None = Field(
        default=None,
        description="Amount of bids accepted on a non-competitive basis, in"
        + " dollars. (pdo1)",
    )
    high_price_per_hundred: float | None = Field(
        default=None,
        description="High price per hundred on competitive bids accepted." + " (pdo1)",
    )
    high_discount_rate: float | None = Field(
        default=None,
        description="High discount rate on competitive bids accepted, as a"
        + " normalized decimal (percent / 100). (pdo1)",
    )
    high_investment_rate: float | None = Field(
        default=None,
        description="High investment rate on competitive bids accepted, as a"
        + " normalized decimal (percent / 100). (pdo1)",
    )
    accepted_yield_discount_margin: float | None = Field(
        default=None,
        description="Accepted yield for notes, bonds, and TIPS, or discount"
        + " margin for FRNs, as a normalized decimal (percent / 100)."
        + " (pdo2)",
    )
    equivalent_price: float | None = Field(
        default=None,
        description="Equivalent price per hundred for notes and bonds." + " (pdo2)",
    )
    securities_amount: float | None = Field(
        default=None,
        description="Amount of securities held, in dollars. (ofs1, ofs2)",
    )
    total_currency_and_coins: float | None = Field(
        default=None,
        description="Total currency and coins, in dollars. (uscc1)",
    )
    total_currency: float | None = Field(
        default=None,
        description="Total currency, in dollars. (uscc1, uscc2)",
    )
    federal_reserve_notes: float | None = Field(
        default=None,
        description="Federal Reserve notes, in dollars. (uscc1, uscc2)",
    )
    us_notes: float | None = Field(
        default=None,
        description="U.S. notes, in dollars; can be negative by"
        + " denomination. (uscc1, uscc2)",
    )
    currency_no_longer_issued: float | None = Field(
        default=None,
        description="Currency no longer issued, in dollars. (uscc1, uscc2)",
    )
    total_coins: float | None = Field(
        default=None,
        description="Total coins, in dollars. (uscc1)",
    )
    dollar_coins: float | None = Field(
        default=None,
        description="Dollar coins, in dollars. (uscc1)",
    )
    fractional_coins: float | None = Field(
        default=None,
        description="Fractional coins, in dollars. (uscc1)",
    )
    per_capita: float | None = Field(
        default=None,
        description="Currency in circulation per capita, in dollars;"
        + " populated only on the 'Total Currency' row, 0 otherwise."
        + " (uscc2)",
    )
    spot_forward_futures_purchased: float | None = Field(
        default=None,
        description="Spot, forward, and futures contracts purchased, in"
        + " units of the currency. (fcp1, fcp2, fcp3)",
    )
    spot_forward_futures_sold: float | None = Field(
        default=None,
        description="Spot, forward, and futures contracts sold, in units of"
        + " the currency. (fcp1, fcp2, fcp3)",
    )
    net_options_position: float | None = Field(
        default=None,
        description="Net options position, in units of the currency. (fcp1)",
    )
    assets: float | None = Field(
        default=None,
        description="Foreign currency assets, in units of the currency."
        + " (fcp2, fcp3)",
    )
    liabilities: float | None = Field(
        default=None,
        description="Foreign currency liabilities, in units of the currency."
        + " (fcp2, fcp3)",
    )
    call_options_bought: float | None = Field(
        default=None,
        description="Call options bought, in units of the currency." + " (fcp2, fcp3)",
    )
    call_options_written: float | None = Field(
        default=None,
        description="Call options written, in units of the currency." + " (fcp2, fcp3)",
    )
    put_options_bought: float | None = Field(
        default=None,
        description="Put options bought, in units of the currency." + " (fcp2, fcp3)",
    )
    put_options_written: float | None = Field(
        default=None,
        description="Put options written, in units of the currency." + " (fcp2, fcp3)",
    )
    options_net_delta: float | None = Field(
        default=None,
        description="Net delta-equivalent options position, in units of the"
        + " currency. (fcp2, fcp3)",
    )
    exchange_rate: float | None = Field(
        default=None,
        description="Units of the foreign currency per U.S. dollar; not"
        + " applicable to U.S. Dollars rows. (fcp1, fcp2, fcp3)",
    )
    activity: float | None = Field(
        default=None,
        description="Activity since the last report date, in dollars." + " (esf1)",
    )
    balance: float | None = Field(
        default=None,
        description="Balance as of the report date, in dollars. (esf1)",
    )
    current_quarter_amount: float | None = Field(
        default=None,
        description="Amount for the current quarter, in dollars. (esf2)",
    )
    fiscal_year_to_date_amount: float | None = Field(
        default=None,
        description="Fiscal year-to-date amount, in dollars. (esf2)",
    )
    total_collections: float | None = Field(
        default=None,
        description="Total collections, in dollars - gross internal revenue"
        + " collections (ffo5) or duties, taxes, and fees collected (ffo6).",
    )
    business_income_taxes: float | None = Field(
        default=None,
        description="Business income taxes collected, in dollars. (ffo5)",
    )
    total_individual_taxes: float | None = Field(
        default=None,
        description="Total individual taxes collected, in dollars. (ffo5)",
    )
    withheld_income_and_fica_taxes: float | None = Field(
        default=None,
        description="Individual income taxes withheld and FICA taxes, in"
        + " dollars. (ffo5)",
    )
    not_withheld_income_and_seca_taxes: float | None = Field(
        default=None,
        description="Individual income taxes not withheld and SECA taxes, in"
        + " dollars. (ffo5)",
    )
    unemployment_insurance_taxes: float | None = Field(
        default=None,
        description="Unemployment insurance taxes, in dollars. (ffo5)",
    )
    railroad_retirement_taxes: float | None = Field(
        default=None,
        description="Railroad retirement taxes, in dollars. (ffo5)",
    )
    estate_and_trust_income_taxes: float | None = Field(
        default=None,
        description="Estate and trust income taxes, in dollars. (ffo5)",
    )
    estate_taxes: float | None = Field(
        default=None,
        description="Estate taxes, in dollars. (ffo5)",
    )
    gift_taxes: float | None = Field(
        default=None,
        description="Gift taxes, in dollars. (ffo5)",
    )
    excise_taxes: float | None = Field(
        default=None,
        description="Excise taxes, in dollars; excludes those collected by"
        + " CBP and TTB. (ffo5)",
    )


class TreasuryBulletinFetcher(
    Fetcher[
        TreasuryBulletinQueryParams,
        list[TreasuryBulletinData],
    ]
):
    """Fetch Treasury Bulletin tables from the FiscalData API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TreasuryBulletinQueryParams:
        """Transform the query params."""
        return TreasuryBulletinQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TreasuryBulletinQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FiscalData API."""
        from openbb_government_us.treasury.utils.fiscal_data import (
            build_filters,
            default_start_date,
            get_fiscal_data,
        )

        start_date = default_start_date(query.start_date, query.end_date, 365)
        filters = build_filters(
            [
                ("record_date", "gte", start_date),
                ("record_date", "lte", query.end_date),
            ]
        )

        return await get_fiscal_data(
            ENDPOINTS[query.table], filters=filters, sort="record_date"
        )

    @staticmethod
    def transform_data(
        query: TreasuryBulletinQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TreasuryBulletinData]:
        """Transform the data."""
        mapping = FIELD_MAP[query.table]
        table_scales = SCALE_MAP.get(query.table, {})
        results: list[dict[str, Any]] = []
        for row in data:
            if (
                query.table == "esf2"
                and row.get("classification_desc") in ESF2_ARTIFACT_ROWS
            ):
                continue
            scales = table_scales
            if query.table in FOREIGN_CURRENCY_TABLES:
                unit = FOREIGN_CURRENCY_UNITS.get(row.get("foreign_currency_denom"), 1)
                scales = dict.fromkeys(FOREIGN_CURRENCY_AMOUNT_FIELDS, unit)
            record: dict[str, Any] = {"table_code": TABLE_CODES[query.table]}
            for source, target in mapping.items():
                if source not in row:
                    continue
                value = row[source]
                if value is not None:
                    if target == "fiscal_year":
                        value = int(str(value)[:4])
                    elif target in PERCENT_FIELDS:
                        value = float(value) / 100
                    elif target in scales:
                        value = float(value) * scales[target]
                record[target] = value
            results.append(record)

        if query.table in PIVOT_TABLES:
            return TreasuryBulletinFetcher._pivot(query.table, results)

        validated = [TreasuryBulletinData.model_validate(row) for row in results]

        return sorted(
            validated,
            key=lambda row: (row.report_date or row.record_date, row.record_date),
            reverse=True,
        )

    @staticmethod
    def _pivot(table: str, records: list[dict]) -> list[TreasuryBulletinData]:
        """Pivot a long table into one row per report date.

        Parameters
        ----------
        table : str
            Key of PIVOT_TABLES.
        records : list[dict]
            The mapped long-format records.

        Returns
        -------
        list[TreasuryBulletinData]
            One row per report date, newest first, with each classification
            spread into its own value column.
        """
        dimensions, values = PIVOT_TABLES[table]
        multi_value = len(values) > 1
        pivoted: dict[Any, dict[str, Any]] = {}
        columns: list[str] = []

        for record in records:
            report_date = record.get("report_date")

            if report_date is None:
                continue

            row = pivoted.setdefault(
                report_date,
                {
                    "table_code": record.get("table_code"),
                    "report_date": report_date,
                    "record_date": record.get("record_date"),
                },
            )

            if record.get("record_date") and record["record_date"] > row["record_date"]:
                row["record_date"] = record["record_date"]

            parts: list[str] = []

            for dimension in dimensions:
                value = record.get(dimension)

                if value in (None, "") or (parts and str(value) == parts[-1]):
                    continue

                parts.append(str(value))

            label = " - ".join(parts)

            for value in values:
                if record.get(value) is None:
                    continue

                column = f"{label} ({VALUE_LABELS[value]})" if multi_value else label

                if not column:
                    continue

                if column not in columns:
                    columns.append(column)

                row[column] = record[value]

        ordered = sorted(
            pivoted.values(), key=lambda row: row["report_date"], reverse=True
        )

        return [
            TreasuryBulletinData.model_validate(
                {
                    "table_code": row["table_code"],
                    "report_date": row["report_date"],
                    "record_date": row["record_date"],
                    **{column: row.get(column) for column in columns},
                }
            )
            for row in ordered
        ]
