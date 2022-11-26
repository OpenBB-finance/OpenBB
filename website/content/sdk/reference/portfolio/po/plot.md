---
title: plot
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# plot

<Tabs>
<TabItem value="model" label="Model" default>

Display efficient frontier

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_view.py#L237)]

```python
openbb.portfolio.po.plot(portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, chart_type: str = "pie", kwargs: Any)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PoEngine | Portfolio optimization engine, by default None<br/>Use `portfolio.po.load` to load a portfolio engine | None | True |
| chart_type | str | Chart type, by default "pie"<br/>Options are "pie", "hist", "dd" or "rc" | pie | True |


---

## Returns

This function does not return anything

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
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="pie")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="hist")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="dd")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="rc")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="heat")
```

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
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
openbb.portfolio.po.plot(portfolio_engine=p, category="ASSET_CLASS", chart_type="pie")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="hist")
openbb.portfolio.po.plot(portfolio_engine=p, category="INDUSTRY", chart_type="dd")
openbb.portfolio.po.plot(portfolio_engine=p, category="COUNTRY", chart_type="rc")
openbb.portfolio.po.plot(portfolio_engine=p, category="ASSET_CLASS", chart_type="heat")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display efficient frontier

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_view.py#L237)]

```python
openbb.portfolio.po.plot_chart(portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, chart_type: str = "pie", kwargs: Any)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PoEngine | Portfolio optimization engine, by default None<br/>Use `portfolio.po.load` to load a portfolio engine | None | True |
| chart_type | str | Chart type, by default "pie"<br/>Options are "pie", "hist", "dd" or "rc" | pie | True |


---

## Returns

This function does not return anything

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
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="pie")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="hist")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="dd")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="rc")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="heat")
```

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
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
openbb.portfolio.po.plot(portfolio_engine=p, category="ASSET_CLASS", chart_type="pie")
openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="hist")
openbb.portfolio.po.plot(portfolio_engine=p, category="INDUSTRY", chart_type="dd")
openbb.portfolio.po.plot(portfolio_engine=p, category="COUNTRY", chart_type="rc")
openbb.portfolio.po.plot(portfolio_engine=p, category="ASSET_CLASS", chart_type="heat")
```

---



</TabItem>
</Tabs>