---
title: Comparison Analysis
description: This page provides an introduction to the Comparison Analysis (CA) sub-menu, within the Stocks menu, of the OpenBB Terminal.
keywords:
- comparison
- analysis
- peers
- similar stocks
- compare
- correlation
- historical
- screen
- pairs
- performance
- valuation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Comparison Analysis - Stocks - Menus | OpenBB Terminal Docs" />

The Comparison Analysis menu features different methods for comparing price, volume, and fundamentals across multiple stocks.

## Usage

Enter the menu from the `/stocks` menu.  If a ticker is not already loaded, enter one now by using the `ticker` command.

```console
/stocks/ca/ticker AMD
```

![Screenshot 2023-10-31 at 9 32 13 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/75ae98f4-e928-4319-8675-a09d4fe0ca87)

### Get

The `get` command will attempt to find the company peers of the base ticker.

```console
get --source Polygon
```

```console
[Polygon] Similar Companies: AMD, INTC, MCHP, NVDA, TXN, HPQ, XLK 
```

Refreshing the screen, `?` or `h` with no command, will update the list of similar companies.

![Screenshot 2023-10-31 at 9 38 17 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/418ca6fc-63d6-4ec6-99d5-ac1f1375b358)

### RMV

Use the syntax below to remove a ticker from the list:

```console
rmv xlk
```

```console
[Polygon] Similar Companies: AMD, INTC, MCHP, NVDA, TXN, HPQ
```

### Add

Similarly, add another one by using the `add` command.

```console
add mu
```

```console
[Custom] Similar Companies: HPQ, MCHP, TXN, INTC, MU, AMD, NVDA 
```

### Technical

With a list of similar companies populated, the `techincal` command will compare recent price performance metrics.

```console
technical
```

![Screenshot 2023-11-01 at 8 16 39 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/9eb4ea36-97a2-44ec-ad8a-8d7ec6145097)


### Cashflow

The `cashflow` command will compare recent annual and quarterly statements for a given period.

```console
cashflow --quarter
```

```console
Other available quarterly timeframes are: 31-Jul-2022, 31-Oct-2022, 31-Jan-2023, 30-Apr-2023, 31-Jul-2023
```

| Item                                   | HPQ (31-Jul-2023)   | MCHP (30-Jun-2023)   | TXN (30-Jun-2023)   | INTC (30-Jun-2023)   | MU (31-Aug-2023)   | AMD (30-Jun-2023)   | NVDA (31-Jul-2023)   |
|:---------------------------------------|:--------------------|:---------------------|:--------------------|:---------------------|:-------------------|:--------------------|:---------------------|
| Net Income before Extraordinaries      | 736M                | 666.4M               | 1.72B               | 1.47B                | (1.43B)            | 27M                 | 6.19B                |
| Net Income Growth                      | -30.96%             | 10.33%               | 0.82%               | 153.22%              | 24.58%             | 119.42%             | 202.94%              |
| Depreciation, Depletion & Amortization | 217M                | 222.9M               | 300M                | 2.28B                | 1.94B              | 873M                | 365M                 |
| Depreciation and Depletion             | 126M                | 50.5M                | 285M                | 1.83B                | 1.92B              | 180M                | 219M                 |
| Amortization of Intangible Assets      | 91M                 | 172.4M               | 15M                 | 444M                 | 20M                | 693M                | 146M                 |
| Deferred Taxes & Investment Tax Credit | 43M                 | 23.9M                | (52M)               |                      |                    | (274M)              | (746M)               |
| Deferred Taxes                         | 43M                 | 23.9M                | (52M)               |                      |                    | (274M)              | (746M)               |
| Investment Tax Credit                  |                     |                      |                     |                      |                    |                     |                      |
| Other Funds                            | 69M                 | 57.9M                | 110M                | 1.14B                | 260M               | 335M                | 714M                 |
| Funds from Operations                  | 1.07B               | 971.1M               | 2.08B               | 4.89B                | 767M               | 961M                | 6.52B                |
| Extraordinaries                        |                     |                      |                     |                      |                    |                     |                      |
| Changes in Working Capital             | (89M)               | 22.1M                | (681M)              | (2.08B)              | (518M)             | (582M)              | (174M)               |
| Receivables                            | (246M)              | (159.7M)             | (79M)               | 851M                 | 35M                | (272M)              | (2.99B)              |
| Accounts Payable                       | 781M                | 34.9M                | 74M                 | (331M)               | (340M)             | 236M                | 778M                 |
| Other Assets/Liabilities               | (659M)              | 50.5M                | (157M)              | (303M)               | (64M)              | (87M)               | (246M)               |
| Net Operating Cash Flow                | 976M                | 993.2M               | 1.4B                | 2.81B                | 249M               | 379M                | 6.35B                |
| Net Operating Cash Flow Growth         | 53.46%              | 39.99%               | 20.60%              | 257.31%              | 937.50%            | -22.02%             | 118.07%              |
| Net Operating Cash Flow / Sales        | 7.38%               | 43.40%               | 30.88%              | 21.69%               | 6.21%              | 7.07%               | 47.00%               |
