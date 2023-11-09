---
title: website
description: This page provides documentation on how to fetch a company's website
  from yfinance using a stock ticker symbol.
keywords:
- yfinance
- website
- stock ticker symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.website - Reference | OpenBB SDK Docs" />

Gets website of company from yfinance

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L210)]

```python
openbb.stocks.fa.website(symbol: str)
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
| str | Company website |
---
