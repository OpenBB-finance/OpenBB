```
usage: customer [-h] [--export {csv,json,xlsx}]
```

List of customers from ticker provided. [Source: CSIMarket]

```
optional arguments:
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
```

Example (Apple and Tesla):
```
2022 Feb 16, 04:25 (✨) /stocks/dd/ $ customer
List of Customers: AMZN, T, AT, BBY, BIG, AVGO, EBAY, GME, LIVE, PTC, S, TMUS, TGT, WMT

2022 Feb 16, 04:26 (✨) /stocks/dd/ $ customer
List of Customers: Y, ALL, AIG, ACGL, AWH, AN, AZO, AVID, CAR, AXS, BRKA, BLBD, BRO, KMX, CAT, CUII, CINF, CRUS, CNFR, DGICA, DORM, DSPG, ESGR, ESNT, FNHC, GM, GBLI, HALL, THG, HCI, HRTG, HMN, JRVR, JANL, KMPR, KINS, KFS, KNX, KN, KOSS, LEAF, L, MKL, MCY, MET, MPAA, NSEC, ORLY, ORI, OSK, OB, PGR, REVG, SAFT, SMP, STFC, HIG, TRV, GTS, TRUE, UNAM, UFCS, UIHC, UVE, WRB, WTM, XL
```
