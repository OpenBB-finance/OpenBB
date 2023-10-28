---
title: hsi
description: This documentation helps understand the 'hsi' command, which retrieves
  the top high short interest stocks over a 20% ratio, a crucial tool for investors
  looking for possible short squeeze potential.
keywords:
- hsi command
- high short interest stocks
- short squeeze potential
- stock investing
- trading tools
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="short_data: hsi - Discord Reference | OpenBB Bot Docs" />

This command retrieves the top high short interest stocks over a 20% ratio. This information can let an investor identify possible short squeeze potential.

### Usage

```python wordwrap
/sh hsi [num]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| num | Number of top stocks to print | True | None |


---

## Examples

```
/sh hsi
```
```
/sh hsi num:4
```

---
