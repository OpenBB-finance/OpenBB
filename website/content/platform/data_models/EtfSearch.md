---
title: Search for ETFs
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EtfSearch` | `EtfSearchQueryParams` | `EtfSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models.etf_search import (
EtfSearchData,
EtfSearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| exchange | Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT'] | The exchange code the ETF trades on. | None | True |
| is_active | Literal[True, False] | Whether the ETF is actively trading. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data.(ETF) |
| name | str | Name of the ETF. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data.(ETF) |
| name | str | Name of the ETF. |
| market_cap | float | The market cap of the ETF. |
| sector | str | The sector of the ETF. |
| industry | str | The industry of the ETF. |
| beta | float | The beta of the ETF. |
| price | float | The current price of the ETF. |
| last_annual_dividend | float | The last annual dividend paid. |
| volume | float | The current trading volume of the ETF. |
| exchange | str | The exchange code the ETF trades on. |
| exchange_name | str | The full name of the exchange the ETF trades on. |
| country | str | The country the ETF is registered in. |
| actively_trading | Literal[True, False] | Whether the ETF is actively trading. |
</TabItem>

</Tabs>
