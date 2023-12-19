---
title: anchor
description: This documentation covers the usage of anchor which displays earnings
  data of a specific terra address. It also provides the option to view the history
  of past transactions. The page provides code examples for better understanding.
keywords:
- anchor
- terra
- cryptocurrency
- crypto
- Blockchain
- earnings data
- transactions history
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/defi/anchor - Reference | OpenBB Terminal Docs" />

Displays anchor protocol earnings data of a certain terra address --transactions flag can be passed to show history of previous transactions [Source: https://cryptosaurio.com/]

### Usage

```python
anchor --address ADDRESS [--transactions]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| address | Terra address. Valid terra addresses start with 'terra' | None | False | None |
| transactions | Flag to show transactions history in anchor earn | False | True | None |


---

## Examples

```python
2022 Mar 18, 14:29 (🦋) /crypto/defi/ $ anchor terra13kc0x8kr3sq8226myf4nmanmn2mrk9s5s9wsnz --transactions
```
![anchor](https://user-images.githubusercontent.com/43375532/159065235-e8fb189d-f670-4391-a7fc-064640b9607d.png)

---
