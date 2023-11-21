---
title: rolling
description: A documentation page explaining the functionality of the OpenBB rolling
  model and rolling chart. These tools deal with computing and plotting rolling means
  and standard deviations in financial data, mapped by stock symbols or tickers. The
  methods are implemented in Python and operate on dataframes.
keywords:
- rolling
- quantitative analysis
- dataframe
- standard deviation
- mean
- Stock ticker
- window
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.rolling - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Return rolling mean and standard deviation

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L16)]

```python wordwrap
openbb.qa.rolling(data: pd.DataFrame, window: int = 14)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of target data | None | False |
| window | int | Length of rolling window | 14 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Dataframe of rolling mean,<br/>Dataframe of rolling standard deviation |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots mean std deviation

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L19)]

```python wordwrap
openbb.qa.rolling_chart(data: pd.DataFrame, target: str, symbol: str = "", window: int = 14, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker |  | True |
| window | int | Length of window | 14 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>