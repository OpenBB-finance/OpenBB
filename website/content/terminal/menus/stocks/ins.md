---
title: Insider Trading
description: This documentation page features the insider trading menu which gives stock screener for SEC Form 4 filings and researching individual companies for executive and director transactions
keywords:
- SEC form 4 filings
- insider
- insider trading
- insider activity
- stock screener
- reporting
- transactions
- trade type
- trade date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Insider Trading - Stocks - Menus | OpenBB Terminal Docs" />

The Insider Trading menu provides screener-like functions for SEC Form 4 filings, or for researching individual companies with executive and director transactions. The features in this menu function only for companies registered with the SEC, that also trade in public markets.

## Usage

Navigate to the Insider Trading submenu from the `stocks` menu by typing `ins` and pressing `enter`.

![Screenshot 2023-11-01 at 12 46 13 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/6e79a43c-f401-4519-a777-415c64581ddd)

The menu can be entered with its absolute path:

```console
/stocks/ins
```

The Insider Trading menu contains three groups of functions:
- Screening: use presets to filter companies.
- Scanning: scan the latest transactions in the market.
- Researching: lookup individual companies.


### Screening

Screening in this sub-menu uses a similar process to the [Stocks Screener](/terminal/menus/stocks/screener.md).  This [template](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_terminal/miscellaneous/stocks/insider/template.ini) file is a starting point, and describes how to configurea preset for use.  Follow the formatting instructions in the comments of the template file, then place this file in the OpenBBUserData folder: `~/OpenBBUserData/presets/stocks/insider`.  Files placed in this folder will be recognized by the auto complete choices on next launch.  Changes to the settings (without altering the filename) will be reflected when the preset  is run, restarting the Terminal is not required.

#### Set

Set the preset to use by typing, `set -p`, and then the spacebar will activated the choices from auto complete.

![Screenshot 2023-11-01 at 1 17 55 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/6eaea63a-bfff-47c3-be79-4a7df490f5c8)

#### Filter

The `filter` command runs the screen.  Use the `--limit` parameter to increase the number of results returned.

```console
set -p Insurance-Agents
filter
```

```console
A: Amended filing
D: Derivative transaction in filing (usually option exercise)
M: Multiple transactions in filing; earliest reported transaction date & weighted average transaction price
P - Purchase: Purchase of securities on an exchange or from another person
S - Sale: Sale of securities on an exchange or to another person
S - Sale+OE: Sale of securities on an exchange or to another person (after option exercise)
```

![Screenshot 2023-11-01 at 1 23 29 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/4793ef66-0e4e-46bd-886f-f6615058b4f6)

### Scanning

The commands grouped by both "Last Insiders" and "Top Insiders" filter market-wide by the description printed on the menu.

#### toppw

`toppw` returns the top officer purchases during the past week.

```console
/stocks/ins/toppw
```

![Screenshot 2023-11-01 at 1 28 32 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/2caf277e-75e3-4f6a-90a5-0f92b449062c)

### Researching

The three functions grouped at the bottom are activated when the Insider Trading menu is entered with a ticker symbol loaded from the `/stocks` menu.

#### stats

The `stats` command shows the insider activity for a ticker.

```console
/stocks/load rivn/ins/stats
```

![Screenshot 2023-11-01 at 1 41 29 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/6028b97e-bea4-4d4e-85e1-3512c8004675)
