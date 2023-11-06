---
title: mktcap
description: The mktcap page describes the usage and parameters of the market cap
  estimate over time. The source for this data is Yahoo Finance. A Python line command
  is used to fetch and display this information.
keywords:
- mktcap
- market cap estimate
- Yahoo Finance
- python commands
- financial data
- parameters
- starting date
- data visualisation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/fa/mktcap - Reference | OpenBB Terminal Docs" />

Market Cap estimate over time. [Source: Yahoo Finance]

### Usage

```python
mktcap [-s START]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| start | The starting date (format YYYY-MM-DD) of the market cap display | 2019-11-23 | True | None |

![gnus_mktcap](https://user-images.githubusercontent.com/25267873/156903038-46f46af1-68ca-435b-aed7-842da041864a.png)

---
