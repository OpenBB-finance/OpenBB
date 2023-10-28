---
title: pir
description: Create comprehensive ETF excel reports using the passive investor ETF
  tool 'pir'. This tool generates a detailed report containing significant metrics
  about any ETFs obtained from Yahoo Finance. Modifiable parameters include the ETF
  symbols, report filename, and save location.
keywords:
- passive investor ETF
- ETF excel report
- Yahoo Finance ETF metrics
- ETF report generation
- OpenBBUserData
- Python programming
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf /pir - Reference | OpenBB Terminal Docs" />

Create passive investor ETF excel report which contains most of the important metrics about an ETF obtained from Yahoo Finnace. You are able to input any ETF ticker you like within the command to create am extensive report

### Usage

```python
pir [-e NAMES] [--filename FILENAME] [--folder FOLDER]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| names | Symbols to create a report for (e.g. pir ARKW ARKQ QQQ VOO) |  | True | None |
| filename | Filename of the excel ETF report | ETF_report_20221125_164801 | True | None |
| folder | Folder where the excel ETF report will be saved | /home/runner/OpenBBUserData/exports | True | None |

![pir](https://raw.githubusercontent.com/JerBouma/ThePassiveInvestor/master/Images/outputExample.gif)

---
