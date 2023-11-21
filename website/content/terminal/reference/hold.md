---
title: hold
description: Turn on figure holding
keywords:
- account
- hold
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="account /hold - Reference | OpenBB Terminal Docs" />

Turn on figure holding. This will stop showing images until hold off is run.

### Usage

```python wordwrap
hold [-o {on,off}] [-s] [--title TITLE [TITLE ...]]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| option | -o  --option |  | off | True | on, off |
| axes | -s  --sameaxis | Put plots on the same axis. Best when numbers are on similar scales | False | True | None |
| title | --title | When using hold off, this sets the title for the figure. |  | True | None |

---
