---
title: Earnings Call Transcript
description: This page describes the implementation of the Earnings Call Transcript
  model in the OpenBB Provider library. It provides details about the Python import
  statements, class names, parameters, and data associated with this model. This includes
  the relevant parameters for querying financial data like symbol, year, and quarter,
  and data fields such as content of the earnings call transcript.
keywords:
- Earnings Call Transcript
- EarningsCallTranscriptData
- EarningsCallTranscriptQueryParams
- OpenBB Provider
- FMP provider
- Python import statement
- Python standard models
- Data Query Params
- Financial data
- Financial Model
- Yearly earnings call transcript
- Quarterly earnings call transcript
- Earnings data
- Earnings data content
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Earnings Call Transcript - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EarningsCallTranscript` | `EarningsCallTranscriptQueryParams` | `EarningsCallTranscriptData` |

### Import Statement

```python
from openbb_provider.standard_models.earnings_call_transcript import (
EarningsCallTranscriptData,
EarningsCallTranscriptQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| year | int | Year of the earnings call transcript. |  | False |
| quarter | int | Quarter of the earnings call transcript. | 1 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| quarter | int | Quarter of the earnings call transcript. |
| year | int | Year of the earnings call transcript. |
| date | datetime | The date of the data. |
| content | str | Content of the earnings call transcript. |
</TabItem>

</Tabs>
