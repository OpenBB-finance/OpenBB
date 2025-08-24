# Congress.gov Provider

This provider integrates with the Congress.gov API to provide access to U.S. legislative data and text.

## Features

### Congress Bills

- Fetch lists of bills from the U.S. Congress.
- Filter by congress session, bill type, date range.

### Bill Summaries & Metadata

- Get summaries of, and metadata for, a specific bill.
- Lists all actions, sponsors, committees, related bills, and titles.
- Returned as both a raw JSON object and formatted Markdown text.

### Bill Text URLs and Downloads

- Get URLs for different versions and file formats.
- Download full bill text as a base64-encoded string.

### OpenBB Workspace Application

With this extension installed, along with `openbb-platform-api`,
an OpenBB Workspace App is added to your backend.

The application provides a PDF viewer, bill summaries and metadata as rendered Markdown,
and a linked query tool for finding and reading legislation.

## Installation

This provider is part of the OpenBB Platform. Install it using:

```bash
pip install openbb-congress-gov
```

The Workspace Application can be launched as a standalone, with only `openbb-congress-gov` and `openbb-platform-api` installed. Launch it from the terminal command line with:

```sh
openbb-api
```

## Configuration

### Congress.gov API Key

To use the Congress Bills and Bill Summaries endpoints, you need a Congress.gov API key:

1. Go to https://api.congress.gov/sign-up/
2. Fill out the registration form
3. Agree to the terms of service
4. You will receive an API key via email

The API key is free and provides access to all Congress.gov data.

### Entering Credentials

Add the credential into OpenBB Platform from any of:

- Entry in `user_settings.json`

```json
{
    "credentials" : {
        "congress_gov_api_key": "YOUR KEY"
    }
}
```

- Set environment variable

```env
CONGRESS_GOV_API_KEY = "YOUR KEY"
```

- Add to the current session only

```python
from openbb import obb

obb.user.credentials.congress_gov_api_key = "YOUR KEY"
```

## Coverage

All endpoints are under the `obb.uscongress` path:

```python
In [1]: from openbb import obb
In [2]: obb.uscongress
Out[2]:
/uscongress
    bill_info
    bill_text
    bill_text_urls
    bills
```

### Bill Text

The `bill_text` endpoint is a POST request from the API, and expects a dictionary in the body of the request.

```json
{
    "urls": ["https://url-to-PDF-document"]
}
```


## Usage Examples

### Fetching Recent Bills

```python
from openbb import obb

# Get the 10 most recently updated bills
bills = obb.uscongress.bills(limit=10)
```

### Getting Bill Summaries

Reference individual bills by either their base URL (returned in the `obb.uscongress.bills` response),
or by the concatenated bill number.

```python
bill_info = obb.uscongress.bill_info(bill_url="119/hr/1")
```

See the function signatures and docstrings for parameters and detailed descriptions.
