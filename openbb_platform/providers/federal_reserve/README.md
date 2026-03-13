# OpenBB Federal Reserve Provider

This extension integrates the [Federal Reserve](https://www.federalreserve.gov/data.htm) data provider into the OpenBB Platform.
It focuses on Federal Reserve data not published to FRED. No authorization is required for access.

## Installation

To install the extension:

```bash
pip install openbb-federal-reserve
```

Then build the Python static assets by running:

```sh
openbb-build
```

## Quick Start

The fastest way to get started is by connecting to the OpenBB Workspace as a custom backend.

### Start Server

```sh
openbb-api
```

This starts the FastAPI server over localhost on port 6900.

### Add to Workspace

See the documentation [here](https://docs.openbb.co/odp/python/quickstart/workspace) for more details.

### Click to Open App

Once added, click on the app to open the dashboard.

The dashboard contains widgets with metadata and information, as well ones for exploring and retrieving the data.


## Coverage

This extension creates multiple OpenBB Workspace apps, along with individual widgets for each endpoint.

### Apps

- FOMC Documents - Current and historical PDF documents of minutes, projections, Beige Books, policy statements, and more.
- Federal Reserve System - Stats & Indicators - Data statistics and indicators from the regional members of the Federal Reserve System.

### Endpoints

- `.economy.money_measures`
- `.economy.central_bank_holdings`
- `.economy.primary_dealer_positioning`
- `.economy.primary_dealer_fails`
- `.economy.fomc_documents`
- `.economy.total_factor_productivity`
- `.economy.survey.inflation_expectations`
- `.fixedincome.rate.sofr`
- `.fixedincome.rate.effr`
- `.fixedincome.rate.overnight_bank_funding`
- `.fixedincome.government.yield_curve`
- `.fixedincome.government.treasury_rates`
- `.fixedincome.government.svensson_yield_curve`
