---
title: nonzero
description: The 'nonzero' page provides documentation on how to display addresses
  with nonzero assets in a specific blockchain using the Glassnode API. The page details
  the usage of the command and parameters, along with providing a visual representation.
keywords:
- nonzero
- blockchain
- glassnode
- addresses
- assets
- data fetching
- api
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/dd/nonzero - Reference | OpenBB Terminal Docs" />

Display addresses with nonzero assets in a certain blockchain [Source: https://glassnode.org] Note that free api keys only allow fetching data with a 1y lag

### Usage

```python
nonzero [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| since | Initial date. Default: 2 years ago | 2020-11-25 | True | None |
| until | Final date. Default: 1 year ago | 2021-11-23 | True | None |

![nonzero](https://user-images.githubusercontent.com/46355364/154064344-5b7825c8-9243-47ba-9930-0f5f7e3282a4.png)

---
