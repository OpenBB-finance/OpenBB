---
title: Importing and Exporting Data
sidebar_position: 3
---

## The OpenBBUserData Folder

The `OpenBBUserData` folder's default location is the home of the system user account. By default this will be the following paths:
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:/Users/<YOUR_USERNAME>/OpenBBUserData`

Within the folder you can find files that you have exported as well as files that you wish to import directly into the OpenBB Terminal. For example, this could be an orderbook which you can store in `OpenBBUserData/portfolio/holdings`.

![OpenBBUserData Folder](https://user-images.githubusercontent.com/85772166/195742985-19f0e420-d8f7-4fea-a145-a0243b8f2ddc.png "OpenBBUserData Folder")

This folder contains all things user-created. For example:

 - Screener presets
 - Portfolio files
 - Exported files
 - Files to be imported by various functions
 - Styles and themes
 - Preferred data sources

The location of this folder can be set by the user from the `/settings` menu. There should be no need to update paths in this menu unless the folders have been moved manually.

[The Settings Menu](https://user-images.githubusercontent.com/85772166/195736718-a1b821da-5977-437a-bd18-b44add2a29a2.png "The Settings Menu")

## Exporting Files

If the location of the OpenBBUserData folder must be changed, it is best to move the entire existing folder to the new path. The path is then changed under the settings menu with:

```console
userdata --folder /path_to/OpenBBUserData
```

The types of files which can be exported from tables and raw data are:

- CSV
- JSON
- XLSX

It is optional to name the file; the minimum requirement is the file type.

```console
/stocks/load CHWY -s 2019-06-01 --export chwy_ohlc.csv
```

![Screenshot 2022-11-30 at 2 10 22 PM](https://user-images.githubusercontent.com/85772166/204919033-d6d5632a-c6ce-42cf-a038-b93d579e38d4.png)

```console
Saved file: /Users/{username}/OpenBBUserData/exports/chwy_ohlc.csv
```

The types of image files charts can be exported as are:

- PNG
- JPG
- PDG
- SVG

If no file name is specified, the file will be automatically named starting with the date and time generated.

```console
candle --ma 20,50,150 -t --export svg

Saved file: /Users/{username}/OpenBBUserData/exports/20221130_141425_stocks_CHWY.svg
```

![Screenshot 2022-11-30 at 2 16 19 PM](https://user-images.githubusercontent.com/85772166/204919882-3cf7ba23-7fba-4b9d-b278-25752efab0c6.png)

Every function capable of exporting content will work in exactly the same manner. Print the `--help` dialogue for any function to see the options available.

```console
(🦋) /stocks/options/ $ chains --help

usage: chains [-c] [-p] [-m MIN_SP] [-M MAX_SP] [-d TO_DISPLAY] [-h] [--export EXPORT] [--source {YahooFinance,Tradier,Nasdaq}]

Display option chains

options:
  -c, --calls           Flag to show calls only (default: False)
  -p, --puts            Flag to show puts only (default: False)
  -m MIN_SP, --min MIN_SP
                        minimum strike price to consider. (default: -1)
  -M MAX_SP, --max MAX_SP
                        maximum strike price to consider. (default: -1)
  -d TO_DISPLAY, --display TO_DISPLAY
                        (tradier only) Columns to look at. Columns can be: bid, ask, strike, bidsize, asksize, volume, open_interest, delta, gamma, theta, vega, ask_iv, bid_iv,
                        mid_iv. E.g. 'bid,ask,strike' (default: ['mid_iv', 'vega', 'delta', 'gamma', 'theta', 'volume', 'open_interest', 'bid', 'ask'])
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {YahooFinance,Tradier,Nasdaq}
                        Data source to select from (default: YahooFinance)

For more information and examples, use 'about chains' to access the related guide.

(🦋) /stocks/options/ $
```

## Importing Data

Menus, such as [Econometrics](https://docs.openbb.co/terminal/guides/intros/econometrics) or [Portfolio](https://docs.openbb.co/terminal/guides/intros/portfolio), allow the user to import their own dataset. Files available to import will be included with the selections made available by auto-complete. In the Econometrics menu, this is activated after pressing the space bar, `load -f `

![Importing Data](https://user-images.githubusercontent.com/85772166/204921760-38742f6c-ec78-4009-9c23-54dcb0504524.png "Importing Data")

As illustrated above, the exported file that was created in the previous example is ready to be loaded into the Econometrics menu. Use the arrow keys to scroll the files available to import.
