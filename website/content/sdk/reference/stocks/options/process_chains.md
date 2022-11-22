---
title: process_chains
description: OpenBB SDK Function
---

# process_chains

Function to take in the requests.get and return a DataFrame

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

