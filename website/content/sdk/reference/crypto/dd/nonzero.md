---
title: nonzero
description: Documentation page for OpenBB's nonzero function and nonzero_chart function.
  These functions are used to retrieve addresses with a non-zero balance of a certain
  symbol and plot them respectively.
keywords:
- nonzero function
- nonzero_chart function
- addresses with non-zero balance
- cryptocurrency
- dataframe
- BTC
- chart plotting
- export data
- due diligence
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.nonzero - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns addresses with non-zero balance of a certain symbol

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_model.py#L248)]

```python wordwrap
openbb.crypto.dd.nonzero(symbol: str, start_date: str = "2010-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search (e.g., BTC) | None | False |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | str | Final date, format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | addresses with non-zero balances |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots addresses with non-zero balance of a certain symbol

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_view.py#L83)]

```python wordwrap
openbb.crypto.dd.nonzero_chart(symbol: str, start_date: str = "2010-01-01", end_date: Optional[str] = None, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search (e.g., BTC) | None | False |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>