---
title: "snapshots"
description: "Snapshots of currency exchange rates from an indirect or direct perspective of a base currency"
keywords:
- currency
- snapshots
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="currency/snapshots - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Snapshots of currency exchange rates from an indirect or direct perspective of a base currency.


Examples
--------

```python
from openbb import obb
obb.currency.snapshots(provider='fmp')
# Get exchange rates from USD and XAU to EUR, JPY, and GBP using 'fmp' as provider.
obb.currency.snapshots(provider='fmp', base='USD,XAU', counter_currencies='EUR,JPY,GBP', quote_type='indirect')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| base | Union[str, List[str]] | The base currency symbol. Multiple items allowed for provider(s): fmp. | usd | True |
| quote_type | Literal['direct', 'indirect'] | Whether the quote is direct or indirect. Selecting 'direct' will return the exchange rate as the amount of domestic currency required to buy one unit of the foreign currency. Selecting 'indirect' (default) will return the exchange rate as the amount of foreign currency required to buy one unit of the domestic currency. | indirect | True |
| counter_currencies | Union[str, List[str]] | An optional list of counter currency symbols to filter for. None returns all. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| base | Union[str, List[str]] | The base currency symbol. Multiple items allowed for provider(s): fmp. | usd | True |
| quote_type | Literal['direct', 'indirect'] | Whether the quote is direct or indirect. Selecting 'direct' will return the exchange rate as the amount of domestic currency required to buy one unit of the foreign currency. Selecting 'indirect' (default) will return the exchange rate as the amount of foreign currency required to buy one unit of the domestic currency. | indirect | True |
| counter_currencies | Union[str, List[str]] | An optional list of counter currency symbols to filter for. None returns all. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CurrencySnapshots
        Serializable results.
    provider : Literal['fmp']
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
| base_currency | str | The base, or domestic, currency. |
| counter_currency | str | The counter, or foreign, currency. |
| last_rate | float | The exchange rate, relative to the base currency. Rates are expressed as the amount of foreign currency received from selling one unit of the base currency, or the quantity of foreign currency required to purchase one unit of the domestic currency. To inverse the perspective, set the 'quote_type' parameter as 'direct'. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| base_currency | str | The base, or domestic, currency. |
| counter_currency | str | The counter, or foreign, currency. |
| last_rate | float | The exchange rate, relative to the base currency. Rates are expressed as the amount of foreign currency received from selling one unit of the base currency, or the quantity of foreign currency required to purchase one unit of the domestic currency. To inverse the perspective, set the 'quote_type' parameter as 'direct'. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | The change in the price from the previous close. |
| change_percent | float | The change in the price from the previous close, as a normalized percent. |
| ma50 | float | The 50-day moving average. |
| ma200 | float | The 200-day moving average. |
| year_high | float | The 52-week high. |
| year_low | float | The 52-week low. |
| last_rate_timestamp | datetime | The timestamp of the last rate. |
</TabItem>

</Tabs>

