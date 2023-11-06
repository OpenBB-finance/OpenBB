---
title: Government
description: This documentation pages describes the government trading menu hwere users can access the reported trades of elected officials, lobbyist activity, awarded contracts, and general spending of the United States Treasury Department.
keywords:
- government
- government trading
- lobbyist activity
- awarded contracts
- treasury
- representatives
- senate
- the house
- congress
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Government - Stocks - Data Available | OpenBB Terminal Docs" />

The features in this menu are intended to show the reported trades of elected officials, lobbyist activity, awarded contracts, and general spending of the United States Treasury Department. This menu only covers the USA, or companies that trade on US exchanges. The information in this menu is compiled by <a href="https://www.quiverquant.com/" target="_blank" rel="noreferrer noopener">QuiverQuant</a>. 

## Usage

Enter the menu from `/stocks` with `gov`, or via the absolute path:

```console
/stocks/gov
```

The menu is divided into two sections. Features under the `Explore` do not depend on individual tickers, while the commands listed under `Ticker` do. 

![Screenshot 2023-11-01 at 11 18 40 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/51be579a-7fa0-4ef8-b04c-f2f06c9ef099)

A symbol can be set by using `load`.

### Lasttrades

The `lasttrades` command displays the most recent purchase and sale disclosures by representatives.

![Screenshot 2023-11-01 at 11 23 48 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/7fe9823e-bdc0-4cb6-8a74-8634f407c145)


### Toplobbying

`toplobbying` shows which public companies are spending the most on lobbying efforts.

```console
/stocks/gov/toplobbying --limit 1
```

![Screenshot 2023-11-01 at 11 29 33 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/9b2564b2-f503-454a-adc4-f397d1b940f2)

### Lobbying

For descriptions of each lobbying event from a company, load a ticker and then use the `lobbying` command.

```console
/stocks/gov/load lmt/lobbying --limit 1
```

```console
2023-10-05: LOCKHEED MARTIN CORPORATION $50000

Tax matters impacting Lockheed Martin Corporation.

Defense issues impacting Lockheed Martin Corporation.

H.R.2670/S.2226 - National Defense Authorization Act for Fiscal Year 2024.

Defense Appropriations.
```

### Lastcontracts

`lastcontracts` is a list of the most recently awarded government contracts.

```console
/stocks/gov/lastcontracts --limit 
```

![Screenshot 2023-11-01 at 12 27 34 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b290c8db-a1b5-4f6c-bea2-65cf16eae3e7)

