---
title: run
description: Learn how to effectively run a notebook from a specific location using
  various parameters. This page also provides details about certain parameters such
  as report parameters and the file to be loaded.
keywords:
- run notebook
- usage
- parameters
- file loading
- report parameters
- OpenBBUserData
- custom reports
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="reports /run - Reference | OpenBB Terminal Docs" />

Run a notebook from this folder: '/home/runner/OpenBBUserData/reports/custom reports'.

### Usage

```python
run -f {} [-p PARAMETERS [PARAMETERS ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| file | The file to be loaded | None | False | None |
| parameters | Report parameters with format 'name:value'. | None | True | None |

---
