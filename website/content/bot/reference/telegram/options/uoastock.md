---
title: uoastock
description: Learn how to use the command to fetch the 20-day average options volume
  by ticker using the /uoastock command, including special features and detailed usage
  examples.
keywords:
- uoastock command
- options volume
- average options volume
- 20-day average
- trading volume
- calls and puts
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: uoastock - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the 20-day average options volume by ticker. The volume is based on the total volume of all options traded in the given period of time, including calls and puts.

### Usage

```python wordwrap
/uoastock [price]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| price | Filter by stocks over a certain price | True | None |


---

## Examples

```
/uoastock
```
```
/uoastock 50
```
---
