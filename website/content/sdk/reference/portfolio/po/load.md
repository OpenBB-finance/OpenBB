---
title: load
description: OpenBB SDK Function
---

# load

Load portfolio optimization engine

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L61)]

```python
openbb.portfolio.po.load(symbols: List[str] = None, symbols_file_path: str = None, parameters_file_path: str = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of symbols, by default None | None | True |
| symbols_file_path | str | Symbols file full path, by default None | None | True |
| parameters_file_path | str | Parameters file full path, by default None | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| PoEngine | Portfolio optimization engine |
---

