---
title: oichart
description: This documentation page gives a detailed explanation of the 'oichart'
  command used to retrieve a chart of Total Open Interest by Strike Price for a specific
  ticker symbol. The page provides usage, parameters, and examples to analyze the
  open interest on various strike prices and make informed decisions about the underlying
  security.
keywords:
- oichart
- Open Interest
- Strike Price
- Visual representation
- ticker symbol
- Stock Ticker
- Expiration Date
- Underlying security
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: oichart - Discord Reference | OpenBB Bot Docs" />

This command allows users to retrieve a chart of Total Open Interest by Strike Price for the given ticker symbol. This chart provides a visual representation of the open interest on various strike prices for the given ticker symbol, where the size of each point on the graph reflects the amount of open interest. This can be used to analyze the open interest on various strike prices and make informed decisions about the underlying security.

### Usage

```python wordwrap
/op oichart ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | True | None |


---

## Examples

```
/op oichart ticker:AMD
```

```
/op oichart ticker:AMD expiry:2022-07-29
```

---
