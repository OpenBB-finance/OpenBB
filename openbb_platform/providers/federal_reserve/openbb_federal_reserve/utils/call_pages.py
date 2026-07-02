"""FFIEC Call Report per-schedule descriptions, keyed by section title."""

CALL_PAGE_DESCRIPTIONS = {
    "Schedule RI - Income Statement": (
        "The Report of Income presents the bank's year-to-date interest income,"
        " interest expense, noninterest income, noninterest expense, provisions,"
        " realized gains and losses on securities, applicable income taxes, and"
        " net income, together with the memoranda items that supplement them."
    ),
    "Schedule RI-A - Changes in Bank Equity Capital": (
        "Reconciles total bank equity capital from the prior period to the current"
        " period, capturing net income, dividends declared, sales and redemptions"
        " of capital, other comprehensive income, and other adjustments."
    ),
    "Schedule RI-B Part I - Charge-offs and Recoveries on Loans and Leases": (
        "Reports charge-offs and recoveries on loans and leases held for"
        " investment by loan category, the gross and net amounts that flow through"
        " the allowance for credit losses during the period."
    ),
    "Schedule RI-B Part II - Changes in Allowances for Credit Losses": (
        "Reconciles the allowance for credit losses on loans and leases from the"
        " prior period balance through charge-offs, recoveries, provisions, and"
        " other adjustments to the current period balance."
    ),
    "Schedule RI-C - Disaggregated Data on the Allowances for Credit Losses": (
        "Disaggregates the allowance for credit losses and the amortized cost of"
        " the related assets by portfolio segment and measurement methodology,"
        " reported by banks that have adopted the CECL accounting standard."
    ),
    "Schedule RI-D - Income from Foreign Offices": (
        "Reports income, expense, and selected balances attributable to the bank's"
        " foreign offices, Edge and Agreement subsidiaries, and IBFs, filed by"
        " banks with significant foreign activities."
    ),
    "Schedule RI-E - Explanations": (
        "Itemizes the larger components of the other income, other expense, and"
        " other capital and allowance line items reported elsewhere in the Report"
        " of Income, with a written description and dollar amount for each"
        " component that exceeds the reporting threshold."
    ),
    "Schedule RC - Balance Sheet": (
        "The Report of Condition presents the bank's end-of-period assets,"
        " liabilities, and equity capital, the consolidated balance sheet that the"
        " remaining RC schedules expand into detail."
    ),
    "Schedule RC-A - Cash and Balances Due From Depository Institutions": (
        "Details cash and balances due from depository institutions, separating"
        " noninterest-bearing and interest-bearing balances, currency and coin, and"
        " balances due from Federal Reserve Banks."
    ),
    "Schedule RC-B - Securities": (
        "Reports the amortized cost and fair value of held-to-maturity and"
        " available-for-sale securities by security type, together with pledged"
        " securities and the remaining-maturity and repricing memoranda."
    ),
    "Schedule RC-C Part I - Loans and Leases": (
        "Distributes loans and leases held for investment by category — real"
        " estate, commercial and industrial, consumer, agricultural, and other —"
        " the principal detail behind total loans on the balance sheet."
    ),
    "Schedule RC-C Part II - Loans to Small Businesses and Small Farms": (
        "Reports the number and amount of small-business and small-farm loans,"
        " those with original amounts at or below the regulatory thresholds,"
        " collected on the June 30 report."
    ),
    "Schedule RC-D - Trading Assets and Liabilities": (
        "Reports trading assets and trading liabilities at fair value by"
        " instrument type, filed by banks that meet the trading-activity reporting"
        " thresholds."
    ),
    "Schedule RC-E - Deposit Liabilities": (
        "Reports deposit liabilities by depositor type and product, distinguishing"
        " transaction and nontransaction accounts, with memoranda on brokered,"
        " time, and retirement deposits."
    ),
    "Schedule RC-E Part I - Deposits in Domestic Offices": (
        "Reports deposits in the bank's domestic offices by depositor type and"
        " account category, the domestic-office detail behind total deposits for"
        " banks that also hold foreign-office deposits."
    ),
    "Schedule RC-F - Other Assets": (
        "Itemizes the components of other assets reported on the balance sheet,"
        " including accrued interest receivable, net deferred tax assets, equity"
        " securities without readily determinable fair values, and bank-owned life"
        " insurance."
    ),
    "Schedule RC-G - Other Liabilities": (
        "Itemizes the components of other liabilities reported on the balance"
        " sheet, including accrued interest payable, net deferred tax liabilities,"
        " and the allowance for credit losses on off-balance-sheet exposures."
    ),
    "Schedule RC-H - Selected Balance Sheet Items for Domestic Offices": (
        "Reports selected asset, liability, and off-balance-sheet items for the"
        " bank's domestic offices only, filed by banks with foreign offices to"
        " isolate domestic activity."
    ),
    "Schedule RC-I - Assets and Liabilities of IBFs": (
        "Reports the total assets and total liabilities of the bank's"
        " International Banking Facilities, filed by banks that operate an IBF."
    ),
    "Schedule RC-K - Quarterly Averages": (
        "Reports quarterly average balances for the major categories of"
        " interest-earning assets, interest-bearing liabilities, and total assets,"
        " the averages used to compute yields and funding costs."
    ),
    "Schedule RC-L - Derivatives and Off-Balance Sheet Items": (
        "Reports commitments, contingencies, and derivative contracts not carried"
        " on the balance sheet — unused commitments, letters of credit, notional"
        " derivative amounts, and related fair values by contract type."
    ),
    "Schedule RC-M - Memoranda": (
        "Collects supplemental memoranda on insider extensions of credit, other"
        " borrowed money, intangible assets, other real estate owned, variable"
        " interest entities, brokered deposits, and other items."
    ),
    "Schedule RC-N - Past Due and Nonaccrual Loans Leases and Other Assets": (
        "Reports loans, leases, and other assets that are past due 30-89 days,"
        " past due 90 days or more and still accruing, or in nonaccrual status, by"
        " asset category, with the related guaranteed and restructured memoranda."
    ),
    "Schedule RC-O - Other Data for Deposit Insurance and FICO Assessments": (
        "Reports the data used to determine the bank's deposit insurance"
        " assessment base and FICO assessment, including estimated insured and"
        " uninsured deposits and the assessment-base adjustments."
    ),
    "Schedule RC-P - 1-4 Family Residential Mortgage Banking Activities": (
        "Reports retail originations, sales, and repurchases of 1-4 family"
        " residential mortgages and the related noninterest income, filed by banks"
        " that meet the mortgage-banking activity thresholds."
    ),
    "Schedule RC-Q - Assets and Liabilities Measured at Fair Value on a"
    " Recurring Basis": (
        "Reports the assets and liabilities measured at fair value on a recurring"
        " basis, distributed across the Level 1, Level 2, and Level 3 fair-value"
        " hierarchy, filed by banks meeting the reporting thresholds."
    ),
    "Schedule RC-R Part I - Regulatory Capital Components and Ratios": (
        "Reports the components of common equity tier 1, additional tier 1, and"
        " tier 2 capital, the regulatory deductions and adjustments, and the"
        " resulting risk-based and leverage capital ratios."
    ),
    "Schedule RC-R Part II - Risk-Weighted Assets": (
        "Distributes on- and off-balance-sheet exposures and derivative credit"
        " equivalents across the standardized risk-weight categories, the"
        " denominator of the risk-based capital ratios."
    ),
    "Schedule RC-S - Servicing Securitization and Asset Sale Activities": (
        "Reports the bank's securitization and asset-sale activities, including"
        " outstanding securitized balances, retained credit exposures, and the"
        " servicing of loans for others, by asset type."
    ),
    "Schedule RC-T - Fiduciary and Related Services": (
        "Reports the bank's fiduciary and related services activity, including"
        " managed and non-managed fiduciary account balances, fiduciary and"
        " related income, and fiduciary settlements and losses."
    ),
    "Schedule RC-V - Variable Interest Entities": (
        "Reports the assets and liabilities of consolidated variable interest"
        " entities, separating securitization vehicles from other VIEs, filed by"
        " banks that consolidate such entities."
    ),
    "Schedule SU - Supplemental Information": (
        "Collects the supplemental information items reported by FFIEC 051 filers"
        " in place of the detailed schedules that those banks are exempt from"
        " filing."
    ),
}
