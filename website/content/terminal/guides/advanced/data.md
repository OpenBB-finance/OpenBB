---
title: Importing and Exporting Data
sidebar_position: 2
description: The `OpenBBUserData` folder is where files are saved when they are created from within the OpenBB Terminal, like exports and generated reports. It is also where user-generated files are stored.
keywords: [export, import, data, excel, xlsx, csv, json, png, pdf, jpg, openbbuserdata, terminal, user, data, presets, screener, portfolio, styles, themes]
---
## The OpenBBUserData Folder

The `OpenBBUserData` folder's default location is the home of the system user account. By default this will be the following paths:
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:/Users/<YOUR_USERNAME>/OpenBBUserData`

Within the folder you can find files that you have exported as well as files that you wish to import directly into the OpenBB Terminal. For example, this could be an orderbook which you can store in `OpenBBUserData/portfolio/holdings`.

![OpenBBUserData Folder](https://user-images.githubusercontent.com/85772166/195742985-19f0e420-d8f7-4fea-a145-a0243b8f2ddc.png)

This folder contains all things user-created. For example:

 - Screener presets
 - Portfolio files
 - Exported files
 - Files to be imported by various functions
 - Styles and themes
 - Preferred data sources

**Note:** With a WSL-enabled Windows installation, this folder will be under the Linux partition

## Exporting Files

Within many of the functionalities, we offer the capability to export to Excel (xlsx and csv) or JSON. This can be demonstrated with the `--export` argument, e.g. if you wish to export to `xlsx` you would add `--export xlsx`. 

For example, if you wish to download market data you can do so from the stocks menu with the following:

```console
/stocks/load AAPL -s 2010-01-01 --export xlsx
```

This results in the following:

![Export Example](https://user-images.githubusercontent.com/46355364/214817681-fd5324c3-003c-45eb-adf4-96d5b41a3c02.png)

We also allow you to define a file name, for example for the same stock tickers, we can also add in the filename. This time, we export to `csv`.

```console
/stocks/load AAPL -s 2010-01-01 --export apple.csv
```

Which results in the following:

![Filename Example](https://user-images.githubusercontent.com/46355364/214818131-597b3bd0-9c66-43f1-bf0e-2c0a703e2645.png)

Lastly, when you select the `xlsx` option, you can also specify the sheet name with `--sheet-name` which allows multiple datasets to be send to the same Excel file. Using the same stock ticker, we can define the following. First, get market data from the `stocks` menu:

```console
/stocks/load AAPL -s 2010-01-01 --export apple.xlsx --sheet-name Market Data
```

Then enter the `fa` (Fundamental Analysis) menu and type:

:::note 
This requires an API key from FinancialModelingPrep. Please have a look [here](https://docs.openbb.co/terminal/quickstart/api-keys).
:::

**Income Statement:**

```console
income --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Income Statement
```

**Balance Sheet:**
```console
balance --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Balance Sheet
```

**Cash Flow Statement:**

```console
cash --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Cash Flow Statement
```

This generates a file for Apple with market data from 2010-01-01 until now and income, balance and cash flow statements over the last 10 years as seen in the image below.

![Sheet Name Example](https://user-images.githubusercontent.com/46355364/214824561-6eaf3a88-746a-4abc-91e1-420c9036c00d.png)

Next to that, we also allow exporting to images, this can be PNG, JPG, PDF and SVG. For example, using our `portfolio` menu we can export the charts to any type of format which again can be found within the `OpenBBUserData` folder.

![image](https://user-images.githubusercontent.com/46355364/214819518-cec40468-9019-440c-8bfe-7bcabc207578.png)

## Importing Data

Menus, such as [Econometrics](https://docs.openbb.co/terminal/guides/intros/econometrics) or [Portfolio](https://docs.openbb.co/terminal/guides/intros/portfolio), allow the user to import their own dataset. Files available to import will be included with the selections made available by auto-complete. In the Econometrics menu, this is activated after pressing the space bar, `load -f `

![Importing Data](https://user-images.githubusercontent.com/85772166/204921760-38742f6c-ec78-4009-9c23-54dcb0504524.png)

The Econometrics menu looks into the `exports` and `custom_imports/econometrics` folder. For the Portfolio functionalities the `portfolio` menu looks into the `portfolio/holdings` folder whereas the `portfolio/po` menu looks into the `portfolio/allocation` and `portfolio/optimization` folder for the `load` and `file` command respectively. Please make sure to read the relevant guides to understand how this works.

## Custom Path for OpenBBUserData folder

The location of this folder can be set by the user from the /settings menu. There should be no need to update paths in this menu unless the folders have been moved manually. If the location of the OpenBBUserData folder must be changed, it is best to move the entire existing folder to the new path. The path is then changed under the settings menu with:

```console
userdata --folder "/complete_path_to/OpenBBUserData"
```
