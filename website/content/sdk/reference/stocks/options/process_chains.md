---
title: process_chains
description: A details documentation page about how to use process_chains function
  of openbb.stocks.options in Python. This function takes API response from Tradier
  and returns a DataFrame with available options.
keywords:
- OpenBB Terminal
- stocks
- options
- process chains
- Python
- API
- Tradier
- DataFrame
- options trading
- documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="process_chains - Options - Stocks - Reference | OpenBB SDK Docs" />

Function to take in the request and return a DataFrame

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/tradier_model.py#L238)]

```python
openbb.stocks.options.process_chains(response: requests.models.Response)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| response | requests.models.Response | This is the response from tradier api. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with all available options |
---
