---
title: "Currency Reference Rates"
description: "Current, official, currency reference rates"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CurrencyReferenceRates` | `CurrencyReferenceRatesQueryParams` | `CurrencyReferenceRatesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.currency_reference_rates import (
CurrencyReferenceRatesData,
CurrencyReferenceRatesQueryParams,
)
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

