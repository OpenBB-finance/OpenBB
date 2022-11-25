---
title: close
description: OpenBB SDK Function
---

# close

Returns the price of a cryptocurrency

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_model.py#L181)]

```python
openbb.crypto.dd.close(symbol: str, start_date: str = "2010-01-01", end_date: Optional[str] = None, print_errors: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto to check close price (BTC or ETH) | None | False |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | str | Final date, format YYYY-MM-DD | None | True |
| print_errors | bool | Flag to print errors. Default: True | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | price over time |
---

