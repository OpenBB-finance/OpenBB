---
title: grhist
description: The grhist page is dedicated to illustrating how to plot historical option
  greeks using Python. It includes various parameters like strike price, put option,
  greek column, OCC option symbol, raw data, among others. It also demonstrates the
  use of a certain data visualization for better understanding.
keywords:
- grhist
- historical option greeks plot
- option greeks
- put option
- strike price
- greek column
- OCC option symbol
- raw data
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /options/grhist - Reference | OpenBB Terminal Docs" />

Plot historical option greeks.

### Usage

```python wordwrap
grhist [-s STRIKE] [-e EXPIRATION] [-p] [-g {iv,gamma,theta,vega,delta,rho,premium}] -c CHAIN_ID [-r] [-l LIMIT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| strike | -s  --strike | Strike price to look at | None | True | None |
| expiration | -e  --expiration | The expiration date of the option. Format: YYYY-MM-DD | 2023-11-24 | True | None |
| put | -p  --put | Flag for showing put option | False | True | None |
| greek | -g  --greek | Greek column to select | delta | True | iv, gamma, theta, vega, delta, rho, premium |
| chain_id | -c  --chain | OCC option symbol |  | False | None |
| raw | -r  --raw | Display raw data | False | True | None |
| limit | -l  --limit | Limit of raw data rows to display | 20 | True | None |

![grhist](https://user-images.githubusercontent.com/46355364/154278932-086a0005-be71-4493-843d-3f9100a60905.png)

---
