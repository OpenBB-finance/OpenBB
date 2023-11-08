---
title: plot
description: Plot documentation page provides information on how to show a plot for
  the given x and y variables, with variables being last trade date, strike, last
  price, bid, ask, percentage change, volume, open interest, implied volatility and
  more. It also shows usage examples and available customizations.
keywords:
- plot
- show plot
- trade date
- strike
- last price
- bid
- ask
- change
- percent change
- volume
- open interest
- implied volatility
- stocks
- options
- graph
- custom graphs
- smile
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/options/plot - Reference | OpenBB Terminal Docs" />

Shows a plot for the given x and y variables

### Usage

```python
plot [-p] [-x {ltd,s,lp,b,a,c,pc,v,oi,iv}] [-y {ltd,s,lp,b,a,c,pc,v,oi,iv}] [-c {smile}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| put | Shows puts instead of calls | False | True | None |
| x | ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility | s | True | ltd, s, lp, b, a, c, pc, v, oi, iv |
| y | ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility | iv | True | ltd, s, lp, b, a, c, pc, v, oi, iv |
| custom | Choose from already created graphs | None | True | smile |


---

## Examples

```python
2022 Feb 16, 09:37 (🦋) /stocks/options/ $ plot -p -x s -y iv
```
![plot](https://user-images.githubusercontent.com/46355364/154287325-97de8945-a44c-418d-9e88-5123ee70469f.png)

---
