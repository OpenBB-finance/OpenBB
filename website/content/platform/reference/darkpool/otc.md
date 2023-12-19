---
title: otc
description: Get weekly aggregate trade data for Over The Counter deals, including
  ATS trading data and non-ATS trading data. The data is provided for each ATS/firm
  with trade reporting obligations under FINRA rules.
keywords:
- Over The Counter deals
- ATS trading data
- FINRA rules
- symbol
- provider
- tier
- is_ats
- OBBject
- results
- OTCAggregate
- warnings
- Chart
- Metadata
- data
- update_date
- share_quantity
- trade_quantity
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Weekly aggregate trade data for Over The Counter deals.

ATS and non-ATS trading data for each ATS/firm
with trade reporting obligations under FINRA rules.

```python wordwrap
obb.equity.darkpool.otc(symbol: Union[str, List[str]] = None, provider: Literal[str] = finra)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['finra'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finra' if there is no default. | finra | True |
</TabItem>

<TabItem value='finra' label='finra'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['finra'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finra' if there is no default. | finra | True |
| tier | Literal['T1', 'T2', 'OTCE'] | "T1 - Securities included in the S&P 500, Russell 1000 and selected exchange-traded products;
        T2 - All other NMS stocks; OTC - Over-the-Counter equity securities | T1 | True |
| is_ats | bool | ATS data if true, NON-ATS otherwise | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[OTCAggregate]
        Serializable results.

    provider : Optional[Literal['finra']]
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
| update_date | date | Most recent date on which total trades is updated based on data received from each ATS/OTC. |
| share_quantity | float | Aggregate weekly total number of shares reported by each ATS for the Symbol. |
| trade_quantity | float | Aggregate weekly total number of trades reported by each ATS for the Symbol |
</TabItem>

</Tabs>

