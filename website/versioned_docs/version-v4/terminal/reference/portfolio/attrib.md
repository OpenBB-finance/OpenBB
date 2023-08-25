---
title: attrib
description: OpenBB Terminal Function
---

# attrib

Displays sector attribution of the portfolio compared to the S&P 500

### Usage

```python
attrib [-p {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}] [-t {relative,absolute}] [--raw [RAW]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period in which to calculate attribution | all | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |
| type | Select between relative or absolute attribution values | relative | True | relative, absolute |
| raw | View raw attribution values in a table | False | True | None |


---

## Examples

```python
2022 Nov 03, 23:37 (🦋) /portfolio/ $ attrib -p 3m
```
---
