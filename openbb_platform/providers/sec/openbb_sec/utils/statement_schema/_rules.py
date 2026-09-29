"""Imputation and verification rule constants for financial statements."""

from __future__ import annotations

IS_IMPUTE: dict[str, list[tuple[str, list[tuple[str, int]]]]] = {
    "industrial": [
        (
            "total_cost_of_revenue",
            [("costs_and_expenses", 1), ("total_operating_expenses", -1)],
        ),
        (
            "total_operating_expenses",
            [("costs_and_expenses", 1), ("total_cost_of_revenue", -1)],
        ),
        (
            "costs_and_expenses",
            [("total_revenue", 1), ("total_operating_income", -1)],
        ),
        (
            "total_gross_profit",
            [("total_revenue", 1), ("total_cost_of_revenue", -1)],
        ),
        (
            "total_cost_of_revenue",
            [("total_revenue", 1), ("total_gross_profit", -1)],
        ),
        (
            "total_operating_expenses",
            [("total_gross_profit", 1), ("total_operating_income", -1)],
        ),
        (
            "total_operating_income",
            [("total_gross_profit", 1), ("total_operating_expenses", -1)],
        ),
        (
            "total_other_income",
            [
                ("total_pretax_income", 1),
                ("total_operating_income", -1),
                ("equity_method_investments", -1),
            ],
        ),
        (
            "total_other_income",
            [("total_pretax_income", 1), ("total_operating_income", -1)],
        ),
    ],
    "diversified": [
        (
            "total_operating_income",
            [("total_pretax_income", 1), ("total_other_income", -1)],
        ),
        (
            "total_operating_income",
            [("total_revenue", 1), ("costs_and_expenses", -1)],
        ),
        (
            "costs_and_expenses",
            [("total_revenue", 1), ("total_operating_income", -1)],
        ),
        (
            "total_other_income",
            [
                ("total_pretax_income", 1),
                ("total_operating_income", -1),
                ("equity_method_investments", -1),
            ],
        ),
        (
            "total_other_income",
            [("total_pretax_income", 1), ("total_operating_income", -1)],
        ),
    ],
    "financial": [
        (
            "total_interest_income",
            [("net_interest_income", 1), ("total_interest_expense", 1)],
        ),
        (
            "net_interest_income_after_provision",
            [("net_interest_income", 1), ("provision_for_credit_losses", -1)],
        ),
        (
            "total_revenue",
            [("net_interest_income", 1), ("total_noninterest_income", 1)],
        ),
        (
            "total_revenue",
            [
                ("total_pretax_income", 1),
                ("total_noninterest_expense", 1),
                ("provision_for_credit_losses", 1),
            ],
        ),
        (
            "total_revenue",
            [("total_pretax_income", 1), ("total_noninterest_expense", 1)],
        ),
    ],
    "insurance": [
        (
            "total_pretax_income",
            [("total_revenue", 1), ("benefits_costs_expenses", -1)],
        ),
        (
            "benefits_costs_expenses",
            [("total_revenue", 1), ("total_pretax_income", -1)],
        ),
    ],
}

IS_VERIFY: list[tuple[str, list[tuple[str, int]]]] = [
    (
        "total_pretax_income",
        [("net_income_continuing", 1), ("income_tax_expense", 1)],
    ),
    (
        "net_income_continuing",
        [("total_pretax_income", 1), ("income_tax_expense", -1)],
    ),
    (
        "total_gross_profit",
        [("total_revenue", 1), ("total_cost_of_revenue", -1)],
    ),
    (
        "total_operating_income",
        [("total_gross_profit", 1), ("total_operating_expenses", -1)],
    ),
]

BS_VERIFY: list[tuple[str, list[tuple[str, int]]]] = [
    ("total_assets", [("total_liabilities_and_equity", 1)]),
    (
        "total_equity_and_noncontrolling_interests",
        [("total_equity", 1), ("noncontrolling_interests", 1)],
    ),
    (
        "total_equity",
        [
            ("total_equity_and_noncontrolling_interests", 1),
            ("noncontrolling_interests", -1),
        ],
    ),
    (
        "total_liabilities",
        [
            ("total_liabilities_and_equity", 1),
            ("total_equity_and_noncontrolling_interests", -1),
            ("temporary_equity", -1),
        ],
    ),
    (
        "total_liabilities",
        [
            ("total_liabilities_and_equity", 1),
            ("total_equity_and_noncontrolling_interests", -1),
        ],
    ),
]

CF_VERIFY: list[tuple[str, list[tuple[str, int]]]] = [
    (
        "net_change_in_cash",
        [
            ("net_cash_from_operating_activities", 1),
            ("net_cash_from_investing_activities", 1),
            ("net_cash_from_financing_activities", 1),
            ("effect_of_exchange_rate_changes", 1),
        ],
    ),
    (
        "net_change_in_cash",
        [
            ("net_cash_from_operating_activities", 1),
            ("net_cash_from_investing_activities", 1),
            ("net_cash_from_financing_activities", 1),
        ],
    ),
    (
        "net_change_in_cash",
        [
            ("net_cash_from_operating_activities", 1),
            ("net_cash_from_investing_activities", 1),
            ("net_cash_from_financing_activities", 1),
            ("effect_of_exchange_rate_changes", 1),
            ("other_net_changes_in_cash", 1),
        ],
    ),
    (
        "net_change_in_cash",
        [
            ("net_cash_from_operating_activities", 1),
            ("net_cash_from_investing_activities", 1),
            ("net_cash_from_financing_activities", 1),
            ("other_net_changes_in_cash", 1),
        ],
    ),
]

IS_IMPUTE_COMMON: list[tuple[str, list[tuple[str, int]]]] = [
    (
        "total_pretax_income",
        [("net_income_continuing", 1), ("income_tax_expense", 1)],
    ),
    (
        "net_income_continuing",
        [("total_pretax_income", 1), ("income_tax_expense", -1)],
    ),
    ("net_income", [("net_income_continuing", 1), ("net_income_discontinued", 1)]),
    (
        "comprehensive_income",
        [("comprehensive_income_parent", 1), ("comprehensive_income_nci", 1)],
    ),
    (
        "comprehensive_income_parent",
        [("comprehensive_income", 1), ("comprehensive_income_nci", -1)],
    ),
    (
        "comprehensive_income_nci",
        [("comprehensive_income", 1), ("comprehensive_income_parent", -1)],
    ),
    (
        "income_tax_expense",
        [("income_tax_current", 1), ("income_tax_deferred", 1)],
    ),
    (
        "income_tax_current",
        [("income_tax_expense", 1), ("income_tax_deferred", -1)],
    ),
    (
        "income_tax_deferred",
        [("income_tax_expense", 1), ("income_tax_current", -1)],
    ),
    (
        "total_pretax_income",
        [("income_before_equity_method", 1), ("equity_method_investments", 1)],
    ),
    (
        "income_before_equity_method",
        [("total_pretax_income", 1), ("equity_method_investments", -1)],
    ),
    (
        "net_income_to_noncontrolling_interest",
        [("net_income_nci_redeemable", 1), ("net_income_nci_nonredeemable", 1)],
    ),
]

BS_IMPUTE: list[tuple[str, list[tuple[str, int]]]] = [
    ("gross_ppe", [("net_ppe", 1), ("accumulated_depreciation", 1)]),
    ("accumulated_depreciation", [("gross_ppe", 1), ("net_ppe", -1)]),
    (
        "total_noncurrent_assets",
        [("total_assets", 1), ("total_current_assets", -1)],
    ),
    (
        "total_noncurrent_liabilities",
        [("total_liabilities", 1), ("total_current_liabilities", -1)],
    ),
    ("total_liabilities_and_equity", [("total_assets", 1)]),
    (
        "total_liabilities",
        [
            ("total_liabilities_and_equity", 1),
            ("total_equity_and_noncontrolling_interests", -1),
            ("temporary_equity", -1),
        ],
    ),
    (
        "total_liabilities",
        [
            ("total_liabilities_and_equity", 1),
            ("total_equity_and_noncontrolling_interests", -1),
        ],
    ),
    (
        "total_equity_and_noncontrolling_interests",
        [("total_equity", 1), ("noncontrolling_interests", 1)],
    ),
    (
        "total_equity",
        [
            ("total_equity_and_noncontrolling_interests", 1),
            ("noncontrolling_interests", -1),
        ],
    ),
    ("total_common_equity", [("total_equity", 1), ("total_preferred_equity", -1)]),
    ("total_common_equity", [("total_equity", 1)]),
    ("total_equity_and_noncontrolling_interests", [("total_equity", 1)]),
    (
        "redeemable_noncontrolling_interest",
        [
            ("redeemable_nci_common", 1),
            ("redeemable_nci_preferred", 1),
            ("redeemable_nci_other", 1),
        ],
    ),
]

CF_IMPUTE: list[tuple[str, list[tuple[str, int]]]] = [
    (
        "net_change_in_cash",
        [
            ("net_cash_from_operating_activities", 1),
            ("net_cash_from_investing_activities", 1),
            ("net_cash_from_financing_activities", 1),
            ("effect_of_exchange_rate_changes", 1),
        ],
    ),
    (
        "depreciation_and_amortization",
        [("depreciation_expense", 1), ("amortization_expense", 1)],
    ),
]

OTHER_LINES: dict[str, tuple[str, ...]] = {
    "total_gross_profit": ("total_cost_of_revenue",),
    "total_operating_income": ("total_operating_expenses", "costs_and_expenses"),
    "total_pretax_income": ("total_other_income", "benefits_costs_expenses"),
    "total_other_income": ("other_income",),
    "costs_and_expenses": ("other_operating_expenses",),
    "total_noninterest_expense": ("other_operating_expenses",),
    "benefits_costs_expenses": ("other_operating_expenses",),
    "net_interest_income": ("total_interest_expense",),
    "net_income_to_common": ("other_adjustments_to_net_income_to_common",),
    "comprehensive_income": ("comprehensive_income_nci",),
    "total_assets": ("total_noncurrent_assets",),
    "total_liabilities": (
        "total_noncurrent_liabilities",
        "other_long_term_liabilities",
    ),
    "total_equity": ("total_common_equity",),
    "total_liabilities_and_equity": ("temporary_equity",),
    "redeemable_noncontrolling_interest": ("redeemable_nci_other",),
    "total_common_equity": ("other_equity",),
    "net_cash_from_continuing_operating_activities": ("other_operating_activities",),
    "increase_decrease_in_operating_capital": (
        "change_in_other_operating_assets_and_liabilities",
    ),
    "net_cash_from_continuing_investing_activities": (
        "other_investing_activities_net",
    ),
    "net_cash_from_continuing_financing_activities": (
        "other_financing_activities_net",
    ),
    "net_change_in_cash": ("other_net_changes_in_cash",),
}

ROLLUP_REQUIRES: dict[str, tuple[str, ...]] = {
    "total_gross_profit": ("total_cost_of_revenue",),
    "total_operating_income": (),
    "total_operating_expenses": (),
    "total_pretax_income": ("total_operating_income",),
    "net_interest_income": ("total_interest_expense",),
    "total_assets": ("total_noncurrent_assets",),
    "total_liabilities": ("total_noncurrent_liabilities",),
    "total_liabilities_and_equity": ("total_liabilities",),
    "comprehensive_income_parent": (),
    "comprehensive_income_nci": (),
}

WHOLE_REMAINDERS: frozenset[str] = frozenset({"total_equity"})

REMAINDER_REQUIRES: dict[str, tuple[str, ...]] = {
    "total_pretax_income": ("total_operating_income",),
}

ADDITIVE_PER_SHARE: frozenset[str] = frozenset({"cash_dividends_per_share"})

DILUTED_SHARES: dict[str, str] = {
    "weighted_ave_diluted_shares_os": "weighted_ave_basic_shares_os",
}

EPS_NUMERATOR = "net_income_to_common"

SINGLE_STEP: tuple[str, str, str] = (
    "total_revenue",
    "costs_and_expenses",
    "total_pretax_income",
)

EVIDENCED_LINES: dict[str, str] = {"temporary_equity": "total_liabilities"}

NONNEGATIVE_CONCEPTS: frozenset[str] = frozenset(
    {
        "us-gaap:AccountsPayableCurrent",
        "us-gaap:AccountsReceivableNetCurrent",
        "us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment",
        "us-gaap:CashAndCashEquivalentsAtCarryingValue",
        "us-gaap:CostOfGoodsAndServicesSold",
        "us-gaap:CostOfGoodsSold",
        "us-gaap:CostOfRevenue",
        "us-gaap:Depreciation",
        "us-gaap:Goodwill",
        "us-gaap:InterestAndDebtExpense",
        "us-gaap:InterestExpense",
        "us-gaap:InterestExpenseDebt",
        "us-gaap:InterestExpenseNonoperating",
        "us-gaap:InterestPaid",
        "us-gaap:InterestPaidNet",
        "us-gaap:InventoryNet",
        "us-gaap:LongTermDebtCurrent",
        "us-gaap:LongTermDebtNoncurrent",
        "us-gaap:PaymentsForRepurchaseOfCommonStock",
        "us-gaap:PaymentsOfDividends",
        "us-gaap:PaymentsOfDividendsCommonStock",
        "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",
        "us-gaap:PropertyPlantAndEquipmentGross",
        "us-gaap:ResearchAndDevelopmentExpense",
        "us-gaap:SellingGeneralAndAdministrativeExpense",
        "us-gaap:ShortTermBorrowings",
        "us-gaap:TreasuryStockCommonValue",
        "us-gaap:TreasuryStockValue",
    }
)

FILER_SCALES: tuple[int, ...] = (1_000, 1_000_000)
SCALED_FILING_MIN = 10
SCALE_SPAN = 1.0

WEIGHTED_SHARE_CONCEPTS = frozenset(
    {
        "ifrs-full:AdjustedWeightedAverageShares",
        "ifrs-full:WeightedAverageShares",
        "us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding",
        "us-gaap:WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        "us-gaap:WeightedAverageNumberOfSharesOutstandingBasic",
    }
)

NET_POSITIONS: dict[str, str] = {
    "us-gaap:AmortizationOfIntangibleAssets": "debit",
    "us-gaap:DeferredIncomeTaxLiabilities": "credit",
    "us-gaap:DeferredIncomeTaxLiabilitiesNet": "credit",
    "us-gaap:DeferredTaxAssetsLiabilitiesNetNoncurrent": "debit",
    "us-gaap:DeferredTaxLiabilities": "credit",
    "us-gaap:DeferredTaxLiabilitiesNoncurrent": "credit",
    "us-gaap:DepreciationAmortizationAndAccretionNet": "debit",
    "us-gaap:DepreciationAndAmortization": "debit",
    "us-gaap:DepreciationDepletionAndAmortization": "debit",
}

NONNEGATIVE_LINES: frozenset[str] = frozenset(
    {
        "temporary_equity",
        "total_noncurrent_assets",
        "total_noncurrent_liabilities",
        "total_cost_of_revenue",
        "costs_and_expenses",
        "total_interest_expense",
        "benefits_costs_expenses",
        "other_depreciation_and_amortization",
        "other_current_assets",
        "other_noncurrent_assets",
        "other_net_ppe",
        "other_current_liabilities",
        "other_noncurrent_liabilities",
        "other_temporary_equity",
    }
)

CLASSIFIED_SECTIONS: tuple[tuple[str, str], ...] = (
    ("total_current_assets", "total_noncurrent_assets"),
    ("total_current_liabilities", "total_noncurrent_liabilities"),
)

BALANCE_TOTALS: tuple[str, ...] = (
    "total_assets",
    "total_liabilities",
    "total_liabilities_and_equity",
)

CHAIN_SUBSETS: dict[str, tuple[tuple[str, str], ...]] = {
    "rd_expense": (
        (
            "us-gaap:ResearchAndDevelopmentExpense",
            "us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ),
    ),
    "total_revenue": (("us-gaap:Revenues", "us-gaap:SalesRevenueNet"),),
    "operating_revenue": (("us-gaap:Revenues", "us-gaap:SalesRevenueNet"),),
    "total_cost_of_revenue": (
        ("us-gaap:CostOfGoodsAndServicesSold", "us-gaap:CostOfRevenue"),
    ),
    "operating_cost_of_revenue": (
        ("us-gaap:CostOfGoodsAndServicesSold", "us-gaap:CostOfRevenue"),
    ),
}

SOFT_TOTALS: frozenset[str] = frozenset(
    {
        "net_cash_from_operating_activities",
        "net_cash_from_investing_activities",
        "net_cash_from_financing_activities",
    }
)

SCOPE_VARIANTS: frozenset[str] = frozenset(
    {
        "effect_of_exchange_rate_changes",
        "equity_method_investments",
        "excise_and_sales_taxes",
        "net_cash_from_discontinued_financing_activities",
        "net_cash_from_discontinued_investing_activities",
        "net_cash_from_discontinued_operating_activities",
        "net_income_discontinued",
        "other_gains",
        "preferred_dividends",
        "total_interest_expense",
        "total_interest_income",
    }
)

CONTAINABLE: frozenset[str] = frozenset(
    {
        "accrued_interest_payable",
        "asset_retirement_and_litigation_obligation",
        "capital_lease_obligations",
        "current_deferred_revenue",
        "current_deferred_tax_assets",
        "current_employee_benefit_liabilities",
        "current_portion_of_long_term_debt",
        "dividends_payable",
        "employee_benefit_assets",
        "finance_lease_liability_current",
        "finance_lease_right_of_use_asset",
        "interest_bearing_deposits_at_other_banks",
        "noncurrent_deferred_revenue",
        "noncurrent_deferred_tax_assets",
        "noncurrent_deferred_tax_liabilities",
        "noncurrent_employee_benefit_liabilities",
        "operating_lease_liability_current",
        "operating_lease_liability_noncurrent",
        "operating_lease_right_of_use_asset",
        "other_taxes_payable",
        "prepaid_expenses",
        "restricted_cash",
    }
)

PROMOTABLE_MEMOS: frozenset[str] = frozenset(
    {
        "depreciation_and_amortization",
        "net_cash_from_discontinued_operations",
        "total_operating_expenses",
    }
)

MAX_IMPUTE_PASSES: int = 10

CF_SIGN_KEEP: frozenset[str] = frozenset(
    {"net_income", "net_income_continuing", "net_income_discontinued"}
)

IDENTITIES: dict[str, tuple[tuple[str, tuple[tuple[str, int], ...] | None], ...]] = {
    "balance_sheet": (
        ("total_assets", (("total_liabilities_and_equity", 1),)),
        ("total_liabilities_and_equity", None),
        ("total_equity_and_noncontrolling_interests", None),
    ),
    "income_statement": (
        ("net_income_continuing", None),
        ("total_operating_income", None),
        ("total_gross_profit", None),
    ),
    "cash_flow": (
        ("net_change_in_cash", None),
        (
            "cash_at_end_of_period",
            (("cash_at_beginning_of_period", 1), ("net_change_in_cash", 1)),
        ),
    ),
}

BALANCE_IDENTITY_LINES: frozenset[str] = frozenset(
    {
        "total_assets",
        "total_liabilities",
        "temporary_equity",
        "total_equity_and_noncontrolling_interests",
        "total_equity",
        "noncontrolling_interests",
        "total_liabilities_and_equity",
    }
)
