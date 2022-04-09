```text
usage: vis [-m {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd}] [-p PERIOD]
           [-cc CONVERT_CURRENCY] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [--raw] [-l LIMIT]
```

Visualize a particular metric with the filters selected [source: StockAnalysis]

```
optional arguments:
  -m {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd}, --metric {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd}
                        Metric to visualize (default: None)
  -p PERIOD, --period PERIOD
                        Limit number of periods to display (default: 12)
  -cc CONVERT_CURRENCY, --convert_currency CONVERT_CURRENCY
                        Convert the currency of the chosen country to a specified currency. By default, this is set to USD (US Dollars). (default: USD)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)

```

![vis](https://user-images.githubusercontent.com/46355364/159114414-8533bef1-aed2-4a4c-88a6-93a04c7513d2.png)
