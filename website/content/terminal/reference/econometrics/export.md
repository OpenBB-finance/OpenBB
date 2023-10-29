---
title: export
description: This documentation page guides you on how to use the 'export' command
  in Python for exporting a dataset to Excel or CSV. It provides detailed usage, parameters,
  and examples.
keywords:
- export
- dataset
- Excel
- CSV
- econometrics
- data export
- export command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /export - Reference | OpenBB Terminal Docs" />

Export dataset to Excel

### Usage

```python
export [-n NAME] [-t {xlsx,csv}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| name | The name of the dataset you wish to export | None | True | None |
| type | The file type you wish to export to | xlsx | True | xlsx, csv |


---

## Examples

```python
2022 Feb 24, 04:35 (🦋) /econometrics/ $ load ThesisData.xlsx thesis

2022 Feb 24, 04:36 (🦋) /econometrics/ $ export thesis -t csv
Saved file: /Users/jeroenbouma/My Drive/Programming/Python/OpenBBTerminal/exports/statistics/thesis_20220224_103614.csv
```
---
