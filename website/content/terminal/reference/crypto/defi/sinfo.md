---
title: sinfo
description: Learn how to use sinfo tool to display staking info of a Terra address.
  Provides usage information and parameter details.
keywords:
- sinfo tool
- Terra address
- staking info
- parameters
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/defi/sinfo - Reference | OpenBB Terminal Docs" />

Displays staking info of a certain terra address. [Source: https://fcd.terra.dev/swagger]

### Usage

```python
sinfo -a ADDRESS [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| address | Terra address. Valid terra addresses start with 'terra' | None | False | None |
| limit | Number of delegations | 10 | True | None |

---
