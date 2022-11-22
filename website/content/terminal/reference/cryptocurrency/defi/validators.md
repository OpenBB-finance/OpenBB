---
title: validators
description: OpenBB Terminal Function
---

# validators

Displays information about terra validators. [Source: https://fcd.terra.dev/swagger]

### Usage

```python
usage: validators [-l LIMIT] [-s {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of validators to show | 10 | True | None |
| sortby | Sort by given column. Default: votingPower | votingPower | True | validatorName, tokensAmount, votingPower, commissionRate, status, uptime |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

