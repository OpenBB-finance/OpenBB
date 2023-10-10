---
title: KeyExecutives
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


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

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| title | str | Designation of the key executive. |
| name | str | Name of the key executive. |
| pay | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Pay of the key executive. |
| currency_pay | str | Currency of the pay. |
| gender | Union[str] | Gender of the key executive. |
| year_born | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Birth year of the key executive. |
| title_since | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Date the tile was held since. |
</TabItem>

</Tabs>

