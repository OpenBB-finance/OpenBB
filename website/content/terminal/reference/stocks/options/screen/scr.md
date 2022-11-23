---
title: scr
description: OpenBB Terminal Function
---

# scr

Screener filter output from https://ops.syncretism.io/index.html. Where: CS: Contract Symbol; S: Symbol, T: Option Type; Str: Strike; Exp v: Expiration; IV: Implied Volatility; LP: Last Price; B: Bid; A: Ask; V: Volume; OI: Open Interest; Y: Yield; MY: Monthly Yield; SMP: Regular Market Price; SMDL: Regular Market Day Low; SMDH: Regular Market Day High; LU: Last Trade Date; LC: Last Crawl; ITM: In The Money; PC: Price Change; PB: Price-to-book.

### Usage

```python
usage: scr
           [-p {template.ini,TSLA_Calls_90Days.ini,high_IV.ini,TSLA_Poots.ini,SPY_ATM_Poots.ini,Highest_OI.ini,SPY_ATM_Calls.ini,Long_FAANGM.ini,Highest_Volume.ini,3DTE_Degenerate.ini,Highest_IV.ini}]
           [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| preset | Filter presets | high_IV | True | template.ini, TSLA_Calls_90Days.ini, high_IV.ini, TSLA_Poots.ini, SPY_ATM_Poots.ini, Highest_OI.ini, SPY_ATM_Calls.ini, Long_FAANGM.ini, Highest_Volume.ini, 3DTE_Degenerate.ini, Highest_IV.ini |
| limit | Limit of random entries to display. Default shows all | 10 | True | None |

---
