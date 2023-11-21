---
title: fr
description: Our docusaurus page provides Python functions that return and display
  crypto coin fundraising data. It deals with launch summary, sales rounds, treasury
  accounts and metric value launch details. The page also showcases how to export
  the data to different file formats.
keywords:
- Crypto coin fundraising data
- Python functions
- Launch Summary
- Sales rounds
- Treasury accounts
- Metric value launch details
- Export data
- Docusaurus page
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.fr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin fundraising

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L644)]

```python wordwrap
openbb.crypto.dd.fr(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check fundraising | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame] | Launch summary,<br/>Sales rounds,<br/>Treasury Accounts,<br/>Metric Value launch details |
---

## Examples

```python
from openbb_terminal.sdk import openbb
fundraise = openbb.crypto.dd.fr(symbol="BTC")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display coin fundraising

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L651)]

```python wordwrap
openbb.crypto.dd.fr_chart(symbol: str, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin fundraising | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>