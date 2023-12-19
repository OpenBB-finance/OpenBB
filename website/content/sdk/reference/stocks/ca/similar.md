---
title: similar
description: Documentation for the 'similar' functionality in the OpenBB-finance package.
  Includes details about the function, parameters and returns, and examples.
keywords:
- OpenBB-finance
- similar tickers
- stock comparison
- stock analysis
- python package
- Finviz
- Polygon
- Finnhub
- TSNE
- stock symbols
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.similar - Reference | OpenBB SDK Docs" />

Find similar tickers to a given symbol.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/sdk_helpers.py#L15)]

```python
openbb.stocks.ca.similar(symbol: str, source: Any = "Finviz")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to find similar tickers to. | None | False |
| source | str | Source to get data for, by default "Finviz".  Can be "Finviz", "Polygon", "Finnhub", or "TSNE" | Finviz | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List[str] | List of similar tickers. |
---

## Examples


To get similar tickers to AAPL from Finviz:

```python
from openbb_terminal.sdk import openbb
similar_tickers = openbb.stocks.ca.similar("AAPL)
```


To use our custom TSNE model for similar tickers in the SP500:

```python
similar_tickers = openbb.stocks.ca.similar("AAPL", source="TSNE")
```

---
