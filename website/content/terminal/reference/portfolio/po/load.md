---
title: load
description: This page provides documentation on how to load a file of stocks tickers
  with optional categories using Python. It contains information on the parameters
  and file options that are available.
keywords:
- Load
- Stocks
- Tickers
- File
- Categories
- Parameters
- Allocation
- OpenBB_Parameters_Template_v1.0.0.xlsx
- defaults.ini
- dany.ini
- james.ini
- example.ini
- dd.ini
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /po/load - Reference | OpenBB Terminal Docs" />

Load file of stocks tickers with optional categories

### Usage

```python wordwrap
load [-f {} [{} ...]] [-e]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| file | -f  --file | Allocation file to be used | None | True | File in `EXPORTS` or `CUSTOM_IMPORTS` directories |
| example | -e  --example | Run an example allocation file to understand how the portfolio optimization menu can be used. | False | True | None |

---
