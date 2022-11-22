---
title: binom
description: OpenBB Terminal Function
---

# binom

Gives the option value using binomial option valuation

### Usage

```python
usage: binom [-s STRIKE] [-p] [-e] [-x] [--plot] [-v VOLATILITY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| strike | Strike price for option shown | 0 | True | None |
| put | Value a put instead of a call | False | True | None |
| europe | Value a European option instead of an American one | False | True | None |
| export | Export an excel spreadsheet with binomial pricing data | False | True | None |
| plot | Plot expected ending values | False | True | None |
| volatility | Underlying asset annualized volatility. Historical volatility used if not supplied. | None | True | None |
---

