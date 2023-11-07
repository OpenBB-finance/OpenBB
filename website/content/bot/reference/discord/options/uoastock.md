---
title: uoastock
description: The uoastock command retrieves the 20-day average options volume by ticker,
  including both calls and puts. This page provides instructions for its usage, including
  how to filter stocks by price.
keywords:
- uoastock command
- options volume by ticker
- 20-day average options volume
- commands for stocks
- trading commands
- stock price filtering
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: uoastock - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the 20-day average options volume by ticker. The volume is based on the total volume of all options traded in the given period of time, including calls and puts.

### Usage

```python wordwrap
/op uoastock [price]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| price | Filter by stocks over a certain price | True | None |


---

## Examples

```
/op uoastock
```

```
/op uoastock price:50
```

---
