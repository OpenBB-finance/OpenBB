---
title: compfees
description: Learn how to use the compfees command to retrieve Protocol fees with
  step-by-step examples. The command caters to various projects including btc, eth,
  doge, etc.
keywords:
- compfees
- Protocol fees
- btc
- eth
- doge
- projects
- /crypto command
- crypto
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: compfees - Discord Reference | OpenBB Bot Docs" />

This command allows users to retrieve the Protocol fees over time for the given project.

### Usage

```python wordwrap
/crypto compfees projects
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| projects | Comma separated list of protocols (e.g., btc,eth) | False | None |


---

## Examples

```
/crypto compfees projects: doge
```

```
/crypto compfees projects: btc,eth
```

---
