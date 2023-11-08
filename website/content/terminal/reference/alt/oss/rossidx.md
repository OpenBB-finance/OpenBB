---
title: rossidx
description: This page provides detailed instructions on how to use the rossidx command
  in Python to sort and display information about startups from the Ross Index. Users
  can sort by various criteria (e.g. GitHub Stars, Company, Country), display charts,
  and set the chart type to 'stars' or 'forks'.
keywords:
- rossidx
- startups
- chart
- stars
- forks
- sorting
- growth chart
- GitHub
- company
- country
- city
- founded
- raised money
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt/oss/rossidx - Reference | OpenBB Terminal Docs" />

Display list of startups from ross index [Source: https://runacap.com/] Use --chart to display chart and -t {stars,forks} to set chart type

### Usage

```python
rossidx [-s SORTBY [SORTBY ...]] [-r] [-c] [-g] [-t {stars,forks}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| sortby | Sort startups by column | Stars AGR [%] | True | GitHub, Company, Country, City, Founded, Raised [$M], Stars, Forks, Stars AGR [%], Forks AGR [%] |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| show_chart | Flag to show chart | False | True | None |
| show_growth | Flag to show growth chart | False | True | None |
| chart_type | Chart type: {stars, forks} | stars | True | stars, forks |

---
