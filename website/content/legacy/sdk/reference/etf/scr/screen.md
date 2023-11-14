---
title: screen
description: 'This page of the documentation is dedicated to the OpenBB''s etf screener;
  it provides an overview of the functionality, parameters, and return types for two
  core methods: the ETF ''screen'' and ''screen_chart'' functions. The website guides
  the users through the use of these functions as well as their source code, helping
  them better understand and utilize the ETF screener.'
keywords:
- ETF screening
- Source code
- ETF scraping
- Data sorting
- Data visualization
- Financial data analysis
- Data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.scr.screen - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/screener/screener_model.py#L43)]

```python
openbb.etf.scr.screen(preset: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Screener to use from presets | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Screened dataframe |
---

</TabItem>
<TabItem value="view" label="Chart">

Display screener output

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/screener/screener_view.py#L18)]

```python
openbb.etf.scr.screen_chart(preset: str, num_to_show: int, sortby: str, ascend: bool, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Preset to use | None | False |
| num_to_show | int | Number of etfs to show | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Ascend when sorted | None | False |
| export | str | Output format of export |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
