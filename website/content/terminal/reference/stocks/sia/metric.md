---
title: metric
description: An informational page detailing the usage and parameters of the 'metric'
  function. This function allows you to visualize various business and economic metrics
  such as return on assets (roa), return on equity (roe), current ratio (cr), and
  more. Understanding these metrics can aid in making informed financial and business
  decisions.
keywords:
- metric visualization
- roa
- roe
- cr
- qr
- de
- tc
- tcs
- tr
- rps
- rg
- eg
- pm
- gp
- gm
- ocf
- om
- fcf
- td
- ebitda
- ebitdam
- rec
- mc
- fte
- er
- bv
- ss
- pb
- beta
- fs
- peg
- ev
- fpe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/sia/metric - Reference | OpenBB Terminal Docs" />

Visualize a particular metric with the filters selected Available Metrics: roa return on assets roe return on equity cr current ratio qr quick ratio de debt to equity tc total cash tcs total cash per share tr total revenue rps revenue per share rg revenue growth eg earnings growth pm profit margins gp gross profits gm gross margins ocf operating cash flow om operating margins fcf free cash flow td total debt ebitda earnings before interest, taxes, depreciation and amortization ebitdam ebitda margins rec recommendation mean mc market cap fte full time employees er enterprise to revenue bv book value ss shares short pb price to book beta beta fs float shares sr short ratio peg peg ratio ev enterprise value fpe forward P/E,

### Usage

```python
metric -m {roa,roe,cr,qr,de,tc,tcs,tr,rps,rg,eg,pm,gp,gm,ocf,om,fcf,td,ebitda,ebitdam,rec,mc,fte,er,bv,ss,pb,beta,fs,peg,ev,fpe} [-l LIMIT] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| metric | Metric to visualize | None | False | roa, roe, cr, qr, de, tc, tcs, tr, rps, rg, eg, pm, gp, gm, ocf, om, fcf, td, ebitda, ebitdam, rec, mc, fte, er, bv, ss, pb, beta, fs, peg, ev, fpe |
| limit | Limit number of companies to display | 10 | True | None |
| raw | Output all raw data | False | True | None |

![metric roe](https://user-images.githubusercontent.com/46355364/159276031-ad84d153-9cb3-440e-9771-090aa6c467c4.png)

![metric fte](https://user-images.githubusercontent.com/46355364/159276335-d0ecb16f-eac2-421f-b69e-3bbffe126bd1.png)

---
