---
title: export
description: Page providing a guide on how to use the 'export' feature of a data-focused
  application, which allows exporting datasets to Excel or CSV formats.
keywords:
- export data guide
- export dataset
- export to Excel
- export to CSV
- data-focused application
- data exporting
- dataset handling
- dataset operation
- automation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast /export - Reference | OpenBB Terminal Docs" />

Export dataset to Excel

### Usage

```python
export [-t {xlsx,csv}] [-d {}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| type | The file type you wish to export to | xlsx | True | xlsx, csv |
| target_dataset | The name of the dataset you want to select | None | True | None |


---

## Examples

```python
(🦋) /forecast/ $ load aapl

(🦋) /forecast/ $ ema aapl
Successfully added 'EMA_10' to 'aapl' dataset

(🦋) /forecast/ $ export aapl
Saved file: .../OpenBBTerminal/exports/forecast/aapl_20220711_151219.xlsx
```
---
