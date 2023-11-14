---
title: load
description: This page provides detailed documentation for the 'load' function of
  the OpenBB portfolio optimization engine. It includes source code, parameters detail,
  return type, and coding examples.
keywords:
- portfolio optimization
- po.load function
- OpenBB portfolio
- PoEngine
- openbb_terminal.sdk
- coding examples
- software documentation
- parameters detail
- portfolio allocation
- AAPL
- MSFT
- AMZN
- Python code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.po.load - Reference | OpenBB SDK Docs" />

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

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
```

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols=["AAPL", "MSFT", "AMZN"])
weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
```

---
