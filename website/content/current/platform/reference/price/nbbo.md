---
title: nbbo
description: Learn how to load the National Best Bid and Offer (NBBO) for a specific
  equity using the OBB.equity.price.nbbo API. Explore the parameters and data returned
  by the query, including ask price, bid price, ask size, bid size, exchange details,
  timestamps, and more.
keywords:
- Equity Quote
- National Best Bid and Offer
- specific equity
- symbol
- provider
- polygon
- query
- limit
- date
- timestamp
- OBBject
- results
- EquityNBBO
- warnings
- Chart
- Metadata
- ask_exchange
- ask
- ask_size
- bid_size
- bid
- bid_exchange
- tape
- conditions
- indicators
- sequence_num
- participant_timestamp
- sip_timestamp
- trf_timestamp
- data
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Equity Quote. Load National Best Bid and Offer for a specific equity.

```python wordwrap
obb.equity.price.nbbo(symbol: Union[str, List[str]], provider: Literal[str] = polygon)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'polygon' if there is no default. | polygon | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'polygon' if there is no default. | polygon | True |
| limit | int | The number of data entries to return. Up to ten million records will be returned. Pagination occurs in groups of 50,000. Remaining limit values will always return 50,000 more records unless it is the last page. High volume tickers will require multiple max requests for a single day's NBBO records. Expect stocks, like SPY, to approach 1GB in size, per day, as a raw CSV. Splitting large requests into chunks is recommended for full-day requests of high-volume symbols. | 50000 | True |
| date | date | A specific date to get data for. Use bracketed the timestamp parameters to specify exact time ranges. | None | True |
| timestamp_lt | Union[datetime, str] | 
            Query by datetime, less than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
         | None | True |
| timestamp_gt | Union[datetime, str] | 
            Query by datetime, greater than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
         | None | True |
| timestamp_lte | Union[datetime, str] | 
            Query by datetime, less than or equal to.
            Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
         | None | True |
| timestamp_gte | Union[datetime, str] | 
            Query by datetime, greater than or equal to.
            Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
         | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquityNBBO]
        Serializable results.

    provider : Optional[Literal['polygon']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| ask_exchange | str | The exchange ID for the ask. |
| ask | float | The last ask price. |
| ask_size | int | 
        The ask size. This represents the number of round lot orders at the given ask price.
        The normal round lot size is 100 shares.
        An ask size of 2 means there are 200 shares available to purchase at the given ask price.
         |
| bid_size | int | The bid size in round lots. |
| bid | float | The last bid price. |
| bid_exchange | str | The exchange ID for the bid. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ask_exchange | str | The exchange ID for the ask. |
| ask | float | The last ask price. |
| ask_size | int | 
        The ask size. This represents the number of round lot orders at the given ask price.
        The normal round lot size is 100 shares.
        An ask size of 2 means there are 200 shares available to purchase at the given ask price.
         |
| bid_size | int | The bid size in round lots. |
| bid | float | The last bid price. |
| bid_exchange | str | The exchange ID for the bid. |
| tape | str | The exchange tape. |
| conditions | Union[str, List[int], List[str]] | A list of condition codes. |
| indicators | List | A list of indicator codes. |
| sequence_num | int | 
            The sequence number represents the sequence in which message events happened.
            These are increasing and unique per ticker symbol, but will not always be sequential
            (e.g., 1, 2, 6, 9, 10, 11)
         |
| participant_timestamp | datetime | 
            The nanosecond accuracy Participant/Exchange Unix Timestamp.
            This is the timestamp of when the quote was actually generated at the exchange.
         |
| sip_timestamp | datetime | 
            The nanosecond accuracy SIP Unix Timestamp.
            This is the timestamp of when the SIP received this quote from the exchange which produced it.
         |
| trf_timestamp | datetime | 
            The nanosecond accuracy TRF (Trade Reporting Facility) Unix Timestamp.
            This is the timestamp of when the trade reporting facility received this quote.
         |
</TabItem>

</Tabs>

