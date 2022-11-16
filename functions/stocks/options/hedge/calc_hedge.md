---
title: calc_hedge
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# calc_hedge

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_hedge_model.calc_hedge

```python title='openbb_terminal/stocks/options/hedge/hedge_model.py'
def calc_hedge(portfolio_option_amount: float, side: str, greeks: dict, sign: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/hedge/hedge_model.py#L12)

Description: Determine the hedge position and the weights within each option and

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_option_amount | float | Number to show | None | False |
| side | str | Whether you have a Call or Put instrument | None | False |
| greeks | dict | Dictionary containing delta, gamma and vega values for the portfolio and option A and B. Structure is
as follows: {'Portfolio': {'Delta': VALUE, 'Gamma': VALUE, 'Vega': VALUE}} etc | None | False |
| sign | int | Whether you have a long (1) or short (-1) position | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| float | None |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_hedge_view.show_calculated_hedge

```python title='openbb_terminal/stocks/options/hedge/hedge_view.py'
def show_calculated_hedge(portfolio_option_amount: float, side: str, greeks: dict, sign: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/hedge/hedge_view.py#L62)

Description: Determine the hedge position and the weights within each option and

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_option_amount | float | Number to show | None | False |
| side | str | Whether you have a Call or Put instrument | None | False |
| greeks | dict | Dictionary containing delta, gamma and vega values for the portfolio and option A and B. Structure is
as follows: {'Portfolio': {'Delta': VALUE, 'Gamma': VALUE, 'Vega': VALUE}} etc | None | False |
| sign | int | Whether you have a long (1) or short (-1) position | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| A table with the neutral portfolio weights. | None |

## Examples



</TabItem>
</Tabs>