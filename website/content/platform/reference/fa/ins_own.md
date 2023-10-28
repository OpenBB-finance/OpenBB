---
title: ins_own
description: This page is about Institutional Ownership, which offers data related
  to the ownership shares in a company including various parameters like number of
  investors, number of shares, total invested amount and more. It also includes an
  API function call to retrieve this data.
keywords:
- institutional ownership
- investors holding
- number of shares
- total invested amount
- ownership percent
- put call ratio
- institutional ownership data
- API function call
- data retrieve
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.ins_own - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Institutional Ownership. Institutional ownership data.

```python wordwrap
ins_own(symbol: Union[str, List[str]], include_current_quarter: bool = False, date: date = None, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| include_current_quarter | bool | Include current quarter data. | False | True |
| date | date | A specific date to get data for. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[InstitutionalOwnership]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| symbol | str | Symbol to get data for. |
| cik | str | CIK of the company. |
| date | date | The date of the data. |
| investors_holding | int | Number of investors holding the stock. |
| last_investors_holding | int | Number of investors holding the stock in the last quarter. |
| investors_holding_change | int | Change in the number of investors holding the stock. |
| number_of_13f_shares | int | Number of 13F shares. |
| last_number_of_13f_shares | int | Number of 13F shares in the last quarter. |
| number_of_13f_shares_change | int | Change in the number of 13F shares. |
| total_invested | float | Total amount invested. |
| last_total_invested | float | Total amount invested in the last quarter. |
| total_invested_change | float | Change in the total amount invested. |
| ownership_percent | float | Ownership percent. |
| last_ownership_percent | float | Ownership percent in the last quarter. |
| ownership_percent_change | float | Change in the ownership percent. |
| new_positions | int | Number of new positions. |
| last_new_positions | int | Number of new positions in the last quarter. |
| new_positions_change | int | Change in the number of new positions. |
| increased_positions | int | Number of increased positions. |
| last_increased_positions | int | Number of increased positions in the last quarter. |
| increased_positions_change | int | Change in the number of increased positions. |
| closed_positions | int | Number of closed positions. |
| last_closed_positions | int | Number of closed positions in the last quarter. |
| closed_positions_change | int | Change in the number of closed positions. |
| reduced_positions | int | Number of reduced positions. |
| last_reduced_positions | int | Number of reduced positions in the last quarter. |
| reduced_positions_change | int | Change in the number of reduced positions. |
| total_calls | int | Total number of call options contracts traded for Apple Inc. on the specified date. |
| last_total_calls | int | Total number of call options contracts traded for Apple Inc. on the previous reporting date. |
| total_calls_change | int | Change in the total number of call options contracts traded between the current and previous reporting dates. |
| total_puts | int | Total number of put options contracts traded for Apple Inc. on the specified date. |
| last_total_puts | int | Total number of put options contracts traded for Apple Inc. on the previous reporting date. |
| total_puts_change | int | Change in the total number of put options contracts traded between the current and previous reporting dates. |
| put_call_ratio | float | Put-call ratio, which is the ratio of the total number of put options to call options traded on the specified date. |
| last_put_call_ratio | float | Put-call ratio on the previous reporting date. |
| put_call_ratio_change | float | Change in the put-call ratio between the current and previous reporting dates. |
</TabItem>

</Tabs>
