---
title: history
description: This page displays details on how to fetch account history using python
  command. It includes a list of parameters like coin symbol, account ID, and limit
  parameter with their optional values and defaults.
keywords:
- account history
- usage
- parameters
- python command
- coin symbol
- account id
- limit parameter
- BTC
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /brokers/coinbase/history - Reference | OpenBB Terminal Docs" />

Display account history

### Usage

```python wordwrap
history [-a ACCOUNT] [-l LIMIT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| account | -a  --acc | Symbol of coin of account or id | BTC | True | None |
| limit | -l  --limit | Limit parameter. | 20 | True | None |

---
