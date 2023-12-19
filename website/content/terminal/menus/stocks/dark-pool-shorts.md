---
title: Dark Pools & Short Data
description: This documentation page introduces the dark pool and short data menu, which provides the user with tools for gauging the level of short interest, FTD rate, and off-exchange volume in NMS securities.
keywords:
- dark pool
- short data
- ftd
- off-exchange volume
- short interest
- nms
- short
- sidtc
- cover
- fail
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Dark Pool & Short Data - Stocks - Menus | OpenBB Terminal Docs" />

The purpose of this menu is to provide the user with tools for gauging the level of short interest, FTD rate, and off-exchange volume in a <a href="https://www.law.cornell.edu/cfr/text/17/242.600" target="_blank" rel="noreferrer noopener">NMS security</a>. There are also commands for looking at market as a whole. 

## Usage

Enter the `dps` menu from the `/stocks` menu, or through the absolute path:

```console
/stocks/dps
```

![Screenshot 2023-11-01 at 8 33 58 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/64775307-b79e-4ff6-95dd-ec676e1ab677)

The commands which are not ticker-specific are grouped at the top of the menu, and they provide screener-like utility. 

### Shorted

A list of the most-shorted stocks, according to Yahoo Finance, is displayed with the `shorted` command. It should be noted that this menu is only able to provide data for SEC-regulated equities.

```console
/stocks/dps/shorted
```

![Screenshot 2023-11-01 at 8 38 12 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/d1361b8f-0795-439f-b9f6-ace9cbde068a)

### HSI

The `hsi` command includes the percent of short interest relative to the float size.

```console
/stocks/dps/hsi
```

![Screenshot 2023-11-01 at 8 40 39 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/1287e58b-dbed-44a0-821a-769daebb3f29)

### PROM

`prom` performs a linear regression to scan for tickers with growing trade activity on ATS tapes, reported to <a href="https://otctransparency.finra.org/otctransparency/AtsIssueData" target="_blank" rel="noreferrer noopener">FINRA</a>.

```console
/stocks/dps/prom -n 50 -l 5 -t T1
```

```console
Processing Tier T1 ...
Processing regression on 50 promising tickers ...
```

![Screenshot 2023-11-01 at 8 45 21 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/13b67056-9d94-45f0-b483-41c1da773f0e)


Tier 2 NMS Tickers:

```console
/stocks/dps/prom -n 50 -l 5 -t T2
```

```console
Processing Tier T2 ...
Processing regression on 50 promising tickers ...
```

![Screenshot 2023-11-01 at 8 48 32 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/fab9bb45-fec9-4d51-8b77-0bb9697d8888)



`pos` provides a summary for the last reported trading day (information is updated in the early evening). Position represents a rolling twenty-day total and directional trends can be identified by watching the changes over time. Adding the `-a` flag will sort the list from the bottom up - the most negative - and creates a fuller picture when watching in tandom with the positive side of the ledger. Monitor the rate of change in position sizes, or a reversal in directional flow. This <a href="https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf?" target="_blank" rel="noreferrer noopener">white paper</a>, written by SqueezeMetrics, sheds some light on the trading activity reported here.

```console
/stocks/dps pos
```

![Screenshot 2023-11-01 at 8 55 25 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/8075ab29-cbac-448c-bfc4-a2ca250f6288)

The other end of the spectrum:

```console
/stocks/dps/pos -a
```

![Screenshot 2023-11-01 at 8 58 27 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/9bd6d148-ae36-4b7b-9faa-79db4dcb93ad)


### CTB

The cost-to-borrow is used as a proxy-measurement for an equity's specialness. `ctb` shows the  most expensive equities to short, and the number shares available to short, on Interactive Brokers.

```console
/stocks/dps/ctb -n 5
```

| Symbol   | Fees       |   Available |
|:---------|:-----------|------------:|
| ALPSQ    | 1187.0287% |      500000 |
| LEO      | 1034.2946% |      300000 |
| NIM      | 872.2794%  |        2000 |
| SVRE     | 801.5519%  |       15000 |
| APLM     | 753.8133%  |       65000 |

### FTD

The `ftd` command will lookup the SEC-reported fails-to-deliver data for a single company.  Use `load` to set the symbol.

```console
/stocks/dps/load cvna/ftd --start 2022-01-01
```

![Screenshot 2023-11-01 at 9 28 34 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/43409271-e306-4f13-9153-8cc322dde851)
