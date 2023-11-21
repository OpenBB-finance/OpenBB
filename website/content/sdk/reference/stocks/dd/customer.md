---
title: customer
description: Documentation for the 'customer' function in the OpenBB Terminal. This
  function allows you to print customers from a ticker, helping in stock analysis
  and due diligence. Here, you'll find details about parameters, return values, and
  the source code.
keywords:
- customer
- stocks
- due diligence
- dataframe
- symbol
- limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.customer - Reference | OpenBB SDK Docs" />

Print customers from ticker provided

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/csimarket_model.py#L66)]

```python
openbb.stocks.dd.customer(symbol: str, limit: int = 50)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to select customers from | None | False |
| limit | int | The maximum number of rows to show | 50 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe of suppliers |
---
