<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Upcoming and Historical IPO Calendar.

```excel wordwrap
=OBB.EQUITY.CALENDAR.IPO(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: intrinio | true |
| symbol | string | Symbol to get data for. | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| limit | number | The number of data entries to return. | true |
| status | string | Status of the IPO. [upcoming, priced, or withdrawn] (provider: intrinio) | true |
| offer_amount_greater_than | number | Return IPOs with an offer dollar amount greater than the given amount. (provider: intrinio) | true |
| offer_amount_less_than | number | Return IPOs with an offer dollar amount less than the given amount. (provider: intrinio) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| ipo_date | The date of the IPO, when the stock first trades on a major exchange.  |
| status | 
            The status of the IPO. Upcoming IPOs have not taken place yet but are expected to.
            Priced IPOs have taken place.
            Withdrawn IPOs were expected to take place, but were subsequently withdrawn and did not take place
         (provider: intrinio) |
| exchange | 
            The acronym of the stock exchange that the company is going to trade publicly on.
            Typically NYSE or NASDAQ.
         (provider: intrinio) |
| offer_amount | The total dollar amount of shares offered in the IPO. Typically this is share price * share count (provider: intrinio) |
| share_price | The price per share at which the IPO was offered. (provider: intrinio) |
| share_price_lowest | 
            The expected lowest price per share at which the IPO will be offered.
            Before an IPO is priced, companies typically provide a range of prices per share at which
            they expect to offer the IPO (typically available for upcoming IPOs).
         (provider: intrinio) |
| share_price_highest | 
            The expected highest price per share at which the IPO will be offered.
            Before an IPO is priced, companies typically provide a range of prices per share at which
            they expect to offer the IPO (typically available for upcoming IPOs).
         (provider: intrinio) |
| share_count | The number of shares offered in the IPO. (provider: intrinio) |
| share_count_lowest | 
            The expected lowest number of shares that will be offered in the IPO. Before an IPO is priced,
            companies typically provide a range of shares that they expect to offer in the IPO
            (typically available for upcoming IPOs).
         (provider: intrinio) |
| share_count_highest | 
            The expected highest number of shares that will be offered in the IPO. Before an IPO is priced,
            companies typically provide a range of shares that they expect to offer in the IPO
            (typically available for upcoming IPOs).
         (provider: intrinio) |
| announcement_url | The URL to the company's announcement of the IPO (provider: intrinio) |
| sec_report_url | 
            The URL to the company's S-1, S-1/A, F-1, or F-1/A SEC filing,
            which is required to be filed before an IPO takes place.
         (provider: intrinio) |
| open_price | The opening price at the beginning of the first trading day (only available for priced IPOs). (provider: intrinio) |
| close_price | The closing price at the end of the first trading day (only available for priced IPOs). (provider: intrinio) |
| volume | The volume at the end of the first trading day (only available for priced IPOs). (provider: intrinio) |
| day_change | 
            The percentage change between the open price and the close price on the first trading day
            (only available for priced IPOs).
         (provider: intrinio) |
| week_change | 
            The percentage change between the open price on the first trading day and the close price approximately
            a week after the first trading day (only available for priced IPOs).
         (provider: intrinio) |
| month_change | 
            The percentage change between the open price on the first trading day and the close price approximately
            a month after the first trading day (only available for priced IPOs).
         (provider: intrinio) |
| id | The Intrinio ID of the IPO. (provider: intrinio) |
| company | The company that is going public via the IPO. (provider: intrinio) |
| security | The primary Security for the Company that is going public via the IPO (provider: intrinio) |
