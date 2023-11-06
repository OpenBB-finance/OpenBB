---
title: revrepo
description: Revrepo is a command allowing the user to retrieve Reverse Repo data
  statistics over specified days. It gives details such as Reverse Repo total, number
  of parties, average and variations.
keywords:
- revrepo command
- Reverse Repo data
- data retrieval
- data statistics
- data averaging
- data difference
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy: revrepo - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve Reverse Repo data for a default period of 35 days. This data includes information such as the total amount of Reverse Repo, the number of parties, the average, and difference.

### Usage

```python wordwrap
/revrepo [days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to display. Default: 50 | True | None |


---

## Examples

```
/revrepo days:35
```

```
/revrepo
```

---
