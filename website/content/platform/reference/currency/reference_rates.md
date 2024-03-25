---
title: "reference_rates"
description: "Current, official, currency reference rates"
keywords:
- currency
- reference_rates
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="currency/reference_rates - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Current, official, currency reference rates.

Foreign exchange reference rates are the exchange rates set by a major financial institution or regulatory body,
serving as a benchmark for the value of currencies around the world.
These rates are used as a standard to facilitate international trade and financial transactions,
ensuring consistency and reliability in currency conversion.
They are typically updated on a daily basis and reflect the market conditions at a specific time.
Central banks and financial institutions often use these rates to guide their own exchange rates,
impacting global trade, loans, and investments.


Examples
--------

```python
from openbb import obb
obb.currency.reference_rates(provider='ecb')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CurrencyReferenceRates
        Serializable results.
    provider : Literal['ecb']
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
| date | date | The date of the data. |
| EUR | float | Euro. |
| USD | float | US Dollar. |
| JPY | float | Japanese Yen. |
| BGN | float | Bulgarian Lev. |
| CZK | float | Czech Koruna. |
| DKK | float | Danish Krone. |
| GBP | float | Pound Sterling. |
| HUF | float | Hungarian Forint. |
| PLN | float | Polish Zloty. |
| RON | float | Romanian Leu. |
| SEK | float | Swedish Krona. |
| CHF | float | Swiss Franc. |
| ISK | float | Icelandic Krona. |
| NOK | float | Norwegian Krone. |
| TRY | float | Turkish Lira. |
| AUD | float | Australian Dollar. |
| BRL | float | Brazilian Real. |
| CAD | float | Canadian Dollar. |
| CNY | float | Chinese Yuan. |
| HKD | float | Hong Kong Dollar. |
| IDR | float | Indonesian Rupiah. |
| ILS | float | Israeli Shekel. |
| INR | float | Indian Rupee. |
| KRW | float | South Korean Won. |
| MXN | float | Mexican Peso. |
| MYR | float | Malaysian Ringgit. |
| NZD | float | New Zealand Dollar. |
| PHP | float | Philippine Peso. |
| SGD | float | Singapore Dollar. |
| THB | float | Thai Baht. |
| ZAR | float | South African Rand. |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| EUR | float | Euro. |
| USD | float | US Dollar. |
| JPY | float | Japanese Yen. |
| BGN | float | Bulgarian Lev. |
| CZK | float | Czech Koruna. |
| DKK | float | Danish Krone. |
| GBP | float | Pound Sterling. |
| HUF | float | Hungarian Forint. |
| PLN | float | Polish Zloty. |
| RON | float | Romanian Leu. |
| SEK | float | Swedish Krona. |
| CHF | float | Swiss Franc. |
| ISK | float | Icelandic Krona. |
| NOK | float | Norwegian Krone. |
| TRY | float | Turkish Lira. |
| AUD | float | Australian Dollar. |
| BRL | float | Brazilian Real. |
| CAD | float | Canadian Dollar. |
| CNY | float | Chinese Yuan. |
| HKD | float | Hong Kong Dollar. |
| IDR | float | Indonesian Rupiah. |
| ILS | float | Israeli Shekel. |
| INR | float | Indian Rupee. |
| KRW | float | South Korean Won. |
| MXN | float | Mexican Peso. |
| MYR | float | Malaysian Ringgit. |
| NZD | float | New Zealand Dollar. |
| PHP | float | Philippine Peso. |
| SGD | float | Singapore Dollar. |
| THB | float | Thai Baht. |
| ZAR | float | South African Rand. |
</TabItem>

</Tabs>

