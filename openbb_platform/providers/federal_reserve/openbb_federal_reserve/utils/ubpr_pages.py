"""FFIEC UBPR per-page descriptions, keyed by report section."""

UBPR_PAGE_DESCRIPTIONS = {
    "Summary Ratios": (
        "The earnings and balance sheet ratios and other information presented on"
        " this page provide a synopsis of the bank's condition and serve as a guide"
        " to more detailed data presented elsewhere in the UBPR. Ratios using after"
        " tax income and dividends have been adjusted for assumed tax rates."
    ),
    "Income Statement $": (
        "This page presents a summary of the bank's year-to-date Report of Income."
        " The major categories of income and expense reported on this page are"
        " expanded on subsequent pages of the UBPR. The tax benefit associated with"
        " tax-exempt income has been estimated and added to total interest income"
        " and applicable income taxes, allocated to municipal securities and to"
        " municipal loans and leases, improving the comparability of interest income"
        " among different banks and time periods. Net income is shown as reported."
    ),
    "QTR Income Statement $": (
        "This page presents quarterly earnings for each quarter presented, which can"
        " assist the user to see differences in quarterly earnings and identify"
        " reasons for the differences."
    ),
    "Noninterest Income and Expenses": (
        "This page presents most of the dollar figures that are components of"
        " noninterest income and overhead expense as reported in the Report of"
        " Income, together with related information such as number of offices. Key"
        " overhead items are also presented as percent of average assets, together"
        " with other related ratios."
    ),
    "Asset Yields and Funding Costs": (
        "This page presents the yield on earning assets and costs of funding"
        " sources. Assets and liabilities as a percentage of average assets are"
        " also shown."
    ),
    "Balance Sheet $": (
        "This page presents end-of-period figures to facilitate comparison of asset"
        " and liability composition from period to period. The major components of"
        " total assets have been aligned into earning and nonearning asset"
        " categories to facilitate earning asset analysis. Annual and one-quarter"
        " percentage changes are provided for most of the data on this page. Data"
        " comes from Call Report Schedules RC, RC-B, RC-C, RC-D, and RC-E."
    ),
    "Off Balance Sheet Items": (
        "The top part of this page presents the amounts of various selected"
        " commitments, contingencies, contracts and other items reported in Call"
        " Report Schedule RC-L (Commitments and Contingencies) that are not reported"
        " as part of the balance sheet, presented as a percent of total assets. The"
        " bottom half displays the same information in dollar format with annual and"
        " one-quarter percentage changes."
    ),
    "Derivative Instruments": (
        "This page presents the amounts of derivatives and related information in"
        " thousands of dollars. The information comes mostly from Call Report"
        " Schedule RC-L Off-Balance Sheet Items, but also from Schedules RC-M"
        " Memoranda, RC-N Past Due and Nonaccrual Loans, Leases and Other Assets,"
        " RC-R Regulatory Capital, and the RI Report of Income memoranda section."
        " Derivatives are summarized using the position indicators in the Call"
        " Report Schedule RC-L matrix."
    ),
    "Derivative Analysis": (
        "This page presents the amounts of derivatives and related information in"
        " percentage format, generally in comparison to total derivatives."
        " Derivatives are summarized using the position indicators in Call Report"
        " Schedule RC-L matrix."
    ),
    "Balance Sheet %": (
        "This page presents the major components of assets, liabilities, and capital"
        " as a percentage of total assets. Averages used on this page are a"
        " year-to-date average of end-of-period balances, including the prior"
        " year-end."
    ),
    "Allowance & Loan Mix-a": (
        "This page presents data regarding the allowance for credit losses. The"
        " dollar figures provide a reconcilement of changes to the reserve from"
        " Schedule RI-B, and the ratios are provided to highlight trends and permit"
        " assessment of the adequacy of the reserve."
    ),
    "Allowance & Loan Mix-b": (
        "Loans are distributed by category as a percent of average gross loans,"
        " averaged using the ending balance for the prior year-end plus the interim"
        " quarters for the current year. Data comes from Call Report Schedule RC-C."
        " If the bank has foreign offices (FFIEC 031 filer), categories represent"
        " balances in domestic offices only, with loans booked in foreign offices"
        " shown as a separate category; otherwise balances are consolidated."
    ),
    "Concentrations of Credit": (
        "This page presents ratios for loans by category as a percentage of Tier 1"
        " Capital plus the Allowance for Credit Losses on loans held for investment."
        " Data comes from Call Report Schedule RC-C."
    ),
    "PD, Nonacc & Rest Loans-a": (
        "This page presents ratios for past due real estate loans as well as"
        " numerical values for noncurrent, guaranteed, modified, and restructured"
        " loans. The information comes from Call Report Schedule RC-N memoranda;"
        " ratios divide the individual past due loan category by the corresponding"
        " balance from Schedule RC-C. Each category displays loans 90+ days past"
        " due, loans on nonaccrual, total noncurrent, and loans 30-89 days past due."
    ),
    "PD, Nonacc & Rest Loans-b": (
        "This page presents information for past due loans not secured by real"
        " estate, as well as information on noncurrent, guaranteed, modified, and"
        " restructured loans. Ratios divide the individual past due loan category by"
        " the corresponding balance from Call Report Schedule RC-C. Each category"
        " displays loans 90+ days past due, loans on nonaccrual, total noncurrent,"
        " and loans 30-89 days past due."
    ),
    "Interest Rate Risk-a": (
        "The Interest Rate Risk Analysis pages present information that may be used"
        " to assess the interest rate risk inherent in a bank's balance sheet. Most"
        " of the underlying repricing data is reported in the memoranda sections of"
        " Call Report Schedules RC-B, RC-C, and RC-E as well as on RC."
    ),
    "Interest Rate Risk-b": (
        "The Interest Rate Risk Analysis pages present information that may be used"
        " to assess the interest rate risk inherent in a bank's balance sheet. Most"
        " of the underlying repricing data is reported in the memoranda sections of"
        " Call Report Schedules RC-B, RC-C, and RC-E as well as on RC."
    ),
    "Liquidity & Funding": (
        "The top portion of the page presents liquid asset ratios, wholesale funding"
        " ratios, and deposit composition ratios expressed as a percentage of total"
        " assets. The bottom portion presents dollar information used in the Net"
        " Noncore Funding Dependence ratio."
    ),
    "Liquidity & Inv Portfolio": (
        "The top portion of the page presents growth rates on key asset and"
        " liability categories. The middle portion displays principal components of"
        " the investment portfolio expressed as a percentage of total investment"
        " securities and Tier 1 Capital. The bottom portion provides ratios covering"
        " unrealized investment portfolio appreciation/depreciation, pledged assets,"
        " and debt securities maturing within one year."
    ),
    "Capital Analysis-a": (
        "This page presents end-of-period capital by Call Report definition, a"
        " reconcilement of total equity capital from period to period, an analysis"
        " of intangible assets, and a series of capital ratios. Ratios using after"
        " tax income and dividends have been adjusted for assumed tax rates."
    ),
    "Capital Analysis-b": (
        "This page presents dollar information and is meant to mimic Call Report"
        " Schedule RC-R, Part I Regulatory Capital Components and Ratios. Tier 1,"
        " Tier 2, and Total Capital values are shown, along with adjustments (stand"
        " alone or aggregated) to Tier 1 and Tier 2 Capital."
    ),
    "Capital Analysis-c": (
        "This page provides a detailed breakout of an institution's risk-weighted"
        " assets. Assets and credit equivalent amounts of derivatives and"
        " off-balance sheet items are assigned to broad risk categories; the"
        " aggregate amount in each is multiplied by the associated risk weights, and"
        " the sum of the weighted values equals total risk-weighted assets, the"
        " denominator for the Risk-Based Capital ratios. Banks electing the"
        " Community Bank Leverage Ratio (CBLR) do not report risk-weighted assets or"
        " risk-based capital ratios. The bottom of the page displays notional"
        " principal amounts of derivatives from Call Report Schedule RC-R."
    ),
    "Income Statement 1-Qtr-Ann": (
        "This page presents a quarter-by-quarter analysis of income and expense,"
        " showing five consecutive single quarters of historical financial"
        " information. The analysis differs from the year-to-date presentation"
        " elsewhere in the UBPR in that the income or expense attributed to one"
        " quarter is annualized (multiplied by 4) and compared to average asset or"
        " liability balances for that quarter, letting the user associate changes in"
        " earnings with a specific quarter."
    ),
    "Securitization & Asset Sale-a": (
        "Data on bank securitization activities comes principally from Call Report"
        " Schedule RC-S. Bank information is presented in dollar and percentage"
        " formats and no peer group information is calculated. One year and"
        " annualized quarterly growth rates are calculated for dollar items."
    ),
    "Securitization & Asset Sale-b": (
        "The type of securitization is expressed as a percentage of total"
        " securitized and sold assets by type."
    ),
    "Securitization & Asset Sale-c": (
        "This page presents ratios for past due securitized assets and annualized"
        " net charge-offs for securitizations."
    ),
    "Fiduciary Services-a": (
        "Information on fiduciary and related services is reported by banks on Call"
        " Report Schedule RC-T, available from December 31, 2001 forward. Several"
        " reporting limitations apply: most fiduciary income data was confidential"
        " prior to 2009, and depending on asset size and the percentage of trust and"
        " related revenue to total income, an institution may report certain items"
        " quarterly, annually, or not at all."
    ),
    "Fiduciary Services-b": (
        "This page displays an analysis of losses on fiduciary accounts. To provide"
        " a basis for analysis, average ratios are calculated for a peer group of"
        " comparably sized banks and a percentile ranking is developed for each"
        " income and loss ratio. Information is also presented on managed assets in"
        " fiduciary accounts. Data presented on this page is only reported on the"
        " December 31 Call Report."
    ),
}
