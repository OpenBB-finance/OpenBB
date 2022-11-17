---
title: calc_gamma
description: OpenBB SDK Function
---

# calc_gamma

## stocks_options_hedge_model.calc_gamma

```python title='openbb_terminal/stocks/options/hedge/hedge_model.py'
def calc_gamma(asset_price: float, asset_volatility: float, strike_price: float, time_to_expiration: float, risk_free_rate: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/hedge/hedge_model.py#L231)

Description: The second-order partial-derivative with respect to the underlying asset of the Black-Scholes equation

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset_price | int | The price. | None | False |
| asset_volatility | float | The implied volatility. | None | False |
| strike_price | float | The strike price. | None | False |
| time_to_expiration | float | The amount of days until expiration. Use annual notation thus a month would be 30 / 360. | None | False |
| risk_free_rate | float | The risk free rate. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| float | Returns the value for the gamma. |

## Examples

