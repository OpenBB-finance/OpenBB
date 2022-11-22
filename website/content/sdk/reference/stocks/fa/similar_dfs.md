---
title: similar_dfs
description: OpenBB SDK Function
---

# similar_dfs

Get dataframes for similar companies

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/dcf_model.py#L468)]

```python
openbb.stocks.fa.similar_dfs(symbol: str, info: Dict[str, Any], n: int, no_filter: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to create a dataframe for | None | False |
| into | Dict[str,Any] | The dictionary produced from the yfinance.info function | None | True |
| n | int | The number of similar companies to produce | None | False |
| no_filter | bool | True means that we do not filter based on market cap | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List[str, pd.DataFrame] | A list of similar companies |
---

