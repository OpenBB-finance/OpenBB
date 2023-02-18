---
title: Importing and Exporting Data
sidebar_position: 3
description: The `OpenBBUserData` folder is where files are saved when they are created from within the OpenBB Terminal, like exports and generated reports. It is also where user-generated files are stored.
keywords: [export, import, data, excel, xlsx, csv, json, png, pdf, jpg, openbbuserdata, terminal, user, data, presets, screener, portfolio, styles, themes]
---
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

## Exporting Files

Most Terminal functions have the ability to export results as a file to the `OpenBBUserData` folder. This can be confirmed by engaging the help dialogue.

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

```console
Loading Daily data for AAPL with starting period 2020-02-13.
Saved file: /Users/danglewood/OpenBBUserData/exports/20230217_204550_OpenBBTerminal_openbb_terminal_load_AAPL.csv
```

Or, the file can be named explicitly:

```console
/stocks/ $ load aapl --export aapl_daily.csv
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

