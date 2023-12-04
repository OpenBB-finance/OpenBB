---
title: consensus
description: Learn how to access and use the Price Target Consensus functionality
  in your application. Explore the available parameters and understand the returned
  data structure.
keywords: 
- Price target consensus data
- equity estimates consensus
- symbol parameter
- provider parameter
- results attribute
- provider attribute
- warnings attribute
- chart attribute
- metadata attribute
- data table
- target_high column
- target_low column
- target_consensus column
- target_median column
---

<!-- markdownlint-disable MD041 -->

Price Target Consensus. Price target consensus data.

## Syntax

```excel wordwrap
=OBB.EQUITY.ESTIMATES.CONSENSUS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| target_high | High target of the price target consensus.  |
| target_low | Low target of the price target consensus.  |
| target_consensus | Consensus target of the price target consensus.  |
| target_median | Median target of the price target consensus.  |
