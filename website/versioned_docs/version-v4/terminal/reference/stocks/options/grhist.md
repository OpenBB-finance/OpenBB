---
title: grhist
description: OpenBB Terminal Function
---

# grhist

Plot historical option greeks.

### Usage

```python
grhist -s STRIKE [-p] [-g {iv,gamma,theta,vega,delta,rho,premium}] [-c CHAIN_ID] [-r] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| strike | Strike price to look at | None | False | None |
| put | Flag for showing put option | False | True | None |
| greek | Greek column to select | delta | True | iv, gamma, theta, vega, delta, rho, premium |
| chain_id | OCC option symbol |  | True | None |
| raw | Display raw data | False | True | None |
| limit | Limit of raw data rows to display | 20 | True | None |

![grhist](https://user-images.githubusercontent.com/46355364/154278932-086a0005-be71-4493-843d-3f9100a60905.png)

---
