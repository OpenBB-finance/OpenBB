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
            ("redeemable_noncontrolling_interest", -1),
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
            ("redeemable_noncontrolling_interest", -1),
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
    (
        "redeemable_noncontrolling_interest",
        [
            ("total_liabilities_and_equity", 1),
            ("total_liabilities", -1),
            ("total_equity_and_noncontrolling_interests", -1),
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
        "effect_of_exchange_rate_changes",
        [
            ("net_change_in_cash", 1),
            ("net_cash_from_operating_activities", -1),
            ("net_cash_from_investing_activities", -1),
            ("net_cash_from_financing_activities", -1),
        ],
    ),
    (
        "depreciation_and_amortization",
        [("depreciation_expense", 1), ("amortization_expense", 1)],
    ),
]

MAX_IMPUTE_PASSES: int = 10
