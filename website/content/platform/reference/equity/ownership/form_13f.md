---
title: "form_13f"
description: "The Securities and Exchange Commission's (SEC) Form 13F is a quarterly report
that is required to be filed by all institutional investment managers with at least
$100 million in assets under management"
keywords:
- equity
- ownership
- form_13f
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/ownership/form_13f - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The Securities and Exchange Commission's (SEC) Form 13F is a quarterly report
that is required to be filed by all institutional investment managers with at least
$100 million in assets under management.
Managers are required to file Form 13F within 45 days after the last day of the calendar quarter.
Most funds wait until the end of this period in order to conceal
their investment strategy from competitors and the public.


Examples
--------

```python
from openbb import obb
obb.equity.ownership.form_13f(symbol='NVDA', provider='sec')
# Enter a date (calendar quarter ending) for a specific report.
obb.equity.ownership.form_13f(symbol='BRK-A', date='2016-09-30', provider='sec')
# Example finding Michael Burry's filings.
cik = obb.regulators.sec.institutions_search("Scion Asset Management").results[0].cik
# Use the `limit` parameter to return N number of reports from the most recent.
obb.equity.ownership.form_13f(cik, limit=2).to_df()
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. A CIK or Symbol can be used. |  | False |
| date | Union[date, str] | A specific date to get data for. The date represents the end of the reporting period. All form 13F-HR filings are based on the calendar year and are reported quarterly. If a date is not supplied, the most recent filing is returned. Submissions beginning 2013-06-30 are supported. | None | True |
| limit | int | The number of data entries to return. The number of previous filings to return. The date parameter takes priority over this parameter. | 1 | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. A CIK or Symbol can be used. |  | False |
| date | Union[date, str] | A specific date to get data for. The date represents the end of the reporting period. All form 13F-HR filings are based on the calendar year and are reported quarterly. If a date is not supplied, the most recent filing is returned. Submissions beginning 2013-06-30 are supported. | None | True |
| limit | int | The number of data entries to return. The number of previous filings to return. The date parameter takes priority over this parameter. | 1 | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Form13FHR
        Serializable results.
    provider : Literal['sec']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end-of-quarter date of the filing. |
| issuer | str | The name of the issuer. |
| cusip | str | The CUSIP of the security. |
| asset_class | str | The title of the asset class for the security. |
| security_type | Literal['SH', 'PRN'] | The total number of shares of the class of security or the principal amount of such class. 'SH' for shares. 'PRN' for principal amount. Convertible debt securities are reported as 'PRN'. |
| option_type | Literal['call', 'put'] | Defined when the holdings being reported are put or call options. Only long positions are reported. |
| voting_authority_sole | int | The number of shares for which the Manager exercises sole voting authority (none). |
| voting_authority_shared | int | The number of shares for which the Manager exercises a defined shared voting authority (none). |
| voting_authority_other | int | The number of shares for which the Manager exercises other shared voting authority (none). |
| principal_amount | int | The total number of shares of the class of security or the principal amount of such class. Only long positions are reported |
| value | int | The fair market value of the holding of the particular class of security. The value reported for options is the fair market value of the underlying security with respect to the number of shares controlled. Values are rounded to the nearest US dollar and use the closing price of the last trading day of the calendar year or quarter. |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end-of-quarter date of the filing. |
| issuer | str | The name of the issuer. |
| cusip | str | The CUSIP of the security. |
| asset_class | str | The title of the asset class for the security. |
| security_type | Literal['SH', 'PRN'] | The total number of shares of the class of security or the principal amount of such class. 'SH' for shares. 'PRN' for principal amount. Convertible debt securities are reported as 'PRN'. |
| option_type | Literal['call', 'put'] | Defined when the holdings being reported are put or call options. Only long positions are reported. |
| voting_authority_sole | int | The number of shares for which the Manager exercises sole voting authority (none). |
| voting_authority_shared | int | The number of shares for which the Manager exercises a defined shared voting authority (none). |
| voting_authority_other | int | The number of shares for which the Manager exercises other shared voting authority (none). |
| principal_amount | int | The total number of shares of the class of security or the principal amount of such class. Only long positions are reported |
| value | int | The fair market value of the holding of the particular class of security. The value reported for options is the fair market value of the underlying security with respect to the number of shares controlled. Values are rounded to the nearest US dollar and use the closing price of the last trading day of the calendar year or quarter. |
| weight | float | The weight of the security relative to the market value of all securities in the filing , as a normalized percent. |
</TabItem>

</Tabs>

