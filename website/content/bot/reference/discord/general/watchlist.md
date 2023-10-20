---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: watchlist
description: OpenBB Discord Command
---

# watchlist

This command allows the user to retrieve an overview of their watchlist, which includes the current price, high/low, volume, and change. You can also get other related information with a quick click like flow, darkpool data, technical analysis, and news - all from one spot.

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
