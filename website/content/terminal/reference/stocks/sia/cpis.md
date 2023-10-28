---
title: cpis
description: This documentation pages describes the cpis command which allows users to visualize companies per industry based on sector and market cap
keywords:
- sector
- industry
- market cap
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/sia/cpis - Reference | OpenBB Terminal Docs" />

Companies per Industry based on Sector and Market Cap

### Usage

```python
cpis [-M MAX_INDUSTRIES_TO_DISPLAY] [-m MIN_PCT_TO_DISPLAY_INDUSTRY] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| max_industries_to_display | Maximum number of industries to display | 15 | True | None |
| min_pct_to_display_industry | Minimum percentage to display industry | 0.015 | True | None |
| raw | Output all raw data | False | True | None |

![CPIS](https://user-images.githubusercontent.com/46355364/153896896-9e102f13-28ee-4abf-9277-a7c2ecfd08ab.png)

---
