---
title: ewf
description: The documentation page discusses two functions - openbb.crypto.ov.ewf
  and openbb.crypto.ov.ewf_chart. The first function scrapes exchange withdrawal fees
  and returns a DataFrame with details on Exchange, Coins, and various statistics.
  The second function allows users to export this data into different formats. The
  source code and use cases of both functions are included.
keywords:
- openbb.crypto.ov.ewf
- Exchange withdrawal fees
- Scrapes exchange withdrawal fees
- openbb.crypto.ov.ewf_chart
- Model
- Chart
- Source Code
- Export dataframe data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.ewf - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Scrapes exchange withdrawal fees

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py#L182)]

```python
openbb.crypto.ov.ewf()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Exchange, Coins, Lowest, Average, Median, Highest |
---

</TabItem>
<TabItem value="view" label="Chart">

Exchange withdrawal fees

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py#L53)]

```python
openbb.crypto.ov.ewf_chart(export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
