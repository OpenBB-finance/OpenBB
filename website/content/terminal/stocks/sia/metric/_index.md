```text
usage: metric [-m {roa,roe,cr,qr,de,tc,tcs,tr,rps,rg,eg,pm,gp,gm,ocf,om,fcf,td,ebitda,ebitdam,rec,mc,fte,er,bv,ss,pb,beta,fs,peg,ev,fpe}] [-l LIMIT] [-r] [-h] [--export EXPORT]
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
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )

```

Return on Equity example:
```
│ Industry          : Software - Infrastructure                                                                                                                                                                                           │
│ Sector            : Technology                                                                                                                                                                                                          │
│ Country           : United States                                                                                                                                                                                                       │
│ Market Cap        : Large                                                                                                                                                                                                               │
│ Exclude Exchanges : True                                                                                                                                                                                                                │
│ Period            : Annual    


2022 Mar 21, 09:51 (✨) /stocks/sia/ $ metric roe
```
![metric roe](https://user-images.githubusercontent.com/46355364/159276031-ad84d153-9cb3-440e-9771-090aa6c467c4.png)


Full Time Employees example:
```
│ Industry          : Financial Data & Stock Exchanges                                                                                                                                                                                    │
│ Sector            : Financial Services                                                                                                                                                                                                  │
│ Country           : United States                                                                                                                                                                                                       │
│ Market Cap        : Large                                                                                                                                                                                                               │
│ Exclude Exchanges : True                                                                                                                                                                                                                │
│ Period            : Annual   

2022 Mar 21, 09:55 (✨) /stocks/sia/ $ metric fte
```
![metric fte](https://user-images.githubusercontent.com/46355364/159276335-d0ecb16f-eac2-421f-b69e-3bbffe126bd1.png)

