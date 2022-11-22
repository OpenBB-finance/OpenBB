---
title: plot
description: OpenBB Terminal Function
---

# plot

Shows a plot for the given x and y variables

### Usage

```python
usage: plot [-p] [-x {ltd,s,lp,b,a,c,pc,v,oi,iv}] [-y {ltd,s,lp,b,a,c,pc,v,oi,iv}] [-c {smile}]
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

