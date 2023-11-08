---
title: view
description: Understand how to view available portfolios in various formats using
  the 'view' command. This page provides a comprehensive guide on the parameters used.
keywords:
- portfolio view
- load portfolios
- csv portfolio
- json portfolio
- xlsx portfolio
- format command
- parameters guide
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/portfolio_analysis/view - Reference | OpenBB Terminal Docs" />

Show available portfolios to load.

### Usage

```python
view [-format {csv,json,xlsx,all}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| file_format | Format of portfolios to view. 'csv' will show all csv files available, etc. | all | True | csv, json, xlsx, all |

---
