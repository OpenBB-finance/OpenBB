---
title: "Price Target"
description: "Get analyst price targets by company"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `PriceTarget` | `PriceTargetQueryParams` | `PriceTargetData` |

### Import Statement

```python
from openbb_core.provider.standard_models.price_target import (
PriceTargetData,
PriceTargetQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): benzinga, finviz. | None | True |
| limit | int | The number of data entries to return. | 200 | True |
| provider | Literal['benzinga', 'finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): benzinga, finviz. | None | True |
| limit | int | The number of data entries to return. | 200 | True |
| provider | Literal['benzinga', 'finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| page | int | Page offset. For optimization, performance and technical reasons, page offsets are limited from 0 - 100000. Limit the query results by other parameters such as date. Used in conjunction with the limit and date parameters. | 0 | True |
| date | Union[date, str] | Date for calendar data, shorthand for date_from and date_to. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| updated | Union[date, int] | Records last Updated Unix timestamp (UTC). This will force the sort order to be Greater Than or Equal to the timestamp indicated. The date can be a date string or a Unix timestamp. The date string must be in the format of YYYY-MM-DD. | None | True |
| importance | int | Importance level to filter by. Uses Greater Than or Equal To the importance indicated | None | True |
| action | Literal['downgrades', 'maintains', 'reinstates', 'reiterates', 'upgrades', 'assumes', 'initiates', 'terminates', 'removes', 'suspends', 'firm_dissolved'] | Filter by a specific action_company. | None | True |
| analyst_ids | Union[str, List[str]] | Comma-separated list of analyst (person) IDs. Omitting will bring back all available analysts. | None | True |
| firm_ids | Union[str, List[str]] | Comma-separated list of firm IDs. | None | True |
| fields | Union[str, List[str]] | Comma-separated list of fields to include in the response. See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields. | None | True |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): benzinga, finviz. | None | True |
| limit | int | The number of data entries to return. | 200 | True |
| provider | Literal['benzinga', 'finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): benzinga, finviz. | None | True |
| limit | int | The number of data entries to return. | 200 | True |
| provider | Literal['benzinga', 'finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| with_grade | bool | Include upgrades and downgrades in the response. | False | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| published_date | Union[date, datetime] | Published date of the price target. |
| published_time | datetime.time | Time of the original rating, UTC. |
| symbol | str | Symbol representing the entity requested in the data. |
| exchange | str | Exchange where the company is traded. |
| company_name | str | Name of company that is the subject of rating. |
| analyst_name | str | Analyst name. |
| analyst_firm | str | Name of the analyst firm that published the price target. |
| currency | str | Currency the data is denominated in. |
| price_target | float | The current price target. |
| adj_price_target | float | Adjusted price target for splits and stock dividends. |
| price_target_previous | float | Previous price target. |
| previous_adj_price_target | float | Previous adjusted price target. |
| price_when_posted | float | Price when posted. |
| rating_current | str | The analyst's rating for the company. |
| rating_previous | str | Previous analyst rating for the company. |
| action | str | Description of the change in rating from firm's last rating. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| published_date | Union[date, datetime] | Published date of the price target. |
| published_time | datetime.time | Time of the original rating, UTC. |
| symbol | str | Symbol representing the entity requested in the data. |
| exchange | str | Exchange where the company is traded. |
| company_name | str | Name of company that is the subject of rating. |
| analyst_name | str | Analyst name. |
| analyst_firm | str | Name of the analyst firm that published the price target. |
| currency | str | Currency the data is denominated in. |
| price_target | float | The current price target. |
| adj_price_target | float | Adjusted price target for splits and stock dividends. |
| price_target_previous | float | Previous price target. |
| previous_adj_price_target | float | Previous adjusted price target. |
| price_when_posted | float | Price when posted. |
| rating_current | str | The analyst's rating for the company. |
| rating_previous | str | Previous analyst rating for the company. |
| action | str | Description of the change in rating from firm's last rating. |
| action_change | Literal['Announces', 'Maintains', 'Lowers', 'Raises', 'Removes', 'Adjusts'] | Description of the change in price target from firm's last price target. |
| importance | Literal[0, 1, 2, 3, 4, 5] | Subjective Basis of How Important Event is to Market. 5 = High |
| notes | str | Notes of the price target. |
| analyst_id | str | Id of the analyst. |
| url_news | str | URL for analyst ratings news articles for this ticker on Benzinga.com. |
| url_analyst | str | URL for analyst ratings page for this ticker on Benzinga.com. |
| id | str | Unique ID of this entry. |
| last_updated | datetime | Last updated timestamp, UTC. |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| published_date | Union[date, datetime] | Published date of the price target. |
| published_time | datetime.time | Time of the original rating, UTC. |
| symbol | str | Symbol representing the entity requested in the data. |
| exchange | str | Exchange where the company is traded. |
| company_name | str | Name of company that is the subject of rating. |
| analyst_name | str | Analyst name. |
| analyst_firm | str | Name of the analyst firm that published the price target. |
| currency | str | Currency the data is denominated in. |
| price_target | float | The current price target. |
| adj_price_target | float | Adjusted price target for splits and stock dividends. |
| price_target_previous | float | Previous price target. |
| previous_adj_price_target | float | Previous adjusted price target. |
| price_when_posted | float | Price when posted. |
| rating_current | str | The analyst's rating for the company. |
| rating_previous | str | Previous analyst rating for the company. |
| action | str | Description of the change in rating from firm's last rating. |
| status | str | The action taken by the firm. This could be 'Upgrade', 'Downgrade', 'Reiterated', etc. |
| rating_change | str | The rating given by the analyst. This could be 'Buy', 'Sell', 'Underweight', etc. If the rating is a revision, the change is indicated by '->' |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| published_date | Union[date, datetime] | Published date of the price target. |
| published_time | datetime.time | Time of the original rating, UTC. |
| symbol | str | Symbol representing the entity requested in the data. |
| exchange | str | Exchange where the company is traded. |
| company_name | str | Name of company that is the subject of rating. |
| analyst_name | str | Analyst name. |
| analyst_firm | str | Name of the analyst firm that published the price target. |
| currency | str | Currency the data is denominated in. |
| price_target | float | The current price target. |
| adj_price_target | float | Adjusted price target for splits and stock dividends. |
| price_target_previous | float | Previous price target. |
| previous_adj_price_target | float | Previous adjusted price target. |
| price_when_posted | float | Price when posted. |
| rating_current | str | The analyst's rating for the company. |
| rating_previous | str | Previous analyst rating for the company. |
| action | str | Description of the change in rating from firm's last rating. |
| news_url | str | News URL of the price target. |
| news_title | str | News title of the price target. |
| news_publisher | str | News publisher of the price target. |
| news_base_url | str | News base URL of the price target. |
</TabItem>

</Tabs>

