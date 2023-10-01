---
title: show
description: OpenBB SDK Function
---

# show

Show portfolio optimization results

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L2361)]

```python
openbb.portfolio.po.show(portfolio_engine: portfolio_optimization.po_engine.PoEngine, category: str = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PoEngine | Portfolio optimization engine<br/>Use `portfolio.po.load` to load a portfolio engine | None | False |
| category | str | Category to show, by default None<br/>After loading a portfolio with `portfolio.po.load` you can use<br/>the object method `get_available_categories()` to get a list of available categories.<br/>You can also use the object method `set_categories_dict()` to set a custom dictionary<br/>of categories. The dictionary must contain "CURRENT_INVESTED_AMOUNT" and "CURRENT_WEIGHTS"<br/>as keys as shown in the example below. | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]] | Portfolio weights and categories |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols=["AAPL", "MSFT", "AMZN"])
d = {
```

```
"SECTOR": {
            "AAPL": "INFORMATION TECHNOLOGY",
            "MSFT": "INFORMATION TECHNOLOGY",
            "AMZN": "CONSUMER DISCRETIONARY",
        },
        "CURRENT_INVESTED_AMOUNT": {
            "AAPL": "100000.0",
            "MSFT": "200000.0",
            "AMZN": "300000.0",
        },
        "CURRENCY": {
            "AAPL": "USD",
            "MSFT": "USD",
            "AMZN": "USD",
        },
    }
```
```python
p.set_categories_dict(categories=d)
weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
p.get_available_categories()
```

```
['SECTOR']
```
```python
weights_df, category_df = openbb.portfolio.po.show(portfolio_engine=p, category="SECTOR")
```

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
p.get_available_categories()
```

```
['ASSET_CLASS',
 'SECTOR',
 'INDUSTRY',
 'COUNTRY',
 'CURRENT_INVESTED_AMOUNT',
 'CURRENCY']
```
```python
weights_df, category_df = openbb.portfolio.po.show(portfolio_engine=p, category="ASSET_CLASS")
```

---

