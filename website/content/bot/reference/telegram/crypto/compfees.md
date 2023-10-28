---
title: compfees
description: Learn how to retrieve the Protocol fees over time for your projects using
  the compfees command. Understand its usage, parameters, and see examples.
keywords:
- compfees command
- Protocol fees
- btc
- eth
- usage
- parameters
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: compfees - Telegram Reference | OpenBB Bot Docs" />

This command allows users to retrieve the Protocol fees over time for the given project.

### Usage

```python wordwrap
/compfees projects
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| projects | Comma separated list of protocols (e.g., btc,eth) | False | None |


---

## Examples

```
/compfees doge
```

```
/compfees projects: btc,eth
```

---
