---
title: gacc
description: OpenBB Terminal Function
---

# gacc

Displays terra blockchain account growth history. [Source: https://fcd.terra.dev/swagger]

### Usage

```python
usage: gacc [-l LIMIT] [--cumulative] [-k {active,total}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of days to show | 90 | True | None |
| cumulative | Show cumulative or discrete values. For active accounts only discrete value are available | True | True | None |
| kind | Total account count or active account count. Default: total | total | True | active, total |
---

