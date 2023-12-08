---
title: price_target
description: Get price target data for an equity symbol. Retrieve information such
  as publication date, analyst details, price target, and more. Supports multiple
  symbols and customizable providers.
keywords: 
- price target data
- equity estimates
- symbol
- provider
- grade
- published date
- news URL
- news title
- analyst name
- analyst company
- price target
- adjusted price target
- price when posted
- news publisher
- news base URL
---

<!-- markdownlint-disable MD041 -->

Price Target. Price target data.

## Syntax

```excel wordwrap
=OBB.EQUITY.ESTIMATES.PRICE_TARGET(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| with_grade | Boolean | Include upgrades and downgrades in the response. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| published_date | Published date of the price target.  |
| news_url | News URL of the price target.  |
| news_title | News title of the price target.  |
| analyst_name | Analyst name.  |
| analyst_company | Analyst company.  |
| price_target | Price target.  |
| adj_price_target | Adjusted price target.  |
| price_when_posted | Price when posted.  |
| news_publisher | News publisher of the price target.  |
| news_base_url | News base URL of the price target.  |
| new_grade | New grade (provider: fmp) |
| previous_grade | Previous grade (provider: fmp) |
| grading_company | Grading company (provider: fmp) |
