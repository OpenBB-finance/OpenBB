---
title: exe
description: Run a notebook from a url that contains the ipynb contents
keywords:
- reports
- exe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="reports /exe - Reference | OpenBB Terminal Docs" />

Run a notebook from a url that contains the ipynb contents

### Usage

```python wordwrap
exe -u URL [-p PARAMETERS [PARAMETERS ...]]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| url | -u  --url | The url of the file to be loaded | None | False | None |
| parameters | -p  --parameters | Report parameters with format 'name:value'. | None | True | None |

---
