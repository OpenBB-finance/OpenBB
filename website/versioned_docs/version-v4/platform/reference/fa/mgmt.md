---
title: mgmt
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mgmt

Key Executives.

```python wordwrap
mgmt(symbol: Union[str, List[str]], provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[KeyExecutives]
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
| title | str | Designation of the key executive. |
| name | str | Name of the key executive. |
| pay | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Pay of the key executive. |
| currency_pay | str | Currency of the pay. |
| gender | Union[str] | Gender of the key executive. |
| year_born | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Birth year of the key executive. |
| title_since | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Date the tile was held since. |
</TabItem>

</Tabs>

