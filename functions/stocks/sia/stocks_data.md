---
title: stocks_data
description: OpenBB SDK Function
---

# stocks_data

## stocks_sia_stockanalysis_model.get_stocks_data

```python title='openbb_terminal/stocks/sector_industry_analysis/stockanalysis_model.py'
def get_stocks_data(symbols: List[str], finance_key: str, stocks_data: dict, period: str, symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/stockanalysis_model.py#L84)

Description: Get stocks data based on a list of stocks and the finance key. The function searches for the

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | list | A list of tickers that will be used to collect data for. | None | False |
| finance_key | str | The finance key used to search within the SA_KEYS for the correct name of item
on the financial statement | None | False |
| stocks_data | dict | A dictionary that is empty on initialisation but filled once data is collected
for the first time. | None | False |
| period | str | Whether you want annually, quarterly or trailing financial statements. | None | False |
| symbol | str | Choose in what currency you wish to convert each company's financial statement.
Default is USD (US Dollars). | USD | False |

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary of filtered stocks data separated by financial statement |

## Examples

