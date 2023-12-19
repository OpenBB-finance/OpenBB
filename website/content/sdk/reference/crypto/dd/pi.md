---
title: pi
description: Details about the PI function used in OpenBB crypto due diligence. It
  covers aspects like fetching coin product info and presenting it as tables and charts.
  Also, includes links to the source code.
keywords:
- Cryptocurrency
- Due Diligence
- pi Function
- Project Info
- Tables
- Charts
- Docusaurus
- Metadata
- Source Code
- Github
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.pi - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin product info

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L353)]

```python
openbb.crypto.dd.pi(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check product info | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] | Metric, Value with project and technology details,<br/>Coin public repos,<br/>Coin audits,<br/>Coin known exploits/vulns |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing project info

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L470)]

```python
openbb.crypto.dd.pi_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check project info | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
