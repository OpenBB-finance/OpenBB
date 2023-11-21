---
title: similar_dfs
description: The similar_dfs function in OpenBB is documented on this page. This function
  is used for generating dataframes for similar companies by taking inputs such as
  a ticker symbol, the output from the yfinance.info function and the number of similar
  companies to produce. The option of filtering based on market cap is also provided.
  Going through this documentation provides valuable information to understand the
  use and functioning of the similar_dfs function.
keywords:
- similar_dfs
- dataframes
- similar companies
- stocks
- fundamental analysis
- yfinance.info function
- ticker symbol
- market cap
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.similar_dfs - Reference | OpenBB SDK Docs" />

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
