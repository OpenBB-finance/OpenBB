---
title: bigprints
description: Bigprints command provides a comprehensive view of the biggest dark pool
  and block trades over a specified number of days, offering insights into the market
  activity over that period.
keywords:
- bigprints
- dark pool trades
- block trades
- /dp bigprints days
- market activity
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: bigprints - Discord Reference | OpenBB Bot Docs" />

This command will retrieve the largest combination of dark pool and block trades over a specified amount of days. It will provide a comprehensive view of the biggest dark pool and block trades over the specified number of days and give the user an idea of the market activity over that period.

### Usage

```python wordwrap
/dp bigprints days
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |


---

## Examples

```
/dp bigprints days:6
```
---
