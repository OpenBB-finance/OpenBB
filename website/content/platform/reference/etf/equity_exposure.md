---
title: "equity_exposure"
description: "Get the exposure to ETFs for a specific stock"
keywords:
- etf
- equity_exposure
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/equity_exposure - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the exposure to ETFs for a specific stock.


Examples
--------

```python
from openbb import obb
obb.etf.equity_exposure(symbol='MSFT', provider='fmp')
# This function accepts multiple tickers.
obb.etf.equity_exposure(symbol='MSFT,AAPL', provider='fmp')
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

## Returns

```python wordwrap
OBBject
    results : EtfEquityExposure
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

