---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: watchlist
description: OpenBB Discord Command
---

# watchlist

This command allows the user to retrieve a markets overview, which includes current stock prices, market indices, and other related information. This can be useful for tracking market trends and getting a quick snapshot of the markets at a glance.

### Usage

```python wordwrap
/watchlist [add] [edit]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| add | Add a ticker to your watchlist. You can add multiple tickers by separating them with a comma. | True | None |
| edit | Remove tickers from your watchlist. Choose Remove to bring up the interactive menu. | True | Remove |


---

## Examples

```
/watchlist
```
```
/watchlist add:AMD
```
```
/watchlist add:AMD,GOOG,TSLA
```
```
/watchlist edit:Remove
```

---
