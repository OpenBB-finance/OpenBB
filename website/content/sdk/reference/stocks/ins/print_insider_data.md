---
title: print_insider_data
description: Documentation page for OpenBB-finance's Print Insider Data feature. It
  includes details about the parameters involved, such as the type of insider data
  and the limit of data rows to display, as well as the option to export data in a
  specific format. The page provides source code links for further information.
keywords:
- Print insider data
- Open insider filtered data
- Type_insider
- Limit
- Export data format
- Docusaurus page metadata
- Source code
- OpenBB-finance
- Metadata SEO
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.print_insider_data - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Print insider data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/openinsider_model.py#L1437)]

```python
openbb.stocks.ins.print_insider_data(type_insider: str = "lcb", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| type_insider | str | Insider type of data. Available types can be accessed through get_insider_types(). | lcb | True |
| limit | int | Limit of data rows to display | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Open insider filtered data |
---

</TabItem>
<TabItem value="view" label="Chart">

Print insider data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/openinsider_view.py#L108)]

```python
openbb.stocks.ins.print_insider_data_chart(type_insider: str = "lcb", limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| type_insider | str | Insider type of data. Available types can be accessed through get_insider_types(). | lcb | True |
| limit | int | Limit of data rows to display | 10 | True |
| export | str | Export data format |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
