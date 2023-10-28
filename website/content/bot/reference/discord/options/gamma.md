---
title: gamma
description: This page is a guide on how to view the Options Gamma Levels for a specific
  stock using the '/op gamma' command. It provides an understanding of Delta's rate
  of change with stock price variations and aids in making informed trading decisions.
keywords:
- options gamma levels
- stock price changes
- delta rate of change
- trading decisions
- call and put gamma
- put wall
- call wall
- stock ticker
- expiry date
- /op gamma
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: gamma - Discord Reference | OpenBB Bot Docs" />

This command allows the user to view the Options Gamma Levels for a particular stock. Options Gamma Levels are important to understanding the rate of change for the option's Delta when the underlying stock price changes. Knowing this information can help traders make informed decisions about which options to purchase.

| Name | Description |
| ---- | ----------- |
| Zero Gamma | Point closest to net zero of Call and Put Gamma |
| Put Wall | Strike with the largest NET Put Gamma |
| Call Wall | Strike with the largest NET Call Gamma |

### Usage

```python wordwrap
/op gamma ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Gamma from now until expiry | True | None |


---

## Examples

```
/op gamma ticker:AMD
```

```
/op gamma ticker:AMD expiry:2022-07-29
```

---
