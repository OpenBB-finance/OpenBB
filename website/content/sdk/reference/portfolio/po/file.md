---
title: file
description: OpenBB SDK Function
---

# file

Load portfolio optimization engine from file

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L108)]

```python
openbb.portfolio.po.file(portfolio_engine: portfolio_optimization.po_engine.PoEngine, parameters_file_path: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PoEngine | Portfolio optimization engine, by default None<br/>Use `portfolio.po.load` to load a portfolio engine | None | False |
| parameters_file_path | str | Parameters file full path, by default None | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict | Loaded parameters |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
p.get_params()
```

```
{}
```
```python
parameters = openbb.portfolio.po.file(portfolio_engine=p, parameters_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/optimization/defaults.ini")
```

```
Parameters:
    interval    : 3y
    log_returns : 0
    freq        : d
    maxnan      : 0.05
    threshold   : 0.3
    alpha       : 0.05
```
```python
p.get_params()
```

```
{'interval': '3y',
 'log_returns': '0',
 'freq': 'd',
 'maxnan': '0.05',
 'threshold': '0.3',
 'alpha': '0.05'}
```
```python
p.set_params({"risk_free_rate": 0.05})
p.get_params()
```

```
{'interval': '3y',
'log_returns': '0',
'freq': 'd',
'maxnan': '0.05',
'threshold': '0.3',
'alpha': '0.05',
'risk_free_rate': 0.05}
```
```python
weights, performance = openbb.portfolio.po.maxsharpe(portfolio_engine=p)
```

---

