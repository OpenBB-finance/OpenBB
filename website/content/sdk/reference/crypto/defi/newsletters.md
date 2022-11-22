---
title: newsletters
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# newsletters

<Tabs>
<TabItem value="model" label="Model" default>

Scrape all substack newsletters from url list.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/substack_model.py#L54)]

```python
openbb.crypto.defi.newsletters()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with recent news from most popular DeFi related newsletters. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing DeFi related substack newsletters.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/substack_view.py#L16)]

```python
openbb.crypto.defi.newsletters_chart(limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 10 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>