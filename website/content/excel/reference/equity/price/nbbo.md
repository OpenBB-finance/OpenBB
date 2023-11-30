<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Equity NBBO. Load National Best Bid and Offer for a specific equity.

```excel wordwrap
=OBB.EQUITY.PRICE.NBBO(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: polygon | true |
| limit | number | The number of data entries to return. Up to ten million records will be returned. Pagination occurs in groups of 50,000. Remaining limit values will always return 50,000 more records unless it is the last page. High volume tickers will require multiple max requests for a single day's NBBO records. Expect stocks, like SPY, to approach 1GB in size, per day, as a raw CSV. Splitting large requests into chunks is recommended for full-day requests of high-volume symbols. (provider: polygon) | true |
| timestamp | string | A specific date to get data for. Use bracketed the timestamp parameters to specify exact time ranges. (provider: polygon) | true |
| timestamp_lt | string | Query by datetime, less than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
(provider: polygon) | true |
| timestamp_gt | string | Query by datetime, greater than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
(provider: polygon) | true |
| timestamp_lte | string | Query by datetime, less than or equal to.
Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
(provider: polygon) | true |
| timestamp_gte | string | Query by datetime, greater than or equal to.
Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
(provider: polygon) | true |

## Data

| Name | Description |
| ---- | ----------- |
| ask_exchange | The exchange ID for the ask.  |
| ask | The last ask price.  |
| ask_size | 
        The ask size. This represents the number of round lot orders at the given ask price.
        The normal round lot size is 100 shares.
        An ask size of 2 means there are 200 shares available to purchase at the given ask price.
          |
| bid_size | The bid size in round lots.  |
| bid | The last bid price.  |
| bid_exchange | The exchange ID for the bid.  |
| tape | The exchange tape. (provider: polygon) |
| conditions | A list of condition codes. (provider: polygon) |
| indicators | A list of indicator codes. (provider: polygon) |
| sequence_num | 
            The sequence number represents the sequence in which message events happened.
            These are increasing and unique per ticker symbol, but will not always be sequential
            (e.g., 1, 2, 6, 9, 10, 11)
         (provider: polygon) |
| participant_timestamp | 
            The nanosecond accuracy Participant/Exchange Unix Timestamp.
            This is the timestamp of when the quote was actually generated at the exchange.
         (provider: polygon) |
| sip_timestamp | 
            The nanosecond accuracy SIP Unix Timestamp.
            This is the timestamp of when the SIP received this quote from the exchange which produced it.
         (provider: polygon) |
| trf_timestamp | 
            The nanosecond accuracy TRF (Trade Reporting Facility) Unix Timestamp.
            This is the timestamp of when the trade reporting facility received this quote.
         (provider: polygon) |
