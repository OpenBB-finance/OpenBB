---
title: gamma
description: This docusaurus page provides insights about the usage of gamma command
  which allows the user to view the Options Gamma Levels for a particular stock. This
  can be crucial to make informed trading decisions.
keywords:
- Options Gamma Levels
- Zero Gamma
- Put Wall
- Call Wall
- Gamma command
- underlying stock price changes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: gamma - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to view the Options Gamma Levels for a particular stock. Options Gamma Levels are important to understanding the rate of change for the option's Delta when the underlying stock price changes. Knowing this information can help traders make informed decisions about which options to purchase.

| Name | Description |
| ---- | ----------- |
| Zero Gamma | Point closest to net zero of Call and Put Gamma |
| Put Wall | Strike with the largest NET Put Gamma |
| Call Wall | Strike with the largest NET Call Gamma |

### Usage

```python wordwrap
/gamma ticker [expiry]
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
/gamma AMD
```

```
/gamma AMD 2022-07-29
```

---
