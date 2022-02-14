```text
usage: metric [-m {roa,roe,cr,qr,de,tc,tcs,tr,rps,rg,eg,pm,gp,gm,ocf,om,fcf,td,ebitda,ebitdam,rec,mc,fte,er,bv,ss,pb,beta,fs,peg,ev,fpe}] [-l LIMIT] [-r] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Visualise a particular metric with the filters selected [source: Yahoo Finance]

```
optional arguments:
  -m {roa,roe,cr,qr,de,tc,tcs,tr,rps,rg,eg,pm,gp,gm,ocf,om,fcf,td,ebitda,ebitdam,rec,mc,fte,er,bv,ss,pb,beta,fs,peg,ev,fpe}, --metric {roa,roe,cr,qr,de,tc,tcs,tr,rps,rg,eg,pm,gp,gm,ocf,om,fcf,td,ebitda,ebitdam,rec,mc,fte,er,bv,ss,pb,beta,fs,peg,ev,fpe}
                        Metric to visualize (default: None)
  -l LIMIT, --limit LIMIT
                        Limit number of companies to display (default: 10)
  -r, --raw             Output all raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![metric](https://user-images.githubusercontent.com/46355364/153871438-dcd1c84e-eff1-4842-9ad6-e7bdaf2b6e1f.png)
