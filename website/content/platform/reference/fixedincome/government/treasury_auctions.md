---
title: "treasury_auctions"
description: "Government Treasury Auctions"
keywords:
- fixedincome
- government
- treasury_auctions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/government/treasury_auctions - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Government Treasury Auctions.


Examples
--------

```python
from openbb import obb
obb.fixedincome.government.treasury_auctions(provider='government_us')
obb.fixedincome.government.treasury_auctions(security_type='Bill', start_date='2022-01-01', end_date='2023-01-01', provider='government_us')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| security_type | Literal['Bill', 'Note', 'Bond', 'CMB', 'TIPS', 'FRN'] | Used to only return securities of a particular type. | None | True |
| cusip | str | Filter securities by CUSIP. | None | True |
| page_size | int | Maximum number of results to return; you must also include pagenum when using pagesize. | None | True |
| page_num | int | The first page number to display results for; used in combination with page size. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. The default is 90 days ago. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. The default is today. | None | True |
| provider | Literal['government_us'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'government_us' if there is no default. | government_us | True |
</TabItem>

<TabItem value='government_us' label='government_us'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| security_type | Literal['Bill', 'Note', 'Bond', 'CMB', 'TIPS', 'FRN'] | Used to only return securities of a particular type. | None | True |
| cusip | str | Filter securities by CUSIP. | None | True |
| page_size | int | Maximum number of results to return; you must also include pagenum when using pagesize. | None | True |
| page_num | int | The first page number to display results for; used in combination with page size. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. The default is 90 days ago. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. The default is today. | None | True |
| provider | Literal['government_us'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'government_us' if there is no default. | government_us | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : TreasuryAuctions
        Serializable results.
    provider : Literal['government_us']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| cusip | str | CUSIP of the Security. |
| issue_date | date | The issue date of the security. |
| security_type | Literal['Bill', 'Note', 'Bond', 'CMB', 'TIPS', 'FRN'] | The type of security. |
| security_term | str | The term of the security. |
| maturity_date | date | The maturity date of the security. |
| interest_rate | float | The interest rate of the security. |
| cpi_on_issue_date | float | Reference CPI rate on the issue date of the security. |
| cpi_on_dated_date | float | Reference CPI rate on the dated date of the security. |
| announcement_date | date | The announcement date of the security. |
| auction_date | date | The auction date of the security. |
| auction_date_year | int | The auction date year of the security. |
| dated_date | date | The dated date of the security. |
| first_payment_date | date | The first payment date of the security. |
| accrued_interest_per_100 | float | Accrued interest per $100. |
| accrued_interest_per_1000 | float | Accrued interest per $1000. |
| adjusted_accrued_interest_per_100 | float | Adjusted accrued interest per $100. |
| adjusted_accrued_interest_per_1000 | float | Adjusted accrued interest per $1000. |
| adjusted_price | float | Adjusted price. |
| allocation_percentage | float | Allocation percentage, as normalized percentage points. |
| allocation_percentage_decimals | float | The number of decimals in the Allocation percentage. |
| announced_cusip | str | The announced CUSIP of the security. |
| auction_format | str | The auction format of the security. |
| avg_median_discount_rate | float | The average median discount rate of the security. |
| avg_median_investment_rate | float | The average median investment rate of the security. |
| avg_median_price | float | The average median price paid for the security. |
| avg_median_discount_margin | float | The average median discount margin of the security. |
| avg_median_yield | float | The average median yield of the security. |
| back_dated | Literal['Yes', 'No'] | Whether the security is back dated. |
| back_dated_date | date | The back dated date of the security. |
| bid_to_cover_ratio | float | The bid to cover ratio of the security. |
| call_date | date | The call date of the security. |
| callable | Literal['Yes', 'No'] | Whether the security is callable. |
| called_date | date | The called date of the security. |
| cash_management_bill | Literal['Yes', 'No'] | Whether the security is a cash management bill. |
| closing_time_competitive | str | The closing time for competitive bids on the security. |
| closing_time_non_competitive | str | The closing time for non-competitive bids on the security. |
| competitive_accepted | int | The accepted value for competitive bids on the security. |
| competitive_accepted_decimals | int | The number of decimals in the Competitive Accepted. |
| competitive_tendered | int | The tendered value for competitive bids on the security. |
| competitive_tenders_accepted | Literal['Yes', 'No'] | Whether competitive tenders are accepted on the security. |
| corp_us_cusip | str | The CUSIP of the security. |
| cpi_base_reference_period | str | The CPI base reference period of the security. |
| currently_outstanding | int | The currently outstanding value on the security. |
| direct_bidder_accepted | int | The accepted value from direct bidders on the security. |
| direct_bidder_tendered | int | The tendered value from direct bidders on the security. |
| est_amount_of_publicly_held_maturing_security | int | The estimated amount of publicly held maturing securities on the security. |
| fima_included | Literal['Yes', 'No'] | Whether the security is included in the FIMA (Foreign and International Money Authorities). |
| fima_non_competitive_accepted | int | The non-competitive accepted value on the security from FIMAs. |
| fima_non_competitive_tendered | int | The non-competitive tendered value on the security from FIMAs. |
| first_interest_period | str | The first interest period of the security. |
| first_interest_payment_date | date | The first interest payment date of the security. |
| floating_rate | Literal['Yes', 'No'] | Whether the security is a floating rate. |
| frn_index_determination_date | date | The FRN index determination date of the security. |
| frn_index_determination_rate | float | The FRN index determination rate of the security. |
| high_discount_rate | float | The high discount rate of the security. |
| high_investment_rate | float | The high investment rate of the security. |
| high_price | float | The high price of the security at auction. |
| high_discount_margin | float | The high discount margin of the security. |
| high_yield | float | The high yield of the security at auction. |
| index_ratio_on_issue_date | float | The index ratio on the issue date of the security. |
| indirect_bidder_accepted | int | The accepted value from indirect bidders on the security. |
| indirect_bidder_tendered | int | The tendered value from indirect bidders on the security. |
| interest_payment_frequency | str | The interest payment frequency of the security. |
| low_discount_rate | float | The low discount rate of the security. |
| low_investment_rate | float | The low investment rate of the security. |
| low_price | float | The low price of the security at auction. |
| low_discount_margin | float | The low discount margin of the security. |
| low_yield | float | The low yield of the security at auction. |
| maturing_date | date | The maturing date of the security. |
| max_competitive_award | int | The maximum competitive award at auction. |
| max_non_competitive_award | int | The maximum non-competitive award at auction. |
| max_single_bid | int | The maximum single bid at auction. |
| min_bid_amount | int | The minimum bid amount at auction. |
| min_strip_amount | int | The minimum strip amount at auction. |
| min_to_issue | int | The minimum to issue at auction. |
| multiples_to_bid | int | The multiples to bid at auction. |
| multiples_to_issue | int | The multiples to issue at auction. |
| nlp_exclusion_amount | int | The NLP exclusion amount at auction. |
| nlp_reporting_threshold | int | The NLP reporting threshold at auction. |
| non_competitive_accepted | int | The accepted value from non-competitive bidders on the security. |
| non_competitive_tenders_accepted | Literal['Yes', 'No'] | Whether or not the auction accepted non-competitive tenders. |
| offering_amount | int | The offering amount at auction. |
| original_cusip | str | The original CUSIP of the security. |
| original_dated_date | date | The original dated date of the security. |
| original_issue_date | date | The original issue date of the security. |
| original_security_term | str | The original term of the security. |
| pdf_announcement | str | The PDF filename for the announcement of the security. |
| pdf_competitive_results | str | The PDF filename for the competitive results of the security. |
| pdf_non_competitive_results | str | The PDF filename for the non-competitive results of the security. |
| pdf_special_announcement | str | The PDF filename for the special announcements. |
| price_per_100 | float | The price per 100 of the security. |
| primary_dealer_accepted | int | The primary dealer accepted value on the security. |
| primary_dealer_tendered | int | The primary dealer tendered value on the security. |
| reopening | Literal['Yes', 'No'] | Whether or not the auction was reopened. |
| security_term_day_month | str | The security term in days or months. |
| security_term_week_year | str | The security term in weeks or years. |
| series | str | The series name of the security. |
| soma_accepted | int | The SOMA accepted value on the security. |
| soma_holdings | int | The SOMA holdings on the security. |
| soma_included | Literal['Yes', 'No'] | Whether or not the SOMA (System Open Market Account) was included on the security. |
| soma_tendered | int | The SOMA tendered value on the security. |
| spread | float | The spread on the security. |
| standard_payment_per_1000 | float | The standard payment per 1000 of the security. |
| strippable | Literal['Yes', 'No'] | Whether or not the security is strippable. |
| term | str | The term of the security. |
| tiin_conversion_factor_per_1000 | float | The TIIN conversion factor per 1000 of the security. |
| tips | Literal['Yes', 'No'] | Whether or not the security is TIPS. |
| total_accepted | int | The total accepted value at auction. |
| total_tendered | int | The total tendered value at auction. |
| treasury_retail_accepted | int | The accepted value on the security from retail. |
| treasury_retail_tenders_accepted | Literal['Yes', 'No'] | Whether or not the tender offers from retail are accepted |
| type | str | The type of issuance. This might be different than the security type. |
| unadjusted_accrued_interest_per_1000 | float | The unadjusted accrued interest per 1000 of the security. |
| unadjusted_price | float | The unadjusted price of the security. |
| updated_timestamp | datetime | The updated timestamp of the security. |
| xml_announcement | str | The XML filename for the announcement of the security. |
| xml_competitive_results | str | The XML filename for the competitive results of the security. |
| xml_special_announcement | str | The XML filename for special announcements. |
| tint_cusip1 | str | Tint CUSIP 1. |
| tint_cusip2 | str | Tint CUSIP 2. |
</TabItem>

<TabItem value='government_us' label='government_us'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| cusip | str | CUSIP of the Security. |
| issue_date | date | The issue date of the security. |
| security_type | Literal['Bill', 'Note', 'Bond', 'CMB', 'TIPS', 'FRN'] | The type of security. |
| security_term | str | The term of the security. |
| maturity_date | date | The maturity date of the security. |
| interest_rate | float | The interest rate of the security. |
| cpi_on_issue_date | float | Reference CPI rate on the issue date of the security. |
| cpi_on_dated_date | float | Reference CPI rate on the dated date of the security. |
| announcement_date | date | The announcement date of the security. |
| auction_date | date | The auction date of the security. |
| auction_date_year | int | The auction date year of the security. |
| dated_date | date | The dated date of the security. |
| first_payment_date | date | The first payment date of the security. |
| accrued_interest_per_100 | float | Accrued interest per $100. |
| accrued_interest_per_1000 | float | Accrued interest per $1000. |
| adjusted_accrued_interest_per_100 | float | Adjusted accrued interest per $100. |
| adjusted_accrued_interest_per_1000 | float | Adjusted accrued interest per $1000. |
| adjusted_price | float | Adjusted price. |
| allocation_percentage | float | Allocation percentage, as normalized percentage points. |
| allocation_percentage_decimals | float | The number of decimals in the Allocation percentage. |
| announced_cusip | str | The announced CUSIP of the security. |
| auction_format | str | The auction format of the security. |
| avg_median_discount_rate | float | The average median discount rate of the security. |
| avg_median_investment_rate | float | The average median investment rate of the security. |
| avg_median_price | float | The average median price paid for the security. |
| avg_median_discount_margin | float | The average median discount margin of the security. |
| avg_median_yield | float | The average median yield of the security. |
| back_dated | Literal['Yes', 'No'] | Whether the security is back dated. |
| back_dated_date | date | The back dated date of the security. |
| bid_to_cover_ratio | float | The bid to cover ratio of the security. |
| call_date | date | The call date of the security. |
| callable | Literal['Yes', 'No'] | Whether the security is callable. |
| called_date | date | The called date of the security. |
| cash_management_bill | Literal['Yes', 'No'] | Whether the security is a cash management bill. |
| closing_time_competitive | str | The closing time for competitive bids on the security. |
| closing_time_non_competitive | str | The closing time for non-competitive bids on the security. |
| competitive_accepted | int | The accepted value for competitive bids on the security. |
| competitive_accepted_decimals | int | The number of decimals in the Competitive Accepted. |
| competitive_tendered | int | The tendered value for competitive bids on the security. |
| competitive_tenders_accepted | Literal['Yes', 'No'] | Whether competitive tenders are accepted on the security. |
| corp_us_cusip | str | The CUSIP of the security. |
| cpi_base_reference_period | str | The CPI base reference period of the security. |
| currently_outstanding | int | The currently outstanding value on the security. |
| direct_bidder_accepted | int | The accepted value from direct bidders on the security. |
| direct_bidder_tendered | int | The tendered value from direct bidders on the security. |
| est_amount_of_publicly_held_maturing_security | int | The estimated amount of publicly held maturing securities on the security. |
| fima_included | Literal['Yes', 'No'] | Whether the security is included in the FIMA (Foreign and International Money Authorities). |
| fima_non_competitive_accepted | int | The non-competitive accepted value on the security from FIMAs. |
| fima_non_competitive_tendered | int | The non-competitive tendered value on the security from FIMAs. |
| first_interest_period | str | The first interest period of the security. |
| first_interest_payment_date | date | The first interest payment date of the security. |
| floating_rate | Literal['Yes', 'No'] | Whether the security is a floating rate. |
| frn_index_determination_date | date | The FRN index determination date of the security. |
| frn_index_determination_rate | float | The FRN index determination rate of the security. |
| high_discount_rate | float | The high discount rate of the security. |
| high_investment_rate | float | The high investment rate of the security. |
| high_price | float | The high price of the security at auction. |
| high_discount_margin | float | The high discount margin of the security. |
| high_yield | float | The high yield of the security at auction. |
| index_ratio_on_issue_date | float | The index ratio on the issue date of the security. |
| indirect_bidder_accepted | int | The accepted value from indirect bidders on the security. |
| indirect_bidder_tendered | int | The tendered value from indirect bidders on the security. |
| interest_payment_frequency | str | The interest payment frequency of the security. |
| low_discount_rate | float | The low discount rate of the security. |
| low_investment_rate | float | The low investment rate of the security. |
| low_price | float | The low price of the security at auction. |
| low_discount_margin | float | The low discount margin of the security. |
| low_yield | float | The low yield of the security at auction. |
| maturing_date | date | The maturing date of the security. |
| max_competitive_award | int | The maximum competitive award at auction. |
| max_non_competitive_award | int | The maximum non-competitive award at auction. |
| max_single_bid | int | The maximum single bid at auction. |
| min_bid_amount | int | The minimum bid amount at auction. |
| min_strip_amount | int | The minimum strip amount at auction. |
| min_to_issue | int | The minimum to issue at auction. |
| multiples_to_bid | int | The multiples to bid at auction. |
| multiples_to_issue | int | The multiples to issue at auction. |
| nlp_exclusion_amount | int | The NLP exclusion amount at auction. |
| nlp_reporting_threshold | int | The NLP reporting threshold at auction. |
| non_competitive_accepted | int | The accepted value from non-competitive bidders on the security. |
| non_competitive_tenders_accepted | Literal['Yes', 'No'] | Whether or not the auction accepted non-competitive tenders. |
| offering_amount | int | The offering amount at auction. |
| original_cusip | str | The original CUSIP of the security. |
| original_dated_date | date | The original dated date of the security. |
| original_issue_date | date | The original issue date of the security. |
| original_security_term | str | The original term of the security. |
| pdf_announcement | str | The PDF filename for the announcement of the security. |
| pdf_competitive_results | str | The PDF filename for the competitive results of the security. |
| pdf_non_competitive_results | str | The PDF filename for the non-competitive results of the security. |
| pdf_special_announcement | str | The PDF filename for the special announcements. |
| price_per_100 | float | The price per 100 of the security. |
| primary_dealer_accepted | int | The primary dealer accepted value on the security. |
| primary_dealer_tendered | int | The primary dealer tendered value on the security. |
| reopening | Literal['Yes', 'No'] | Whether or not the auction was reopened. |
| security_term_day_month | str | The security term in days or months. |
| security_term_week_year | str | The security term in weeks or years. |
| series | str | The series name of the security. |
| soma_accepted | int | The SOMA accepted value on the security. |
| soma_holdings | int | The SOMA holdings on the security. |
| soma_included | Literal['Yes', 'No'] | Whether or not the SOMA (System Open Market Account) was included on the security. |
| soma_tendered | int | The SOMA tendered value on the security. |
| spread | float | The spread on the security. |
| standard_payment_per_1000 | float | The standard payment per 1000 of the security. |
| strippable | Literal['Yes', 'No'] | Whether or not the security is strippable. |
| term | str | The term of the security. |
| tiin_conversion_factor_per_1000 | float | The TIIN conversion factor per 1000 of the security. |
| tips | Literal['Yes', 'No'] | Whether or not the security is TIPS. |
| total_accepted | int | The total accepted value at auction. |
| total_tendered | int | The total tendered value at auction. |
| treasury_retail_accepted | int | The accepted value on the security from retail. |
| treasury_retail_tenders_accepted | Literal['Yes', 'No'] | Whether or not the tender offers from retail are accepted |
| type | str | The type of issuance. This might be different than the security type. |
| unadjusted_accrued_interest_per_1000 | float | The unadjusted accrued interest per 1000 of the security. |
| unadjusted_price | float | The unadjusted price of the security. |
| updated_timestamp | datetime | The updated timestamp of the security. |
| xml_announcement | str | The XML filename for the announcement of the security. |
| xml_competitive_results | str | The XML filename for the competitive results of the security. |
| xml_special_announcement | str | The XML filename for special announcements. |
| tint_cusip1 | str | Tint CUSIP 1. |
| tint_cusip2 | str | Tint CUSIP 2. |
</TabItem>

</Tabs>

