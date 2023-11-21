---
title: bench
description: This page provides a detailed guideline on how to load in benchmarks
  for a portfolio based on the ticker. It elaborates the usage of the 'bench' command
  in python, its parameters, choices and gives practical examples of its application.
keywords:
- benchmark
- portfolio
- SPDR S&P 500 ETF Trust (SPY)
- iShares Core S&P 500 ETF (IVV)
- Vanguard Total Stock Market ETF (VTI)
- Vanguard S&P 500 ETF (VOO)
- Invesco QQQ Trust (QQQ)
- full_shares
- shares
- choices
- parameters
- Vanguard FTSE Developed Markets ETF (VEA)
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /bench - Reference | OpenBB Terminal Docs" />

Load in a benchmark from a selected list or set your own based on the ticker.

### Usage

```python wordwrap
bench -b BENCHMARK [-s]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| benchmark | -b  --benchmark | Set the benchmark for the portfolio. By default, this is SPDR S&P 500 ETF Trust (SPY). | SPY | False | None |
| full_shares | -s  --full_shares | Whether to only make a trade with the benchmark when a full share can be bought (no partial shares). | False | True | None |


---

## Examples

```python
2022 May 10, 09:53 (🦋) /portfolio/ $ bench Vanguard FTSE Developed Markets ETF (VEA)

Benchmark: Vanguard Developed Markets Index Fund (VEA)

2022 May 10, 09:53 (🦋) /portfolio/ $
```
---
