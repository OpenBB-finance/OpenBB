---
title: "Earnings Call Transcript"
description: "Get earnings call transcripts for a given company"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

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
from openbb_core.provider.standard_models.earnings_call_transcript import (
EarningsCallTranscriptData,
EarningsCallTranscriptQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| year | int | Year of the earnings call transcript. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| year | int | Year of the earnings call transcript. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| quarter | int | Quarter of the earnings call transcript. |
| year | int | Year of the earnings call transcript. |
| date | datetime | The date of the data. |
| content | str | Content of the earnings call transcript. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| quarter | int | Quarter of the earnings call transcript. |
| year | int | Year of the earnings call transcript. |
| date | datetime | The date of the data. |
| content | str | Content of the earnings call transcript. |
</TabItem>

</Tabs>

