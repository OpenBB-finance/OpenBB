---
title: hqm
description: The HQM yield curve represents the high quality corporate bond market, i
keywords:
- fixedincome
- hqm
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /hqm - Reference | OpenBB Terminal Docs" />

The HQM yield curve represents the high quality corporate bond market, i.e., corporate bonds rated AAA, AA, or A. The HQM curve contains two regression terms. These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve that is the market-weighted average (MWA) quality of high quality bonds.

### Usage

```python wordwrap
hqm [-d DATE] [-p]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| date | -d  --date | Define the date of the yield curve. | None | True | None |
| par | -p  --par | Whether to include the Par Yield. | False | True | None |

---
