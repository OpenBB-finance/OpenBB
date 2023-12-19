---
title: Discovery
description: This documentation page is an introduction to the Discovery sub-menu, within Stocks, of the OpenBB Terminal. Functions in this menu include stock lists, calendars, trending moves and an S&P 500 heatmap.
keywords:
- Stocks Discovery
- following trends
- current events
- gainers
- losers
- most active
- calendar
- dividend
- earnings
- Seeking Alpha news
- S&P 500
- heatmap
- ark
- penny stocks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Discovery - Stocks - Menus | OpenBB Terminal Docs" />

The Discovery menu has functions for upcoming corporate calendar events and stock lists.  Commands in this menu are not ticker-specific and do not require a symbol to be loaded.

## Usage

Enter the Discovery menu from the `/stocks` menu by typing `disc` into the Terminal, or through the absolute path:

```console
/stocks/disc
```

![Screenshot 2023-11-01 at 9 34 25 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/94d61da1-a04e-4d03-87bc-1d95443dc851)


### DIVCAL

The dividend calendar will display single dates, and does not provide historical data.  The `date` will be with respect to the ex-dividend date.

```console
/stocks/disc/divcal
```

![Screenshot 2023-11-01 at 9 43 46 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/d99e5973-6a49-441d-bb4d-5a60139f7334)

### Upcoming


Check the upcoming earnings schedule using, `upcoming`.  The `limit` parameter represents the number of days to look ahead.

```console
/stocks/disc/upcoming --start 2023-11-02 --limit 5
```

![Screenshot 2023-11-01 at 9 47 27 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/99fc4bec-7ffe-4b98-bf98-e791c81aab3a)


### Filings

The `filings` command is the RSS feed of latest filings to the SEC.  The results are printed directly to the screen, or they can be exported with the `--export` command.  To see all the entries from today, add `--today` to the command.  By default, the five most-recent documents will be displayed.

```console
/stocks/disc/filings
```

```console
Timestamp: 2023-11-01 12:44:49  US/Eastern
Ticker: NVO
CIK: 353278
Form Type: 6-K
6-K - NOVO NORDISK A S (0000353278) (Filer)
https://www.sec.gov/Archives/edgar/data/353278/000117184323006584/0001171843-23-006584-index.htm

Timestamp: 2023-11-01 12:44:49  US/Eastern
Ticker: NONOF
CIK: 353278
Form Type: 6-K
6-K - NOVO NORDISK A S (0000353278) (Filer)
https://www.sec.gov/Archives/edgar/data/353278/000117184323006584/0001171843-23-006584-index.htm

Timestamp: 2023-11-01 12:38:55  US/Eastern
Ticker: None
CIK: 1715593
Form Type: 13F-HR
13F-HR - Csenge Advisory Group (0001715593) (Filer)
https://www.sec.gov/Archives/edgar/data/1715593/000171559323000007/0001715593-23-000007-index.htm

Timestamp: 2023-11-01 12:36:58  US/Eastern
Ticker: HMY
CIK: 1023514
Form Type: 6-K
6-K - HARMONY GOLD MINING CO LTD (0001023514) (Filer)
https://www.sec.gov/Archives/edgar/data/1023514/000162828023035854/0001628280-23-035854-index.htm

Timestamp: 2023-11-01 12:36:58  US/Eastern
Ticker: HGMCF
CIK: 1023514
Form Type: 6-K
6-K - HARMONY GOLD MINING CO LTD (0001023514) (Filer)
https://www.sec.gov/Archives/edgar/data/1023514/000162828023035854/0001628280-23-035854-index.htm
```
