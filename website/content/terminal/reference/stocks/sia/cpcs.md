---
title: cpcs
description: CPCS is a powerful tool that allows users to view company distribution
  based on various parameters like sector, market cap and more. It offers customizable
  options to control the data display.
keywords:
- CPCS
- Company distribution by Country, Sector and Market Cap
- Country distribution data
- Sector distribution data
- Market cap data
- Data visualization
- Data customization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/sia/cpcs - Reference | OpenBB Terminal Docs" />

Companies per Country based on Sector and Market Cap

### Usage

```python
cpcs [-M MAX_COUNTRIES_TO_DISPLAY] [-m MIN_PCT_TO_DISPLAY_COUNTRY] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| max_countries_to_display | Maximum number of countries to display | 15 | True | None |
| min_pct_to_display_country | Minimum percentage to display country | 0.015 | True | None |
| raw | Output all raw data | False | True | None |

![CPCS](https://user-images.githubusercontent.com/46355364/153896494-5c0c9c00-aa2a-45cb-8a93-cfaa908b35df.png)

---
