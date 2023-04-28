---
title: Mutual Funds
keywords: [mutual funds, funds, morningstar, morning star, blackrock, vanguard, countries, global, search, holdings]
description: An introduction to the Mutual Funds menu - search and analyze the global mutual funds universe by country.
---
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

`<HeadTitle title="Mutual Funds - Terminal | OpenBB Docs" />`

## Overview

The Mutual Funds menu provides a global view of the mutual funds universe.  Enter the menu by typing, `/funds`.

## The Mutual Funds Menu

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

### Select a Country

To use the menu, a country must be selected, and the default is `united_states`.  To select a different one, type `country`, followed by the `spacebar`.  This will bring up a list that can be picked from using the up/down arrow keys.

![Mutual Funds Menu](mutualfunds1.png)

Refresh the screen, by typing `?`, to verify the choice has been made.

![Selecting a Country](mutualfunds2.png)

### Search

The most effective way to sift through a vast quantity of funds is to use the `search` function broadly, then narrow the focus using the built-in filters on the displayed table.  In the example below, there are 668 results returned for `RBC` and `Canada`.  Filtering for money market funds gets it down to only ten funds.

```console
/funds/country canada/search rbc --limit 1000
```

![Search Funds](mutualfunds3.png)

### Load

A mutual fund is loaded by using the ID number, which is the column labeled, `SECID`, on the left side of the table.

```console
load F0CAN05LTL
```

```console
The fund RBC Premium Money Market Fund A - 52.8.RBF447 (F0CAN05LTL) was successfully loaded.
```

## Examples

### holdings

With a fund loaded, get the weighting of the portfolio using the `holdings` command.

:::note
The holdings data returned will vary by country.  Some will only return the top ten, while others will publish the entire portfolio.
:::

```console
/funds/country canada/load F00000U48G/holdings
```

![Holdings](mutualfunds4.png)

In contrast, the iShares Developed Real Estate Index Fund Investor A Shares, from the United States, returns 449 results.

```console
funds/country united_states/load F00000VW8Z/holdings
```

![Holdings](mutualfunds5.png)

### plot

Plot historical performance of the fund against its benchmark index or the broad category.

```console
/funds/country united_states/load F00000VW8Z --start 2000-01-01/plot -c both
```

![Plot Performance](mutualfunds6.png)

### sector

The `sector` command displays a breakdown of sector weightings, compared against the benchmark index and broad category.

```console
/funds/country united_states/load F00000ZAFI/sector
```

### infoswe

Use the `infoswe` command when the target country is, `sweden`, and a loaded fund is issued by Avanza.

```console
/funds/country sweden/load F00000OW3P/infoswe
```

```console
The fund Avanza 100 - SE0004841526 (F00000OW3P) was successfully loaded.

Swedish Description:

Fonden är en fondandelsfond och har som mål att ge en positiv avkastning på lång sikt med hänsyn tagen till fondens risknivå. De underliggande fonderna skall vara kostnadseffektiva och ha en bred marknadsexponering. Fonden placerar främst i globala, svenska och tillväxtmarknadsorienterade aktiefonder. Den aktieexponerade andelen i fonden ligger normalt mellan 80 och 100 procent.

The fund is managed by:
        - Peter Stengård since 2012-10-19
        - Hampus Ernstsson since 2023-02-27
from Avanza.
Fund currency is SEK and it the fund started 2012-10-19. It is not a index fund. The fund manages 764173863.0 SEK. The standard deviation of the fund is 13.200000000000001 and the sharpe ratio is 1.08.
```
