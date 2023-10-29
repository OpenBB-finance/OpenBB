---
title: prem
description: The page discusses the 'prem' command used for retrieving a chart displaying
  the sum of premium for call/put options for a specific ticker. It provides usage
  details, parameters, and examples for newcomers or experienced users to visualize
  the changing premium amounts over time.
keywords:
- prem command
- options premium
- call/put options
- stock ticker
- premium chart
- /flow prem usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: prem - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a chart displaying the sum of premium for call/put options for a particular ticker on a daily basis. This chart will help users quickly and easily visualize the changing premium amounts over time.

### Usage

```python wordwrap
/flow prem ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/flow prem ticker:AMD
```

---
