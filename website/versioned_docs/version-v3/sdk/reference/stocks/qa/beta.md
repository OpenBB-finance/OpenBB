---
title: beta
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# beta

<Tabs>
<TabItem value="model" label="Model" default>

Calculate beta for a ticker and a reference ticker.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/quantitative_analysis/beta_model.py#L11)]

```python
openbb.stocks.qa.beta(symbol: str, ref_symbol: str, data: pd.DataFrame = None, ref_data: pd.DataFrame = None, interval: int = 1440)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | A ticker to calculate beta for | None | False |
| ref_symbol | str | A reference ticker symbol for the beta calculation (default in terminal is SPY) | None | False |
| data | pd.DataFrame | The selected ticker symbols price data | None | True |
| ref_data | pd.DataFrame | The reference ticker symbols price data | None | True |
| interval | int | The interval of the ref_data. This will ONLY be used if ref_data is None | 1440 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.Series, pd.Series, float, float] | Stock ticker symbols close-to-close returns, Reference ticker symbols close-to-close returns, beta, alpha |
---



</TabItem>
<TabItem value="view" label="Chart">

Display the beta scatterplot + linear regression.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/quantitative_analysis/beta_view.py#L18)]

```python
openbb.stocks.qa.beta_chart(symbol: str, ref_symbol: str, data: pd.DataFrame = None, ref_data: pd.DataFrame = None, interval: int = 1440, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | A ticker to calculate beta for | None | False |
| ref_symbol | str | A reference ticker symbol for the beta calculation (default in terminal is SPY) | None | False |
| data | pd.DataFrame | The selected ticker symbols price data | None | True |
| ref_data | pd.DataFrame | The reference ticker symbols price data | None | True |
| interval | int | The interval of the ref_data. This will ONLY be used if ref_data is None | 1440 | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>