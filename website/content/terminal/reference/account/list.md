---
title: list
description: List routines available in the cloud
keywords:
- account
- list
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="account /list - Reference | OpenBB Terminal Docs" />

List routines available in the cloud.

### Usage

```python wordwrap
list [-t {default,personal}] [-p PAGE] [-s SIZE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| type | -t  --type | The type of routines to list. | personal | True | default, personal |
| page | -p  --page | The page number. | 1 | True | None |
| size | -s  --size | The number of results per page. | 10 | True | None |

---
