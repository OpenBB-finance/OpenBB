---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: day
description: OpenBB Telegram Command
---

# flow

Returns the flow for a stock. /flow, /flow wk, /flow open, /flow unu, /flow prem

### Usage

```python wordwrap
/flow [ticker] [expiry] [strike] [opt_type]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker - Not required for subcmd: unu | True | None |
| expiry | Expiration date - Only available for subcmd: day (default: None) | True | None |
| strike | Strike price - Only available for subcmd: day (default: None) | True | None |
| opt_type | call/put/calls/puts/c/p - Only available for subcmd: day (default: None) | True | Calls, Puts, c, p, call, put |


---

## Examples

```
/flow AMD
```

```
/flow AMD 2022-07-29
```

---
