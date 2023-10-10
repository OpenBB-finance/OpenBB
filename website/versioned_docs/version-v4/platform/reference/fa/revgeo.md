---
title: revgeo
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# revgeo

Revenue Geographic.

```python wordwrap
revgeo(symbol: Union[str, List[str]], period: Literal[str] = annual, structure: Literal[str] = flat, provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Period of the data to return. | annual | True |
| structure | Literal['hierarchical', 'flat'] | Structure of the returned data. | flat | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[RevenueGeographic]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fmp'], NoneType]]
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
| geographic_segment | Dict[str, int] | Day level data containing the revenue of the geographic segment. |
| americas | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Revenue from the the American segment. |
| europe | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Revenue from the the European segment. |
| greater_china | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Revenue from the the Greater China segment. |
| japan | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Revenue from the the Japan segment. |
| rest_of_asia_pacific | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Revenue from the the Rest of Asia Pacific segment. |
</TabItem>

</Tabs>

