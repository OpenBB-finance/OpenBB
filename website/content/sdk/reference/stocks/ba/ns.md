---
title: ns
description: Getting Onclusive Data
keywords:
- stocks
- ba
- ns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.ns - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Getting Onclusive Data. [Source: Invisage Platform]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/behavioural_analysis/news_sentiment_model.py#L11)]

```python wordwrap
openbb.stocks.ba.ns(ticker: str = "", start_date: str = "", end_date: str = "", date: str = "", limit: int = 100, offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker | str | Stock ticker |  | True |
| start_date | str | Records are coming from this day (Start date in YYYY-MM-DD format) |  | True |
| end_date | str | Records will get upto this day (End date in YYYY-MM-DD format) |  | True |
| date | str | Show that the records on this day (date in YYYY-MM-DD format) |  | True |
| limit | int | The number of records to get | 100 | True |
| offset | int | The number of records to offset | 0 | True |


---

## Returns

This function does not return anything

---



</TabItem>
<TabItem value="view" label="Chart">

Display Onclusive Data. [Source: Invisage Plotform]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/behavioural_analysis/news_sentiment_view.py#L13)]

```python wordwrap
openbb.stocks.ba.ns_chart(ticker: str = "", start_date: str = "", end_date: str = "", date: str = "", limit: int = 100, offset: int = 0, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker | str | Stock ticker |  | True |
| start_date | str | Records are coming from this day (Start date in YYYY-MM-DD format) |  | True |
| end_date | str | Records will get upto this day (End date in YYYY-MM-DD format) |  | True |
| date | str | Show that the records on this day (date in YYYY-MM-DD format) |  | True |
| limit | int | The number of records to get | 100 | True |
| offset | int | The number of records to offset | 0 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>