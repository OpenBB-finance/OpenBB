---
title: topstrikevol
description: This page provides information on the 'topstrikevol' command allowing
  users to retrieve the top option strike by volume for a given security. It includes
  the option to add an expiration date for a more detailed breakdown.
keywords:
- topstrikevol
- option strike
- stock ticker
- expiration date
- security
- volume
- /topstrikevol AMD
- detail breakdown
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: topstrikevol - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the top option strike by volume for a given security with the ability to add an expiration date for a more detailed breakdown.

### Usage

```python wordwrap
/topstrikevol ticker [expiry]
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
/topstrikevol AMD
```
---
