---
title: perf
description: OpenBB SDK Function
---

# perf

## portfolio_model.get_performance_vs_benchmark

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_performance_vs_benchmark(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, show_all_trades: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1581)

Description: Get portfolio performance vs the benchmark

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| show_all_trades | bool | Whether to also show all trades made and their performance (default is False) | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | None |

## Examples

