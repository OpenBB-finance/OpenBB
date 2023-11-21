---
title: shrs
description: This page provides information on how to print Major, institutional and
  mutualfunds shareholders using the 'shrs' command in Python. The data source for
  this information is Yahoo Finance.
keywords:
- shrs
- major shareholders
- institutional shareholders
- mutualfunds shareholders
- Yahoo Finance
- shareholder table
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/shrs - Reference | OpenBB Terminal Docs" />

Print Major, institutional and mutualfunds shareholders. [Source: Yahoo Finance]

### Usage

```python wordwrap
shrs [-t TICKER] [--holder {major,institutional,mutualfund}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to analyze | None | True | None |
| holder | --holder | Table of holders to get | institutional | True | major, institutional, mutualfund |

---
