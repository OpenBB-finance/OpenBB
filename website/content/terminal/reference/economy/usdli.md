---
title: usdli
description: The USD Liquidity Index is defined as [WALCL - WLRRAL - WDTGAL]
keywords:
- economy
- usdli
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /usdli - Reference | OpenBB Terminal Docs" />

The USD Liquidity Index is defined as: [WALCL - WLRRAL - WDTGAL]. It is expressed in billions of USD.

### Usage

```python wordwrap
usdli [-o {SP500,CBBTCUSD,CBETHUSD,DJCA,DJIA,DJTA,DJUA,NASDAQCOM,NASDAQ100,WILL2500PR,WILL2500PRGR,WILL2500INDGR,WILL2500PRVAL,WILL2500INDVAL,WILL4500PR,WILL5000PR,WILL5000PRFC,WILLLRGCAP,WILLLRGCAPPR,WILLLRGCAPGRPR,WILLLRGCAPVALPR,WILLMIDCAP,WILLMIDCAPPR,WILLMIDCAPGRPR,WILLMIDCAPVALPR,WILLSMLCAP,WILLSMLCAPPR,WILLSMLCAPGR,WILLSMLCAPVAL,WILLMICROCAP,WILLREITIND,WILLRESIPR,DTWEXBGS}] [-s]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| overlay | -o  --overlay | The equity index to compare against. Set `show = True` for the list of choices. | SP500 | True | SP500, CBBTCUSD, CBETHUSD, DJCA, DJIA, DJTA, DJUA, NASDAQCOM, NASDAQ100, WILL2500PR, WILL2500PRGR, WILL2500INDGR, WILL2500PRVAL, WILL2500INDVAL, WILL4500PR, WILL5000PR, WILL5000PRFC, WILLLRGCAP, WILLLRGCAPPR, WILLLRGCAPGRPR, WILLLRGCAPVALPR, WILLMIDCAP, WILLMIDCAPPR, WILLMIDCAPGRPR, WILLMIDCAPVALPR, WILLSMLCAP, WILLSMLCAPPR, WILLSMLCAPGR, WILLSMLCAPVAL, WILLMICROCAP, WILLREITIND, WILLRESIPR, DTWEXBGS |
| show | -s  --show | Show the list of available equity indices to overlay. | False | True | None |

---
