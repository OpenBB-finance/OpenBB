---
title: cpci
description: This page provides information on the usage and parameters of 'cpci',
  a tool for analyzing Companies per Country based on Industry and Market Cap. It
  helps users understand how to input parameters and what effect each one has on the
  output.
keywords:
- cpci
- companies per country
- industry
- market cap
- parameters
- usage
- data analysis
- raw data
- maximum number of countries to display
- minimum percentage to display country
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/sia/cpci - Reference | OpenBB Terminal Docs" />

Companies per Country based on Industry and Market Cap

### Usage

```python
cpci [-M MAX_COUNTRIES_TO_DISPLAY] [-m MIN_PCT_TO_DISPLAY_COUNTRY] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| max_countries_to_display | Maximum number of countries to display | 15 | True | None |
| min_pct_to_display_country | Minimum percentage to display country | 0.015 | True | None |
| raw | Output all raw data | False | True | None |

![CPCI](https://user-images.githubusercontent.com/46355364/153896041-d66b4002-554d-47af-91d8-9a79824a6ccd.png)

---
