---
title: trailing_dividend_yield
description: Trailing 1yr dividend yield
keywords:
- equity
- fundamental
- trailing_dividend_yield
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity /fundamental/trailing_dividend_yield - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Trailing 1yr dividend yield.

```python wordwrap
obb.equity.fundamental.trailing_dividend_yield(symbol: Union[str, List[str]] = None, provider: Literal[str] = tiingo)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['tiingo'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tiingo' if there is no default. | tiingo | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[TrailingDividendYield]
        Serializable results.

    provider : Optional[Literal['tiingo']]
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
| date | date | The date of the data. |
| trailing_dividend_yield | float | Trailing dividend yield. |
</TabItem>

</Tabs>

