```
usage: lastcontracts [-p PAST_TRANSACTION_DAYS] [-l LIMIT] [-s] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Details US government spending. [Source: www.quiverquant.com]

```
optional arguments:
  -p PAST_TRANSACTION_DAYS, --past_transaction_days PAST_TRANSACTION_DAYS
                        Past transaction days (default: 2)
  -l LIMIT, --limit LIMIT
                        Limit of contracts to display (default: 20)
  -s, --sum             Flag to show total amount of contracts. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:

```
2022 Feb 16, 07:22 (🦋) /stocks/gov/ $ lastcontracts
                                                        Last Government Contracts
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Date                ┃ Ticker ┃ Amount    ┃ Description                                        ┃ Agency                                ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-02-12 00:00:00 │ EW     │ 32500.00  │ HEART VALVE                                        │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ HNGR   │ 0.00      │ PROSTHETIC LIMB                                    │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ WBA    │ 11425.69  │ JYNARQUE                                           │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ VSTO   │ 14563.20  │ AMMUNITION FOR TRAINING FOR SIU CLASSES            │ DEPARTMENT OF JUSTICE (DOJ)           │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ VSTO   │ 680239.08 │ 556M RH JACKETED FRANGIBLE AMMUNITION PN Z556AA40  │ DEPARTMENT OF HOMELAND SECURITY (DHS) │
│                     │        │           │ (DOD VERSION OF PN BC556X1)                        │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ VSTO   │ 1070.18   │ AMMUNITION ORDER - D45 W/MO                        │ DEPARTMENT OF JUSTICE (DOJ)           │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ VAR    │ 712143.00 │ PREVENTATIVE MAINTENANCE AND REPAIRS OF VARIAN     │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
│                     │        │           │ LINEAR ACCELERATORS LOCATED AT THE LTC CHARLES S.  │                                       │
│                     │        │           │ KETTLES VAMC                                       │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ VAR    │ 298800.00 │ DATA HOSTING FOR VARIAN LINAC SOFTWARE             │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
│                     │        │           │ (ECLIPSE/ARIA)                                     │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ UPS    │ 4500.00   │ EXPRESS MAIL AND COURIER SERVICES FOR THE COEUR    │ DEPARTMENT OF AGRICULTURE (USDA)      │
│                     │        │           │ D'ALENE NURSERY, ID                                │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ TTEK   │ 215214.00 │ SUPERFUND TECHNICAL ASSESSMENT & RESPONSE TEAM 5   │ ENVIRONMENTAL PROTECTION AGENCY (EPA) │
│                     │        │           │ (START V) CONTRACT FOR EPA REGION 7 - SITE/PROJECT │                                       │
│                     │        │           │ NAME: NEBRASKA SITE ASSESSMENTS.                   │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ TTEK   │ 65468.54  │ SUPERFUND TECHNICAL ASSESSMENT & RESPONSE TEAM 5   │ ENVIRONMENTAL PROTECTION AGENCY (EPA) │
│                     │        │           │ (START V) CONTRACT FOR EPA REGION 7 - SITE/PROJECT │                                       │
│                     │        │           │ NAME: FABALL ABANDONED CONTAINER.                  │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ TTEK   │ 60769.52  │ SUPERFUND TECHNICAL ASSESSMENT & RESPONSE TEAM 5   │ ENVIRONMENTAL PROTECTION AGENCY (EPA) │
│                     │        │           │ (START V) CONTRACT FOR EPA REGION 7 - SITE/PROJECT │                                       │
│                     │        │           │ NAME: 10TH STREET SITE ASSESSMENT IN COLUMBUS, NE. │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ TTEK   │ 231856.02 │ SUPERFUND TECHNICAL ASSESSMENT & RESPONSE TEAM 5   │ ENVIRONMENTAL PROTECTION AGENCY (EPA) │
│                     │        │           │ (START V) CONTRACT FOR EPA REGION 7 - SITE/PROJECT │                                       │
│                     │        │           │ NAME: IOWA SITE ASSESSMENTS.                       │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ T      │ 9817.28   │ TELECOMMUNICATION SERVICES (JANUARY)               │ DEPARTMENT OF JUSTICE (DOJ)           │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ T      │ 187.49    │ LOCAL LONG DISTANCE PHONE SERVICE - 2ND QUARTER FY │ DEPARTMENT OF JUSTICE (DOJ)           │
│                     │        │           │ 2022                                               │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ SYY    │ 88158.78  │ BASE FOOD ORDER TO REPLENISH THE WAREHOUSE.        │ DEPARTMENT OF JUSTICE (DOJ)           │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ SYK    │ 12938.43  │ HIP REPLACEMENT                                    │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ SYK    │ 43282.32  │ STRYKER NEPTUNE SERVICES                           │ DEPARTMENT OF VETERANS AFFAIRS (VA)   │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ SO     │ 4697.51   │ TO PROVIDE NON-PERSONAL SERVICE TO REPAIR FDC AT   │ GENERAL SERVICES ADMINISTRATION (GSA) │
│                     │        │           │ THE CUSTOM HOUSE (GSA BLDG. NO. TX0101ZZ), LOCATED │                                       │
│                     │        │           │ AT 701 SAN JACINTO STREET, HOUSTON, TX 77002-3673. │                                       │
├─────────────────────┼────────┼───────────┼────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2022-02-11 00:00:00 │ NOC    │ 416297.80 │ THE PURPOSE OF THIS CALL ORDER IS FOR THE          │ SOCIAL SECURITY ADMINISTRATION (SSA)  │
│                     │        │           │ CONTRACTOR TO PROVIDE DATA COLLECTION & ANALYTICS  │                                       │
│                     │        │           │ (M-21-31 ENTERPRISE LOGGING ONBOARDING SUPPORT)    │                                       │
│                     │        │           │ SERVICES.                                          │                                       │
└─────────────────────┴────────┴───────────┴────────────────────────────────────────────────────┴───────────────────────────────────────┘
```
