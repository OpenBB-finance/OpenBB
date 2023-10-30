---
title: group
description: This page documents the 'group' function in python for displaying a portfolio
  group by a given column. This includes an optional allocation column addition to
  the dataframe, with usage and parameter details provided.
keywords:
- Group Function
- Portfolio Group
- Allocation Column
- Marketing Parameters
- Dataframe Modification
- Group By Ticker
- Python Command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/portfolio_analysis/group - Reference | OpenBB Terminal Docs" />

Displays portfolio grouped by a given column

### Usage

```python
group [-g {}] [-a]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| group | Column to group by | Ticker | True | Index([], dtype='object') |
| allocation | Add allocation column in % to dataframe | False | True | None |

---
