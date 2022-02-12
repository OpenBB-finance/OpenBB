```text
usage: vis [-m {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd}] [-l LIMIT]
           [-p PERIOD] [-r] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Visualize a particular metric with the filters selected [source: StockAnalysis]

```
optional arguments:
  -m {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd}, --metric {ce,sti,cce,rec,inv,oca,tca,ppe,lti,gai,olta,tlta,ta,ap,dr,cd,ocl,tcl,ltd,oltl,tltl,tl,ret,ci,se,tle,ninc,da,sbc,ooa,ocf,cex,acq,cii,oia,icf,dp,si,di,ofa,fcf,ncf,re,cr,gp,sga,rd,ooe,oi,ie,oe,it,ni,pd}
                        Metric to visualize (default: None)
  -l LIMIT, --limit LIMIT
                        Limit number of companies to display (default: 10)
  -p PERIOD, --period PERIOD
                        Limit number of periods to display (default: 12)
  -r, --raw             Output all raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```
