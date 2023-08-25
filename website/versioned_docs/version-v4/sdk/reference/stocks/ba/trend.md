---
title: trend
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# trend

<Tabs>
<TabItem value="model" label="Model" default>

Get sentiment data on the most talked about tickers

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/sentimentinvestor_model.py#L136)]

```python
openbb.stocks.ba.trend(start_date: Optional[str] = None, hour: int = 0, number: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Optional[str] | Initial date, format YYYY-MM-DD | None | True |
| hour | int | Hour of the day in 24-hour notation (e.g. 14) | 0 | True |
| number | int | Number of results returned by API call<br/>Maximum 250 per api call | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of trending data |
---



</TabItem>
<TabItem value="view" label="Chart">

Display most talked about tickers within

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/sentimentinvestor_view.py#L151)]

```python
openbb.stocks.ba.trend_chart(start_date: Optional[str] = None, hour: int = 0, number: int = 10, limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Optional[str] | Initial date, format YYYY-MM-DD | None | True |
| hour | int | Hour of the day in 24-hour notation (e.g. 14) | 0 | True |
| number | int | Number of results returned by API call<br/>Maximum 250 per api call | 10 | True |
| limit | int | Number of results display on the terminal<br/>Default: 10 | 10 | True |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>