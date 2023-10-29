---
title: vol
description: The documentation explores the 'vol' command used to retrieve a chart
  of Options Volume by Strike for a specific ticker. Explains usage, parameters, and
  provides examples.
keywords:
- vol command
- Options Volume by Strike
- expiry
- stock ticker
- Expiration Date
- Market Analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: vol - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a chart of Options Volume by Strike for a specified ticker. This data can be broken down further by adding an expiration date for a more detailed breakdown.

### Usage

```python wordwrap
/vol ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (optional) | True | None |


---

## Examples

```
/vol AMD
```

```
/vol AMD 2022-07-29
```
---
