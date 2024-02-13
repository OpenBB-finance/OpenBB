---
title: dapp_metrics
description: Shows dapp metrics [Source https//dappradar
keywords:
- crypto.disc
- dapp_metrics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /disc/dapp_metrics - Reference | OpenBB Terminal Docs" />

Shows dapp metrics [Source: https://dappradar.com/] Accepts --dappId argument to specify the dapp --chain argument to filter by blockchain for multi-chain dapps --time_range argument to specify the time range. Default: 7d (can be 24h, 7d, 30d)

### Usage

```python wordwrap
dapp_metrics [-d DAPP_ID] [-c CHAIN] [-t TIME_RANGE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| dappId | -d  --dappId | Dapp ID | None | True | None |
| chain | -c  --chain | Filter by blockchain | None | True | None |
| time_range | -t  --time_range | Time range | 7d | True | 24h, 7d, 30d |

---
