---
title: earnings
description: This site provides an extensive guide to retrieving earnings data of
  any stock ticker using the OpenBB Terminal. The page includes detailed parameters
  descriptions and practical examples.
keywords:
- earnings data
- stock ticker
- AlphaVantage
- YahooFinance
- quarterly data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.earnings - Reference | OpenBB SDK Docs" />

Get earnings data.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/sdk_helpers.py#L203)]

```python
openbb.stocks.fa.earnings(symbol: str, source: str = "YahooFinance", quarterly: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| source | str | Source to use, by default "AlphaVantage" | YahooFinance | True |
| quarterly | bool | Flag to get quarterly data (AlphaVantage only), by default False. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of earnings |
---

## Examples

```python
from openbb_terminal.sdk import openbb
aapl_earnings = openbb.stocks.fa.earnings("AAPL", source ="YahooFinance)
```

```
To obtain quarterly earnings, use the quarterly flag with AlphaVantage
```
```python
aapl_earnings = openbb.stocks.fa.metrics("earnings", source ="AlphaVantage, quarterly=True)
```

---
