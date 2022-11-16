---
title: equal
description: OpenBB SDK Function
---

# equal

## portfolio_optimization_optimizer_model.get_equal_weights

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py'
def get_equal_weights(symbols: List[str], interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, value: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py#L164)

Description: Equally weighted portfolio, where weight = 1/# of symbols

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio stocks | None | False |
| interval | str | interval to get stock data, by default "3mo" | None | True |
| start_date | str | If not using interval, start date string (YYYY-MM-DD) | None | True |
| end_date | str | If not using interval, end date string (YYYY-MM-DD). If empty use last
weekday. | None | True |
| log_returns | bool | If True calculate log returns, else arithmetic returns. Default value
is False | value | True |
| freq | str | The frequency used to calculate returns. Default value is 'D'. Possible
values are:

- 'D' for daily returns.
- 'W' for weekly returns.
- 'M' for m' for monthly returns. | value | True |
| maxnan | float | Max percentage of nan values accepted per asset to be included in
returns. | None | False |
| threshold | float | Value used to replace outliers that are higher to threshold. | None | False |
| method | str | Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | value | False |
| value | float | Amount to allocate.  Returns percentages if set to 1. | None | True |

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary of weights where keys are the tickers |

## Examples

