---
title: prem
description: This page provides instructions on how to use the 'flow prem' command
  to retrieve a daily chart which visually represents the sum of premiums for call/put
  options for a given stock ticker. A clear graphic visualization will make it easier
  for users to understand the dynamics of premium changes.
keywords:
- flow prem command
- call/put options
- options premium chart
- daily premium data
- premium visualization
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow - flow: prem - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a chart displaying the sum of premium for call/put options for a particular ticker on a daily basis. This chart will help users quickly and easily visualize the changing premium amounts over time.

### Usage

```python wordwrap
/flow prem [ticker]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker - Not required for subcmd: unu | True | None |


---

## Examples

```
/flow prem AMD
```

---
