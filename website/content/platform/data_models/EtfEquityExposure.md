---
title: "Etf Equity Exposure"
description: "Get the exposure to ETFs for a specific stock"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EtfEquityExposure` | `EtfEquityExposureQueryParams` | `EtfEquityExposureData` |

### Import Statement

```python
from openbb_core.provider.standard_models.etf_equity_exposure import (
EtfEquityExposureData,
EtfEquityExposureQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (Stock) Multiple items allowed for provider(s): fmp. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (Stock) Multiple items allowed for provider(s): fmp. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| equity_symbol | str | The symbol of the equity requested. |
| etf_symbol | str | The symbol of the ETF with exposure to the requested equity. |
| shares | int | The number of shares held in the ETF. |
| weight | float | The weight of the equity in the ETF, as a normalized percent. |
| market_value | Union[int, float] | The market value of the equity position in the ETF. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| equity_symbol | str | The symbol of the equity requested. |
| etf_symbol | str | The symbol of the ETF with exposure to the requested equity. |
| shares | int | The number of shares held in the ETF. |
| weight | float | The weight of the equity in the ETF, as a normalized percent. |
| market_value | Union[int, float] | The market value of the equity position in the ETF. |
</TabItem>

</Tabs>

