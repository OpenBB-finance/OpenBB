---
title: COT
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
| provider | Union[Literal['quandl']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'quandl' if there is no default. | quandl | True |
</TabItem>

<TabItem value='quandl' label='quandl'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['quandl']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'quandl' if there is no default. | quandl | True |
| code | str | 
            CFTC series code.  Use search_cot() to find the code.
            Codes not listed in the curated list, but are published by on the Nasdaq Data Link website, are valid.
            Certain symbols, such as "ES=F", or exact names are also valid.
            Default report is: S&P 500 Consolidated (CME))
             | 13874P | True |
| data_type | Union[Literal['F', 'FO', 'CITS']] | 
            The type of data to reuturn. Default is "FO".

            F = Futures only

            FO = Futures and Options

            CITS = Commodity Index Trader Supplemental. Only valid for commodities.
         | FO | True |
| legacy_format | Union[bool] | Returns the legacy format of report. Default is False. | False | True |
| report_type | Union[Literal['ALL', 'CHG', 'OLD', 'OTR']] | 
            The type of report to return. Default is "ALL".

                ALL = All

                CHG = Change in Positions

                OLD = Old Crop Years

                OTR = Other Crop Years
         | ALL | True |
| measure | Union[Literal['CR', 'NT', 'OI', 'CHG']] | 
            The measure to return. Default is None.

            CR = Concentration Ratios

            NT = Number of Traders

            OI = Percent of Open Interest

            CHG = Change in Positions. Only valid when data_type is "CITS".
         | None | True |
| start_date | Union[date] | The start date of the time series. Defaults to all. | None | True |
| end_date | Union[date] | The end date of the time series. Defaults to the most recent data. | None | True |
| transform | Union[Literal['diff', 'rdiff', 'cumul', 'normalize']] | Transform the data as w/w difference, percent change, cumulative, or normalize. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
</TabItem>

</Tabs>

