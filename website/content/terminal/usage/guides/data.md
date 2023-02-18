---
title: Exporting and Importing Datasets
sidebar_position: 3
description: The `OpenBBUserData` folder is where files are saved when they are created from within the OpenBB Terminal, like exports and generated reports. It is also where user-generated files are stored.
keywords: [export, import, data, excel, xlsx, csv, json, png, pdf, jpg, openbbuserdata, terminal, user, data, presets, screener, portfolio, styles, themes]
---

The OpenBB Terminal offers a variety of ways to export financial data. This can be through XLSX, CSV or JSON but also through PNG, JPG, PDF and SVG giving plenty of flexibility to export the data the way you desire.

## The OpenBBUserData Folder

The `OpenBBUserData` folder is where files are saved when they are created from within the OpenBB Terminal, like exports and generated reports. It is also where user-generated files are stored, such as:

- Screener presets
- Portfolio files
- Exported files
- Files to be imported by various functions
- Styles and themes

The folder's location is at the root of user account for the operating system.

- Linux: `~/home/<YOUR_USERNAME>/OpenBBUserData`
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:\Users\<YOUR_USERNAME>\OpenBBUserData`

**Note:** With a WSL-enabled Windows installation, this folder will be under the Linux partition

**Note:** With a WSL-enabled Windows installation, this folder will be under the Linux partition

## Exporting Files

Within many of the functionalities, we offer the capability to export to Excel (xlsx and csv) or JSON. This can be demonstrated with the `--export` argument, e.g. if you wish to export to `xlsx` you would add `--export xlsx`.

For example, if you wish to download market data you can do so from the stocks menu with the following:

```console
/economy/ycrv --help
```

```console
usage: ycrv [-d DATE] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [--raw]

Generate country yield curve. The yield curve shows the bond rates at different maturities.

options:
  -d DATE, --date DATE  Date to get data from FRED. If not supplied, the most recent entry will be used. (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  --raw                 Flag to display raw data (default: False)

For more information and examples, use 'about ycrv' to access the related guide.

```

For exporting data from tables, the valid output types are:

- CSV
- JSON
- XLSX

Images can be exported as:

- JPG
- PDF
- PNG
- SVG

Deploying the `--export` flag can include just the file type:

```console
/stocks/ $ load aapl --export csv
```

Then enter the `fa` (Fundamental Analysis) menu and copy and paste the code below. This requires an API key from FinancialModelingPrep which you can obtain for free. Please have a look [here](https://docs.openbb.co/terminal/quickstart/api-keys).


```console
income --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Income Statement
balance --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Balance Sheet
cash --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Cash Flow Statement
```

```console
Loading Daily data for AAPL with starting period 2020-02-13.
Saved file: /Users/danglewood/OpenBBUserData/exports/aapl_daily.csv
```

When `xlsx` is the file type, an additional argument for the sheet name is available. The purpose of this functionality is to export multiple items to the same spreadsheet; for example:

```console
/stocks/load aapl --export watchlist.xlsx --sheet-name AAPL
```

```console
Loading Daily data for AAPL with starting period 2020-02-13.
Saved file: /Users/danglewood/OpenBBUserData/exports/watchlist.xlsx
```

```console
/stocks/load msft --export watchlist.xlsx --sheet-name MSFT
```

```console
Loading Daily data for MSFT with starting period 2020-02-13.
Saved file: /Users/danglewood/OpenBBUserData/exports/watchlist.xlsx
```

![Exporting Data](exports1.png)

## Importing Data

Menus, such as [Econometrics](https://docs.openbb.co/terminal/usage/intros/econometrics) or [Portfolio](https://docs.openbb.co/terminal/usage/intros/portfolio), allow the user to import their own dataset. Files available to import will be included with the selections made available by auto-complete. In the Econometrics menu, this is activated after pressing the space bar, `load -f `

![Importing Data](https://user-images.githubusercontent.com/85772166/204921760-38742f6c-ec78-4009-9c23-54dcb0504524.png)

The Econometrics menu looks into the `exports` and `custom_imports/econometrics` folder. For the Portfolio functionalities the `portfolio` menu looks into the `portfolio/holdings` folder whereas the `portfolio/po` menu looks into the `portfolio/allocation` and `portfolio/optimization` folder for the `load` and `file` command respectively. Please make sure to read the relevant guides to understand how this works.

## Custom Path for OpenBBUserData Folder

The location of this folder can be set by the user from the /settings menu. There should be no need to update paths in this menu unless the folders have been moved manually. If the location of the OpenBBUserData folder must be changed, it is best to move the entire existing folder to the new path. The path is then changed under the settings menu with:

```console
userdata --folder "/complete_path_to/OpenBBUserData"
```
