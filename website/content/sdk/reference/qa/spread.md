---
title: spread
description: 'The page provides information about two central functions of the OpenBBTerminal:
  ''spread'' and ''spread_chart''. These Python functions are part of the quantitative
  analysis, analyzing standard deviation, variance and create spread charts. The descriptions
  include source code, parameters, and return values.'
keywords:
- Standard Deviation
- Variance
- Quantitative Analysis
- Rolling model
- Spread
- Spread chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.spread - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Standard Deviation and Variance

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L41)]

```python wordwrap
openbb.qa.spread(data: pd.DataFrame, window: int = 14)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of targeted data | None | False |
| window | int | Length of window | 14 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Dataframe of rolling standard deviation,<br/>Dataframe of rolling variance |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots rolling spread

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L126)]

```python wordwrap
openbb.qa.spread_chart(data: pd.DataFrame, target: str, symbol: str = "", window: int = 14, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
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