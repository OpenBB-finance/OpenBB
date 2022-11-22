---
title: grhist
description: OpenBB Terminal Function
---

# grhist

Plot historical option greeks.

### Usage

```python
usage: grhist -s STRIKE [-p] [-g {iv,gamma,theta,vega,delta,rho,premium}] [-c CHAIN_ID] [-r] [-l LIMIT]
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
---

