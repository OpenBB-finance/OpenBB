---
title: lins
description: 'The webpage is a technical documentation section related to the usage
  of the functions ''lins'' and ''lins_chart''. It involves extracting and displaying
  last insider activity for a particular stock ticker from source: Finviz.'
keywords:
- technical documentation
- stock ticker
- insider activity
- Finviz
- OpenBB.finance
- functions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.lins - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get last insider activity for a given stock ticker. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/finviz_model.py#L16)]

```python
openbb.stocks.ins.lins(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Latest insider trading activity |
---

</TabItem>
<TabItem value="view" label="Chart">

Display insider activity for a given stock ticker. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/finviz_view.py#L15)]

```python
openbb.stocks.ins.lins_chart(symbol: str, limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of latest insider activity to display | 10 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
