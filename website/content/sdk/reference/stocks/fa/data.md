---
title: data
description: Detailed instruction on how to get fundamental data from finviz using
  'openbb' Python package. It explains the usage of 'stocks.fa.data' function, its
  parameters and return type along with an example.
keywords:
- fundamental data
- finviz
- stock ticker symbol
- dataframe
- openbb_terminal
- sdk
- IWV
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.data - Reference | OpenBB SDK Docs" />

Get fundamental data from finviz

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finviz_model.py#L15)]

```python
openbb.stocks.fa.data(symbol: str)
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
| pd.DataFrame | DataFrame of fundamental data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.fa.data("IWV")
```

---
