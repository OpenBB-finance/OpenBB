---
title: hq
description: This documentation page provides source code for retrieving the Google
  Map URL of a company's headquarters based on its stock ticker symbol, using the
  OpenBB's function openbb.stocks.fa.hq. It includes the parameter details and return
  type description.
keywords:
- hq
- google map url
- headquarter
- stock
- ticker symbol
- openbb.stocks.fa.hq
- fundamental analysis
- yahoo finance model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.hq - Reference | OpenBB SDK Docs" />

Gets google map url for headquarter

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L228)]

```python
openbb.stocks.fa.hq(symbol: str)
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
| str | Headquarter google maps url |
---
