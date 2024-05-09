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

:::note
Note that the commands and menus may vary.
:::

To export as a spreadsheet, `xlsx`,  add `--export xlsx` to the  command.

```console

```

Which creates:


## Specifying the Filename

Instead of the default filename, it can be specified. Exporting as a `csv` this time:

```console

```



## Specifying a Target Sheet Name

With the `xlsx` option, `--sheet-name`  allows multiple datasets to be saved to the same file. For example:

```console

```

```console

```

This generates a file for `AAPL`, with market data from 2010-01-01 until now, as well as the  income, balance and cash flow statements from the last ten years.


## Export Directly From Charts

See the [interactive charts](interactive-charts.md#export-tools) page for instructions.
