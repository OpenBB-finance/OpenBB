---
title: fees
description: Show cryptos with most fees
keywords:
- crypto
- disc
- fees
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.fees - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Show cryptos with most fees. [Source: CryptoStats]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/cryptostats_model.py#L20)]

```python wordwrap
openbb.crypto.disc.fees(marketcap: bool, tvl: bool, date: Any)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| marketcap | bool | Whether to show marketcap or not | None | False |
| tvl | bool | Whether to show tvl or not | None | False |
| date | datetime | Date to get data from (YYYY-MM-DD) | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Top coins with most fees |
---



</TabItem>
<TabItem value="view" label="Chart">

Display crypto with most fees paid [Source: CryptoStats]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/cryptostats_view.py#L17)]

```python wordwrap
openbb.crypto.disc.fees_chart(marketcap: bool, tvl: bool, date: str, limit: int = 15, sortby: str = "", ascend: bool = True, sheet_name: Optional[str] = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| marketcap | bool | Flag to include marketcap | None | False |
| date | str | Date to get data from (YYYY-MM-DD) | None | False |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key to sort data. |  | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>