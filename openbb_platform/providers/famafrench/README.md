# OpenBB Fama-French Extension

This extension implements the Ken French data library (Source: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
as an OpenBB Platform Provider and Router extension.

## Installation

Install this extension with:

```sh
pip install openbb-famafrench
```

## Coverage

The extension provides six API endpoints:

```python
In [1]: from openbb import obb

In [2]: obb.famafrench
Out[2]:
/famafrench
    breakpoints
    country_portfolio_returns
    factor_choices  <-- Utility function serving choices to the OpenBB Workspace widget
    factors
    international_index_returns
    regional_portfolio_returns
    us_portfolio_returns
```

## Usage

The most common use will be for retrieving the 3 and 5-factor models, default state is 3-factors, at a monthly interval, for the United States.

```python
from openbb import obb

factors = obb.famafrench.factors()
```

Or, by region and factor:

```python
momentum = obb.famafrench.factors(factor="momentum", region="europe")
```

Metadata corresponding to the file downloaded is available under, `extra["results_metadata"]`, of the results object.

```python
factors.extra["results_metadata"]

{
    'description': '### \n\nThis file was created using the 202504 CRSP database. The 1-month TBill rate data until 202405 are from Ibbotson Associates. Starting from 202406, the 1-month TBill rate is from ICE BofA US 1-Month Treasury Bill Index.\n\n',
    'frequency': 'monthly',
    'formations': ['Mkt-RF', 'SMB', 'HML', 'RF']
}
```

Refer to the endpoint's docstring for detailed descriptions.
