---
title: upload
description: Upload a routine to the cloud
keywords:
- account
- upload
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="account /upload - Reference | OpenBB Terminal Docs" />

Upload a routine to the cloud.

### Usage

```python wordwrap
upload [-f FILE [FILE ...]] [-d DESCRIPTION [DESCRIPTION ...]] [-n NAME [NAME ...]] [-t TAGS [TAGS ...]] [-p]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| file | -f  --file | The file to be loaded | None | True | None |
| description | -d  --description | The description of the routine |  | True | None |
| name | -n  --name | The name of the routine. | None | True | None |
| tags | -t  --tags | The tags of the routine |  | True | None |
| public | -p  --public | Whether the routine should be public or not | False | True | None |

---
