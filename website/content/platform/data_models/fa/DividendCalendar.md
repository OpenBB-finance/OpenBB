---
title: DividendCalendar
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
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| date | date | The date of the data. |
| label | str | Date in human readable form in the calendar. |
| adj_dividend | NonNegativeFloat | Adjusted dividend on a date in the calendar. |
| dividend | NonNegativeFloat | Dividend amount in the calendar. |
| record_date | date | Record date of the dividend in the calendar. |
| payment_date | date | Payment date of the dividend in the calendar. |
| declaration_date | date | Declaration date of the dividend in the calendar. |
</TabItem>

</Tabs>

