---
title: gov
description: This page provides functions for retrieving and viewing data on cryptocurrency
  governance using OpenBB's Gov and Gov Chart functions. Check a crypto symbol's governance
  and view it in a table or chart format. Also includes option to export data.
keywords:
- cryptocurrency
- governance
- data analysis
- python functions
- gov function
- gov chart function
- crypto symbol
- data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.gov - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin governance

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L567)]

```python
openbb.crypto.dd.gov(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check governance | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[str, pd.DataFrame] | Governance summary,<br/>Metric Value with governance details |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing coin governance

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L602)]

```python
openbb.crypto.dd.gov_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin governance | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
