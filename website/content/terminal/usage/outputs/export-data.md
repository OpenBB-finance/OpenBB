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

The OpenBB Terminal offers a variety of ways to export financial data. This can be to a text-based file - XLSX, CSV or JSON -  or as images - PNG, JPG, PDF and SVG.

To export as a spreadsheet, `xlsx`,  add `--export xlsx` to the  command.

```console
/stocks/load AAPL -s 2010-01-01 --export xlsx
```

Which creates:

![Export Example](https://user-images.githubusercontent.com/46355364/214817681-fd5324c3-003c-45eb-adf4-96d5b41a3c02.png)

## Specifying the Filename

Instead of the default filename, it can be specified. Exporting as a `csv` this time:

```console
/stocks/load AAPL -s 2010-01-01 --export apple.csv
```

![Filename Example](https://user-images.githubusercontent.com/46355364/214818131-597b3bd0-9c66-43f1-bf0e-2c0a703e2645.png)

## Specifying a Target Sheet Name

With the `xlsx` option, `--sheet-name`  allows multiple datasets to be saved to the same file. For example:

```console
/stocks/load AAPL -s 2010-01-01 --export apple.xlsx --sheet-name Market Data
```

Then enter the `fa` (Fundamental Analysis) menu.  Copy and paste the code below to follow along.  This requires an API key from FinancialModelingPrep which you can obtain for free. Please have a look [here](/terminal/usage/data/api-keys).

```console
fa
income --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Income Statement
balance --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Balance Sheet
cash --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Cash Flow Statement
```

This generates a file for `AAPL`, with market data from 2010-01-01 until now, as well as the  income, balance and cash flow statements from the last ten years.

![Sheet Name Example](https://user-images.githubusercontent.com/46355364/214824561-6eaf3a88-746a-4abc-91e1-420c9036c00d.png)

## Export Directly From Charts

See the [interactive charts](/terminal/usage/outputs/interactive-charts.md#export-tools) page for instructions.
