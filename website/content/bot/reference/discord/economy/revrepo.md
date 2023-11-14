---
title: revrepo
description: On this page, you can understand how to use the '/econ revrepo' command
  to retrieve Reverse Repo data with flexibility on the number of days, specifically
  catering to your needs.
keywords:
- RevRepo
- /econ revrepo
- Retrieving Reverse Repo data
- Command Usage
- Parameters
- Examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy: revrepo - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve Reverse Repo data for a default period of 35 days. This data includes information such as the total amount of Reverse Repo, the number of parties, the average, and difference.

### Usage

```python wordwrap
/econ revrepo [days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to display. Default: 50 | True | None |


---

## Examples

```
/econ revrepo days:35
```

```
/econ revrepo
```
---
