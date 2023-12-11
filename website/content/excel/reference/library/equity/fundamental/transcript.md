---
title: transcript
description: Learn how to retrieve earnings call transcripts for a given company using
  Python obb.equity.fundamental.transcript. Understand the data parameters, returns,
  symbol, year, quarter, and metadata associated with the transcripts.
keywords: 
- earnings call transcript
- python obb.equity.fundamental.transcript
- data parameters
- returns
- symbols
- year
- quar
- content
- metadata
- provider
---

<!-- markdownlint-disable MD041 -->

Earnings Call Transcript. Earnings call transcript for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.TRANSCRIPT(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| year | Number | Year of the earnings call transcript. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| quarter | Quarter of the earnings call transcript.  |
| year | Year of the earnings call transcript.  |
| date | The date of the data.  |
| content | Content of the earnings call transcript.  |
