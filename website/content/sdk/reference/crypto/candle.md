---
title: candle
description: The page provides documentation for the 'candle' function in the OpenBB
  crypto module. It describes how a candle chart can be plotted from a provided DataFrame,
  and the various parameters that can be adjusted.
keywords:
- crypto.candle
- candle chart
- Binance source
- Python script
- data visualization
- OpenBB crypto module
- matplotlib
- OHLCV
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.candle - Reference | OpenBB SDK Docs" />

Plot candle chart from dataframe. [Source: Binance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L834)]

```python wordwrap
openbb.crypto.candle(symbol: str, data: Optional[pd.DataFrame] = None, start_date: Union[datetime.datetime, str, NoneType] = None, end_date: Union[datetime.datetime, str, NoneType] = None, interval: Union[str, int] = "1440", exchange: str = "binance", to_symbol: str = "usdt", source: str = "CCXT", volume: bool = True, title: str = "", external_axes: bool = False, yscale: str = "linear", raw: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker name | None | False |
| data | pd.DataFrame | Dataframe containing time and OHLCV | None | True |
| start_date | Union[datetime, Union[str, None]] | Start date for data | None | True |
| end_date | Union[datetime, Union[str, None]] | End date for data | None | True |
| interval | Union[str, int] | Interval for data | 1440 | True |
| exchange | str | Exchange to use | binance | True |
| to_symbol | str | Currency to use | usdt | True |
| source | str | Source to use | CCXT | True |
| volume | bool | If volume data shall be plotted, by default True | True | True |
| ylabel | str | Y-label of the graph, by default "" | None | True |
| title | str | Title of graph, by default "" |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |
| yscale | str | Scaling for y axis.  Either linear or log | linear | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.crypto.candle(symbol="eth")
openbb.crypto.candle(symbol="btc", raw=True)
```

---

