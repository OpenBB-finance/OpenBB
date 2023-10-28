---
title: vol
description: This page provides information on using the 'vol' command in retrieving
  Options Volume by Strike for a specified ticker. It also includes usage examples
  and how to add an expiration date for more specific data.
keywords:
- Options Volume
- Stock Ticker
- Expiration Date
- Command 'vol'
- Retrieve Ticker Data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: vol - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a chart of Options Volume by Strike for a specified ticker. This data can be broken down further by adding an expiration date for a more detailed breakdown.

### Usage

```python wordwrap
/op vol ticker [expiry]
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
/op vol ticker:AMD
```

```
/op vol ticker:AMD expiry:2022-07-29
```

---
