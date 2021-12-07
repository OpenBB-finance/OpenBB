```text
usage: metric [-m {roa,roe,cr,qr,de,tc,tcs,tr,rps,rg,eg,pm,gp,gm,ocf,om,fcf,td,ebitda,ebitdam,rec,mc,fte,er,bv,ss,pb,beta,fs,peg,ev,fpe}] [-l LIMIT] [-r] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Visualise a particular metric with the filters selected

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


<img width="1400" alt="Feature Screenshot - metric" src="https://user-images.githubusercontent.com/85772166/145095318-25f4cffd-9d55-4f5e-87cd-3b35a4ce6e1c.png">
