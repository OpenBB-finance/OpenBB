---
title: set
description: This documentation page provides an understanding of the different portfolio
  optimization models available. It explains how to use the set command in Python
  to select a model from a list, including maxsharpe, minrisk, maxutil, and others.
keywords:
- portfolio optimization models
- set command
- maxsharpe
- minrisk
- maxutil
- maxret
- maxdiv
- maxdecorr
- ef
- riskparity
- relriskparity
- hrp
- herc
- nco
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/parameters/set /po - Reference | OpenBB Terminal Docs" />

Select one of the portfolio optimization models

### Usage

```python
set -m {maxsharpe,minrisk,maxutil,maxret,maxdiv,maxdecorr,ef,riskparity,relriskparity,hrp,herc,nco}
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| model | Frequency used to calculate returns | None | False | maxsharpe, minrisk, maxutil, maxret, maxdiv, maxdecorr, ef, riskparity, relriskparity, hrp, herc, nco |

---
