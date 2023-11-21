---
title: historical
description: Get historical fund, category, index price
keywords:
- funds
- historical
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds.historical - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical fund, category, index price

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_model.py#L12)]

```python wordwrap
openbb.funds.historical(loaded_funds: mstarpy.funds.Funds, start_date: str, end_date: str, comparison: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_funds | mstarpy.Funds | class mstarpy.Funds instantiated with selected funds | None | False |
| start_date | str | start date of the historical data | None | False |
| end_date | str | end date of the historical data | None | False |
| comparison | str | can be index, category, both |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing historical data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
openbb.funds.historical(f, "2020-01-01", "2020-12-31")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display historical fund, category, index price

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/mstarpy_view.py#L54)]

```python wordwrap
openbb.funds.historical_chart(loaded_funds: mstarpy.funds.Funds, start_date: str, end_date: str, comparison: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_funds | mstarpy.funds | class mstarpy.Funds instantiated with selected funds | None | False |
| start_date | str | start date of the period to be displayed | None | False |
| end_date | str | end date of the period to be displayed | None | False |
| comparison | str | type of comparison, can be index, category, both |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
f = openbb.funds.load("Vanguard", "US")
openbb.funds.historical_chart(f)
```

---



</TabItem>
</Tabs>