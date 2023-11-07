---
title: cpic
description: This is a documentation page for CPIC, a tool that displays companies
  per industry based on country and market cap. It allows users to adjust parameters
  such as the maximum number of industries to display and the minimum percentage to
  display an industry.
keywords:
- CPIC
- companies per industry
- country
- market cap
- maximum industries to display
- minimum percentage to display industry
- raw data
- business tool
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/sia/cpic - Reference | OpenBB Terminal Docs" />

Companies per Industry based on Country and Market Cap

### Usage

```python
cpic [-M MAX_INDUSTRIES_TO_DISPLAY] [-m MIN_PCT_TO_DISPLAY_INDUSTRY] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| max_industries_to_display | Maximum number of industries to display | 15 | True | None |
| min_pct_to_display_industry | Minimum percentage to display industry | 0.015 | True | None |
| raw | Output all raw data | False | True | None |

![CPIC](https://user-images.githubusercontent.com/46355364/153896804-87ae9eb1-b252-4c8f-a089-b653920372fc.png)

---
