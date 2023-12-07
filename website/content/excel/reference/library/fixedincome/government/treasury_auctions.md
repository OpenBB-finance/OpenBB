---
title: treasury_auctions
description: Government Treasury Auctions
keywords: 
- fixedincome
- government
- treasury_auctions
---

<!-- markdownlint-disable MD041 -->

Government Treasury Auctions.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.GOVERNMENT.TREASURY_AUCTIONS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: government_us | True |
| type | Any | Used to only return securities of a particular type. | True |
| cusip | Text | Filter securities by CUSIP. | True |
| pagesize | Number | Maximum number of results to return; you must also include pagenum when using pagesize. | True |
| pagenum | Number | The first page number to display results for; used in combination with page size. | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. The default is 90 days ago. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. The default is today. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| cusip | CUSIP of the Security.  |
| issue_date | The issue date of the security.  |
| security_type | The type of security.  |
| security_term | The term of the security.  |
| maturity_date | The maturity date of the security.  |
| interest_rate | The interest rate of the security.  |
| cpi_on_issue_date | Reference CPI rate on the issue date of the security.  |
| cpi_on_dated_date | Reference CPI rate on the dated date of the security.  |
| announcement_date | The announcement date of the security.  |
| auction_date | The auction date of the security.  |
| auction_date_year | The auction date year of the security.  |
| dated_date | The dated date of the security.  |
| first_payment_date | The first payment date of the security.  |
| accrued_interest_per_100 | Accrued interest per $100.  |
| accrued_interest_per_1000 | Accrued interest per $1000.  |
| adjusted_accrued_interest_per_100 | Adjusted accrued interest per $100.  |
| adjusted_accrued_interest_per_1000 | Adjusted accrued interest per $1000.  |
| adjusted_price | Adjusted price.  |
| allocation_percentage | Allocation percentage, as normalized percentage points.  |
| allocation_percentage_decimals | The number of decimals in the Allocation percentage.  |
| announced_cusip | The announced CUSIP of the security.  |
| auction_format | The auction format of the security.  |
| avg_median_discount_rate | The average median discount rate of the security.  |
| avg_median_investment_rate | The average median investment rate of the security.  |
| avg_median_price | The average median price paid for the security.  |
| avg_median_discount_margin | The average median discount margin of the security.  |
| avg_median_yield | The average median yield of the security.  |
| back_dated | Whether the security is back dated.  |
| back_dated_date | The back dated date of the security.  |
| bid_to_cover_ratio | The bid to cover ratio of the security.  |
| call_date | The call date of the security.  |
| callable | Whether the security is callable.  |
| called_date | The called date of the security.  |
| cash_management_bill | Whether the security is a cash management bill.  |
| closing_time_competitive | The closing time for competitive bids on the security.  |
| closing_time_non_competitive | The closing time for non-competitive bids on the security.  |
| competitive_accepted | The accepted value for competitive bids on the security.  |
| competitive_accepted_decimals | The number of decimals in the Competitive Accepted.  |
| competitive_tendered | The tendered value for competitive bids on the security.  |
| competitive_tenders_accepted | Whether competitive tenders are accepted on the security.  |
| corp_us_cusip | The CUSIP of the security.  |
| cpi_base_reference_period | The CPI base reference period of the security.  |
| currently_outstanding | The currently outstanding value on the security.  |
| direct_bidder_accepted | The accepted value from direct bidders on the security.  |
| direct_bidder_tendered | The tendered value from direct bidders on the security.  |
| est_amount_of_publicly_held_maturing_security | The estimated amount of publicly held maturing securities on the security.  |
| fima_included | Whether the security is included in the FIMA (Foreign and International Money Authorities).  |
| fima_non_competitive_accepted | The non-competitive accepted value on the security from FIMAs.  |
| fima_non_competitive_tendered | The non-competitive tendered value on the security from FIMAs.  |
| first_interest_period | The first interest period of the security.  |
| first_interest_payment_date | The first interest payment date of the security.  |
| floating_rate | Whether the security is a floating rate.  |
| frn_index_determination_date | The FRN index determination date of the security.  |
| frn_index_determination_rate | The FRN index determination rate of the security.  |
| high_discount_rate | The high discount rate of the security.  |
| high_investment_rate | The high investment rate of the security.  |
| high_price | The high price of the security at auction.  |
| high_discount_margin | The high discount margin of the security.  |
| high_yield | The high yield of the security at auction.  |
| index_ratio_on_issue_date | The index ratio on the issue date of the security.  |
| indirect_bidder_accepted | The accepted value from indirect bidders on the security.  |
| indirect_bidder_tendered | The tendered value from indirect bidders on the security.  |
| interest_payment_frequency | The interest payment frequency of the security.  |
| low_discount_rate | The low discount rate of the security.  |
| low_investment_rate | The low investment rate of the security.  |
| low_price | The low price of the security at auction.  |
| low_discount_margin | The low discount margin of the security.  |
| low_yield | The low yield of the security at auction.  |
| maturing_date | The maturing date of the security.  |
| max_competitive_award | The maximum competitive award at auction.  |
| max_non_competitive_award | The maximum non-competitive award at auction.  |
| max_single_bid | The maximum single bid at auction.  |
| min_bid_amount | The minimum bid amount at auction.  |
| min_strip_amount | The minimum strip amount at auction.  |
| min_to_issue | The minimum to issue at auction.  |
| multiples_to_bid | The multiples to bid at auction.  |
| multiples_to_issue | The multiples to issue at auction.  |
| nlp_exclusion_amount | The NLP exclusion amount at auction.  |
| nlp_reporting_threshold | The NLP reporting threshold at auction.  |
| non_competitive_accepted | The accepted value from non-competitive bidders on the security.  |
| non_competitive_tenders_accepted | Whether or not the auction accepted non-competitive tenders.  |
| offering_amount | The offering amount at auction.  |
| original_cusip | The original CUSIP of the security.  |
| original_dated_date | The original dated date of the security.  |
| original_issue_date | The original issue date of the security.  |
| original_security_term | The original term of the security.  |
| pdf_announcement | The PDF filename for the announcement of the security.  |
| pdf_competitive_results | The PDF filename for the competitive results of the security.  |
| pdf_non_competitive_results | The PDF filename for the non-competitive results of the security.  |
| pdf_special_announcement | The PDF filename for the special announcements.  |
| price_per_100 | The price per 100 of the security.  |
| primary_dealer_accepted | The primary dealer accepted value on the security.  |
| primary_dealer_tendered | The primary dealer tendered value on the security.  |
| reopening | Whether or not the auction was reopened.  |
| security_term_day_month | The security term in days or months.  |
| security_term_week_year | The security term in weeks or years.  |
| series | The series name of the security.  |
| soma_accepted | The SOMA accepted value on the security.  |
| soma_holdings | The SOMA holdings on the security.  |
| soma_included | Whether or not the SOMA (System Open Market Account) was included on the security.  |
| soma_tendered | The SOMA tendered value on the security.  |
| spread | The spread on the security.  |
| standard_payment_per_1000 | The standard payment per 1000 of the security.  |
| strippable | Whether or not the security is strippable.  |
| term | The term of the security.  |
| tiin_conversion_factor_per_1000 | The TIIN conversion factor per 1000 of the security.  |
| tips | Whether or not the security is TIPS.  |
| total_accepted | The total accepted value at auction.  |
| total_tendered | The total tendered value at auction.  |
| treasury_retail_accepted | The accepted value on the security from retail.  |
| treasury_retail_tenders_accepted | Whether or not the tender offers from retail are accepted  |
| type | The type of issuance.  This might be different than the security type.  |
| unadjusted_accrued_interest_per_1000 | The unadjusted accrued interest per 1000 of the security.  |
| unadjusted_price | The unadjusted price of the security.  |
| updated_timestamp | The updated timestamp of the security.  |
| xml_announcement | The XML filename for the announcement of the security.  |
| xml_competitive_results | The XML filename for the competitive results of the security.  |
| xml_special_announcement | The XML filename for special announcements.  |
| tint_cusip1 | Tint CUSIP 1.  |
| tint_cusip2 | Tint CUSIP 2.  |
