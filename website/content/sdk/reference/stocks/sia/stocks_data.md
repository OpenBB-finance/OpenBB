---
title: stocks_data
description: OpenBB SDK Function
---

# stocks_data

Get stocks data based on a list of stocks and the finance key. The function searches for the

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/stockanalysis_model.py#L84)]

```python
openbb.stocks.sia.stocks_data(symbols: List[str] = None, finance_key: str = "ncf", stocks_data: dict = None, period: str = "annual", symbol: str = "USD")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | list | A list of tickers that will be used to collect data for. | None | True |
| finance_key | str | The finance key used to search within the SA_KEYS for the correct name of item<br/>on the financial statement | ncf | True |
| stocks_data | dict | A dictionary that is empty on initialisation but filled once data is collected<br/>for the first time. | None | True |
| period | str | Whether you want annually, quarterly or trailing financial statements. | annual | True |
| symbol | str | Choose in what currency you wish to convert each company's financial statement.<br/>Default is USD (US Dollars). | USD | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary of filtered stocks data separated by financial statement |
---

