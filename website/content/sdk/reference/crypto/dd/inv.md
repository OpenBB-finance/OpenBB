---
title: inv
description: Our inv function provides an overview of coin investors. It provides
  a comprehensive list of individual and organizational investors for a specific cryptocurrency.
  Additionally, our inv chart function prints a table of these coin investors and
  offers the option of exporting this data to various file formats.
keywords:
- coin investors
- cryptocurrency
- investors
- docusaurus page SEO
- functions
- crypto symbols
- data export
- csv
- json
- xlsx
- due diligence
- messari model
- messari view
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.inv - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin investors

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L494)]

```python
openbb.crypto.dd.inv(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check investors | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Individuals,<br/>Organizations |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing coin investors

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L510)]

```python
openbb.crypto.dd.inv_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin investors | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
