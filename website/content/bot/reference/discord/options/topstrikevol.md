---
title: topstrikevol
description: This documentation page explains how to use the topstrikevol command
  to retrieve the top option strike by volume for a specific stock ticker. It includes
  clear specifications of parameters and provides usage examples.
keywords:
- topstrikevol command
- stock ticker
- option strike by volume
- expiration date
- Python code usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: topstrikevol - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the top option strike by volume for a given security with the ability to add an expiration date for a more detailed breakdown.

### Usage

```python wordwrap
/op topstrikevol ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (optional) | True | None |


---

## Examples

```python wordwrap
/op topstrikevol ticker:AMD
```

---
