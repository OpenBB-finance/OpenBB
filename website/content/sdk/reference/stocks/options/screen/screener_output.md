---
title: screener_output
description: This documentation page cover the usage of screener output for OpenBB
  Terminal. It includes explanations for using preset filters, printing the output,
  and parameters for sorting and export formatting. There are also links to the source
  code and Python command line instructions.
keywords:
- screener output
- preset filters
- export formatting
- command line instructions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.screen.screener_output - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Screen options based on preset filters

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_model.py#L159)]

```python
openbb.stocks.options.screen.screener_output(preset: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Chosen preset | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, str] | DataFrame with screener data or empty if errors, String containing error message if supplied |
---

</TabItem>
<TabItem value="view" label="Chart">

Print the output of screener

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/screen/syncretism_view.py#L60)]

```python
openbb.stocks.options.screen.screener_output_chart(preset: str, limit: int = 20, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset | str | Chosen preset | None | False |
| limit | int | Number of randomly sorted rows to display | 20 | True |
| export | str | Format for export file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List | List of tickers screened |
---

</TabItem>
</Tabs>
