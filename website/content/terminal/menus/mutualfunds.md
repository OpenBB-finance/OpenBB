---
title: Mutual Funds
description: The documentation presents various commands and functions available within
  the Mutual Funds menu, enabling users to analyze and get detailed insights about
  different mutual funds. It covers features like searching funds, loading fund data,
  analyzing sector weightings, and viewing current fund holdings, among others.
keywords:
- Mutual funds
- Fund analysis
- Investment
- Fund listings
- /funds commands
- Fund data
- Mutual fund information
- Fund sector weightings
- Mutual fund holdings
- Mutual fund carbon metrics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Mutual Funds - Menus | OpenBB Terminal Docs" />

The Mutual Funds menu provides a global view of the mutual funds universe.  

## Usage

Enter the menu by typing, `funds`, from the main menu. Or, use the absolute path:

```console
/funds
```

Commands in the Mutual Funds menu are grouped according to the workflow.

| Function Key |                                                   Description |
| :----------- | ------------------------------------------------------------: |
| country      |                                       Set the target country. |
| search       |           Search for a mutual fund within the target country. |
| load         |                              Load a mutual fund for analysis. |
| plot         |                        Plot the historical price performance. |
| sector       | A chart of the sector weightings against the benchmark index. |
| holdings     |                                 Current holdings of the fund. |
| carbon       |                                  Carbon metrics for the fund. |
| exclusion    |             The fund's policy for excluding investment types. |
| alswe        |             Display the fund's allocation data (Sweden-only). |
| infoswe      |                           Get fund information (Sweden only). |

### Country

To use the menu, a country must be selected, and the default is `united_states`.  To select a different one, type `country`, followed by the `spacebar`.  This will bring up a list that can be picked from using the up/down arrow keys.

![Mutual Funds Menu](https://user-images.githubusercontent.com/85772166/235046797-0541dfbf-8f2a-41a0-a70b-d6fb890aa61d.png)

Refresh the screen, by typing `?`, to verify the choice has been made.

![Selecting a Country](https://user-images.githubusercontent.com/85772166/235046837-4bc9ad55-a4ca-411d-a3b4-800fe2e03db1.png)

### Search

The most effective way to sift through a vast quantity of funds is to use the `search` function broadly, then narrow the focus using the built-in filters on the displayed table.  In the example below, there are 668 results returned for `RBC` and `Canada`.  Filtering for money market funds gets it down to only ten funds.

```console
/funds/country canada/search rbc --limit 1000
```

![Search Funds](https://user-images.githubusercontent.com/85772166/235046894-6cae803b-6b42-4e24-9d16-a02be06599e9.png)

### Load

A mutual fund is loaded by using the ID number, which is the column labeled, `SECID`, on the left side of the table.

```console
load F0CAN05LTL
```

```console
The fund RBC Premium Money Market Fund A - 52.8.RBF447 (F0CAN05LTL) was successfully loaded.
```

### Holdings

With a fund loaded, get the weighting of the portfolio using the `holdings` command.

:::note
The holdings data returned will vary by country.  Some will only return the top ten, while others will publish the entire portfolio.
:::

```console
/funds/country canada/load F00000U48G/holdings
```

![Holdings](https://user-images.githubusercontent.com/85772166/235046949-e4aa2a5c-149d-4733-80a2-e1a703741cd3.png)

In contrast, the iShares Developed Real Estate Index Fund Investor A Shares, from the United States, returns 449 results.

```console
funds/country united_states/load F00000VW8Z/holdings
```

![Holdings](https://user-images.githubusercontent.com/85772166/235047003-7e4e0e0f-7a72-416e-a40a-8f9d30027c35.png)

### Plot

Plot historical performance of the fund against its benchmark index or the broad category.

```console
/funds/country united_states/load F00000VW8Z --start 2000-01-01/plot -c both
```

![Plot Performance](https://user-images.githubusercontent.com/85772166/235047052-0f7cd672-534f-4a03-b6af-a5ec53ff1718.png)

### Sector

The `sector` command displays a breakdown of sector weightings, compared against the benchmark index and broad category.

```console
/funds/country united_states/load F00000ZAFI/sector
```

![Sector Breakdown](https://user-images.githubusercontent.com/85772166/235047206-01cfd8c3-d65f-4bfa-ae47-ba0869a0c38e.png)

### Infoswe

Use the `infoswe` command when the target country is, `sweden`, and a loaded fund is issued by Avanza.

```console
/funds/country sweden/load F00000OW3P/infoswe
```

**The description below has been translated into English in this documentation because of the spelling checkers working in the repository are expecting English.**

```console
The fund Avanza 100 - SE0004841526 (F00000OW3P) was successfully loaded.

Swedish Description:

The fund is a mutual fund and aims to provide a positive return in the long term, taking into account the fund's risk level. The underlying funds must be cost-effective and have broad market exposure. The fund mainly invests in global, Swedish and growth market-oriented equity funds. The share exposed to shares in the fund is normally between 80 and 100 percent.

The fund is managed by:
        - Peter Stengård since 2012-10-19
        - Hampus Ernstsson since 2023-02-27
from Avanza.
Fund currency is SEK and it the fund started 2012-10-19. It is not a index fund. The fund manages 764173863.0 SEK. The standard deviation of the fund is 13.200000000000001 and the sharpe ratio is 1.08.
```
