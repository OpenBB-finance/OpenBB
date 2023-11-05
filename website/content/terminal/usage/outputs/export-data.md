---
title: Export data
sidebar_position: 3
description: Learn how to export financial data through the OpenBB Terminal in different
  formats like XLSX, CSV, JSON, PNG, JPG, PDF, and SVG. Also learn to specify filename,
  sheet name, and export directly into a chart.
keywords:
- financial data export
- XLSX
- CSV
- JSON
- PNG
- JPG
- PDF
- SVG
- filename specification
- sheet name specification
- export to chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Export data - Outputs - Usage | OpenBB Terminal Docs" />

The OpenBB Terminal offers a variety of ways to export financial data. This can be through XLSX, CSV or JSON but also through PNG, JPG, PDF and SVG giving plenty of flexibility to export the data the way you desire.

This can be demonstrated with the `--export` argument, e.g. if you wish to export to `xlsx` you would add `--export xlsx`.

For example, if you wish to download market data you can do so from the stocks menu with the following:

```console
(🦋) /stocks/ $ load AAPL -s 2010-01-01 --export xlsx
```

This results in the following:

![Export Example](https://user-images.githubusercontent.com/46355364/214817681-fd5324c3-003c-45eb-adf4-96d5b41a3c02.png)

## Specifying filename

We also allow you to define a file name, for example for the same stock tickers, we can also add in the filename. This time, we export to `csv`.

```console
(🦋) /stocks/ $ load AAPL -s 2010-01-01 --export apple.csv
```

Which results in the following:

![Filename Example](https://user-images.githubusercontent.com/46355364/214818131-597b3bd0-9c66-43f1-bf0e-2c0a703e2645.png)

## Specifying sheet name when XLSX

When you select the `xlsx` option, you can also specify the sheet name with `--sheet-name` which allows multiple datasets to be grouped to the same Excel file. Using the same stock ticker, we can define the following. First, get market data from the `stocks` menu:

```console
(🦋) /stocks/ $ load AAPL -s 2010-01-01 --export apple.xlsx --sheet-name Market Data
```

Then enter the `fa` (Fundamental Analysis) menu and copy and paste the code below. This requires an API key from FinancialModelingPrep which you can obtain for free. Please have a look [here](/terminal/usage/data/api-keys).

```console
(🦋) /stocks/fa/ $ income --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Income Statement
(🦋) /stocks/fa/ $ balance --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Balance Sheet
(🦋) /stocks/fa/ $ cash --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Cash Flow Statement
```

This generates a file for Apple with market data from 2010-01-01 until now and income, balance and cash flow statements over the last 10 years as seen in the image below.

![Sheet Name Example](https://user-images.githubusercontent.com/46355364/214824561-6eaf3a88-746a-4abc-91e1-420c9036c00d.png)

## Export directly into chart

We allow exporting to images, this can be PNG, JPG, PDF and SVG. For example, using our `portfolio` menu we can export the charts to any type of format which again can be found within the `OpenBBUserData` folder.

![image](https://user-images.githubusercontent.com/46355364/214819518-cec40468-9019-440c-8bfe-7bcabc207578.png)
