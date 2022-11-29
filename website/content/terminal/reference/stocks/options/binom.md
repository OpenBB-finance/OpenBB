---
title: binom
description: OpenBB Terminal Function
---

# binom

Gives the option value using binomial option valuation

### Usage

```python
binom [-s STRIKE] [-p] [-e] [-x] [--plot] [-v VOLATILITY]
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

## Examples

```python
2022 Feb 16, 08:40 (🦋) /stocks/options/ $ binom -s 3100 -e --plot

AMZN call at $3100.00 expiring on 2022-03-25 is worth $136.85

2022 Feb 16, 08:41 (🦋) /stocks/options/ $ binom -s 3500 -p --plot

AMZN put at $3500.00 expiring on 2022-03-25 is worth $389.72
```
![binom](https://user-images.githubusercontent.com/46355364/154276789-b6786517-3bea-4aa7-9d2e-e6669dd82587.png)

---
