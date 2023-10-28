---
title: transcript
description: The documentation page provides details about fetching earnings call
  transcripts for any company by specifying the symbol, year, and quarter. It also
  provides information about the data provider and the metadata returned along with
  the query results.
keywords:
- Earnings call transcript
- Data provider
- FMP
- symbol
- quarter
- year
- Metadata
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.transcript - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# transcript

Earnings Call Transcript. Earnings call transcript for a given company.

```python wordwrap
transcript(symbol: Union[str, List[str]], year: int, quarter: int = 1, provider: Literal[str] = fmp)
```

---

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

---

## Returns

```python wordwrap
OBBject
    results : List[EarningsCallTranscript]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

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
