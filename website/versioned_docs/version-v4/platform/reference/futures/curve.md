---
title: curve
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# curve

Futures Historical Price.

```python wordwrap
curve(symbol: Union[str, List[str]], date: Union[date] = None, provider: Union[Literal[str]] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| date | Union[date] | Historical date to search curve for. | None | True |
| provider | Union[Literal['cboe', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FuturesCurve]
        Serializable results.

    provider : Optional[Literal[Union[Literal['cboe', 'yfinance'], NoneType]]
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
| expiration | str | Futures expiration month. |
| price | Union[float] | The close price of the symbol. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| expiration | str | Futures expiration month. |
| price | Union[float] | The close price of the symbol. |
| symbol | str | The trading symbol for the tenor of future. |
</TabItem>

</Tabs>

