---
title: get_strategies
description: Gets options strategies for all, or a list of, DTE(s)
keywords:
- stocks
- options
- get_strategies
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.get_strategies - Reference | OpenBB SDK Docs" />

Gets options strategies for all, or a list of, DTE(s).

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_chains_model.py#L1404)]

```python wordwrap
openbb.stocks.options.get_strategies(options: openbb_terminal.stocks.options.op_helpers.Options, days: Optional[list[int]] = None, straddle_strike: Optional[float] = 0, strangle_moneyness: Optional[list[float]] = None, synthetic_longs: Optional[list[float]] = None, synthetic_shorts: Optional[list[float]] = None, vertical_calls: Optional[list[float]] = None, vertical_puts: Optional[list[float]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| options | object | The Options data object. Use `load_options_chains()` to load the data. | None | False |
| days | list[int] | List of DTE(s) to get strategies for. Enter a single value, or multiple as a list. Defaults to all. | None | True |
| strike_price | float | The target strike price. Defaults to the last price of the underlying stock. | None | True |
| strangle_moneyness | list[float] | List of OTM moneyness to target, expressed as a percent value between 0 and 100.<br/>Enter a single value, or multiple as a list. Defaults to 5. | None | True |
| synthetic_long | list[float] | List of strikes for a synthetic long position. | None | True |
| synthetic_short | list[float] | List of strikes for a synthetic short position. | None | True |
| vertical_calls | list[float] | Call strikes for vertical spreads, listed as [sold strike, bought strike]. | None | True |
| vertical_puts | list[float] | Put strikes for vertical spreads, listed as [sold strike, bought strike]. | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Pandas DataFrame with the results. |
---

## Examples


Load data

```python
from openbb_terminal.stocks.options import options_chains_model
data = options_chains_model.load_options_chains("SPY")
```


Return just straddles

```python
options_chains_model.calculate_strategies(data)
```


Return strangles

```python
options_chains_model.calculate_strategies(data, strangle_moneyness = 10)
```


Return multiple values for both moneness and days:

```python
options_chains_model.calculate_strategies(data, days = [10,30,60,90], moneyness = [2.5,-5,10,-20])
```


Return vertical spreads for all expirations.

```python
options_chains_model.calculate_strategies(data, vertical_calls=[430,427], vertical_puts=[420,426])
```


Return synthetic short and long positions:

```python
options_chains_model.calculate_strategies(
```


data, days = [30,60], synthetic_short = [450,445], synthetic_long = [450,455]
)

---

