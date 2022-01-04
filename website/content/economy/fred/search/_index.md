```
usage: search [-s SERIES_TERM] [-n NUM] [-h]
```

Print series notes when searching for series. [Source: FRED]

```
optional arguments:
  -s SERIES_TERM, --series SERIES_TERM
                        Search for this series term. (default: None)
  -n NUM, --num NUM     Maximum number of series notes to display. (default: 5)
  -h, --help            show this help message (default: False)
```

Sample usage:
```python
(✨) (economy)(fred)> search gdp -n 3
╒═════════════════╤═════════════════════════════╤══════════════════════════════════════════════════════════════════════════════════════════════════════╕
│ Series ID       │ Title                       │ Description                                                                                          │
╞═════════════════╪═════════════════════════════╪══════════════════════════════════════════════════════════════════════════════════════════════════════╡
│ GDPC1           │ Real Gross Domestic Product │ BEA Account Code: A191RX  Real gross domestic product is the inflation adjusted value of the goods   │
│                 │                             │ and services produced by labor and property located in the United States.For more information see    │
│                 │                             │ the Guide to the National Income and Product Accounts of the United States (NIPA). For more          │
│                 │                             │ information, please visit the Bureau of Economic Analysis                                            │
│                 │                             │ (http://www.bea.gov/national/pdf/nipaguid.pdf).                                                      │
├─────────────────┼─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ A191RL1Q225SBEA │ Real Gross Domestic Product │ BEA Account Code: A191RL  Gross domestic product (GDP) is the value of the goods and services        │
│                 │                             │ produced by the nation's economy less the value of the goods and services used up in production. GDP │
│                 │                             │ is also equal to the sum of personal consumption expenditures, gross private domestic investment,    │
│                 │                             │ net exports of goods and services, and government consumption expenditures and gross investment.     │
│                 │                             │ Real values are inflation-adjusted estimates—that is, estimates that exclude the effects of price    │
│                 │                             │ changes.  For more information about this series, please visit the Bureau of Economic Analysis       │
│                 │                             │ (http://www.bea.gov/national/).                                                                      │
├─────────────────┼─────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GDP             │ Gross Domestic Product      │ BEA Account Code: A191RC  Gross domestic product (GDP), the featured measure of U.S. output, is the  │
│                 │                             │ market value of the goods and services produced by labor and property located in the United          │
│                 │                             │ States.For more information, see the Guide to the National Income and Product Accounts of the United │
│                 │                             │ States (NIPA) and the Bureau of Economic Analysis (http://www.bea.gov/national/pdf/nipaguid.pdf).    │
╘═════════════════╧═════════════════════════════╧══════════════════════════════════════════════════════════════════════════════════════════════════════╛


```