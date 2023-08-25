---
title: vis
description: OpenBB Terminal Function
---

# vis

Visualize a particular metric with the filters selected Balance Sheet Statement ce Cash & Equivalents sti Short-Term Investments cce Cash & Cash Equivalents rec Receivables inv Inventory oca Other Current Assets tca Total Current Assets ppe Property, Plant & Equipment lti Long-Term Investments gai Goodwill and Intangibles olta Other Long-Term Assets tlta Total Long-Term Assets ta Total Assets ap Accounts Payable dr Deferred Revenue cd Current Debt ocl Other Current Liabilities tcl Total Current Liabilities ltd Long-Term Debt oltl Other Long-Term Liabilities tltl Total Long-Term Liabilities tl Total Liabilities ret Retained Earnings ci Comprehensive Income se Shareholders' Equity tle Total Liabilities and Equity Income Statement re Revenue cr Cost of Revenue gp Gross Profit sga Selling, Genera & Admin rd Research & Development ooe Other Operating Expenses oi Operating Income ie Interest Expense / Income oe Other Expense / Income it Income Tax ni Net Income pd Preferred Dividends Cash Flow Statement ninc Net Income da Depreciation & Amortization sbc Share-Based Compensation ooa Other Operating Activities ocf Operating Cash Flow cex Capital Expenditures acq Acquisitions cii Change in Investments oia Other Investing Activities icf Investing Cash Flow dp Dividends Paid si Share Insurance / Repurchase di Debt Issued / Paid ofa Other Financing Activities fcf Financing Cash Flow ncf Net Cash Flow

### Usage

```python
vis -m {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd} [-p PERIOD] [-c CURRENCY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| metric | Metric to visualize | None | False | ce, sti, cce, rec, inv, oca, tca, ppe, lti, gai, olta, tlta, ta, ap, dr, cd, ocl, tcl, ltd, oltl, tltl, tl, ret, ci, se, tle, ninc, da, sbc, ooa, ocf, cex, acq, cii, oia, icf, dp, si, di, ofa, fcf, ncf, re, cr, gp, sga, rd, ooe, oi, ie, oe, it, ni, pd |
| period | Limit number of periods to display | 12 | True | None |
| currency | Convert the currency of the chosen country to a specified currency. By default, this is set to USD (US Dollars). | USD | True | None |

![vis](https://user-images.githubusercontent.com/46355364/159114414-8533bef1-aed2-4a4c-88a6-93a04c7513d2.png)

---
