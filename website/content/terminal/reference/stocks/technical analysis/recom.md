---
title: recom
description: OpenBB Terminal Function
---

# recom

Print tradingview recommendation based on technical indicators. [Source: Tradingview]

### Usage

```python
usage: recom
             [-s {australia,brazil,cfd,crypto,euronext,forex,france,germany,hongkong,india,indonesia,malaysia,philippines,russia,ksa,rsa,korea,spain,sweden,taiwan,thailand,turkey,uk,america,vietnam}]
             [-e EXCHANGE] [-i {1m,5m,15m,1h,4h,1d,1W,1M}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| screener | Screener. See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html | america | True | australia, brazil, cfd, crypto, euronext, forex, france, germany, hongkong, india, indonesia, malaysia, philippines, russia, ksa, rsa, korea, spain, sweden, taiwan, thailand, turkey, uk, america, vietnam |
| exchange | Set exchange. For Forex use: 'FX_IDC', and for crypto use 'TVC'. See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html. By default Alpha Vantage tries to get this data from the ticker. |  | True | None |
| interval | Interval, that corresponds to the recommendation given by tradingview based on technical indicators. See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html |  | True | 1m, 5m, 15m, 1h, 4h, 1d, 1W, 1M |
---

