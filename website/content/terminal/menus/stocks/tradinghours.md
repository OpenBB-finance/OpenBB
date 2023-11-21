---
title: Trading Hours
description: This introduces the Trading Hours sub-menu, within the Stocks menu of the OpenBB Terminal.  Use these commands to check the operating status of markets globally.
keywords:
- trading hours
- trading
- market hours
- open
- close
- bursa
- pandasmarketcalendars
- status
- holidays
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Trading Hours - Stocks - Menus | OpenBB Terminal Docs" />

This set of features is for checking the operating status of markets globally.

## Usage

Enter, `th`, from the [`/stocks/`](/terminal/menus/stocks) menu. Or, with the absolute path:

```console
/stocks/th
```

![Screenshot 2023-11-01 at 2 21 56 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/66fe02c2-22d1-4ce3-a410-7df6f7f4defa)

### Exchange

Get the regular market hours and status of a particular exchange.

```console
/stocks/th/exchange -n ASX
```

|                       | ASX                                                                                               |
|:----------------------|:--------------------------------------------------------------------------------------------------|
| name                  | Australian Securities Exchange                                                                    |
| short_name            | AX                                                                                                |
| website               | https://www2.asx.com.au/markets/market-resources/trading-hours-calendar/cash-market-trading-hours |
| market_open           | 10:00:00                                                                                          |
| market_close          | 16:00:00                                                                                          |
| lunchbreak_start      |                                                                                                   |
| lunchbreak_end        |                                                                                                   |
| opening_auction_start | 07:00:00                                                                                          |
| opening_auction_end   | 10:00:00                                                                                          |
| closing_auction_start | 16:10:00                                                                                          |
| closing_auction_end   | 16:12:00                                                                                          |
| timezone              | Australia/Sydney                                                                                  |
| flag                  | 🇦🇺                                                                                                |
| open                  | False                                                                                             |
