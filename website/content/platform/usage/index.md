---
title: Basics
sidebar_position: 1
description: The OpenBB Platform is a modern investment research platform for everyone.  At its base, the Platform supplies core architecture and services for connecting data providers and extensions.  It is consumable as a Python client and FastAPI.
keywords: [basics, installation, getting started, platform, core, openbb, provider, extensions, architecture, api, Fast, rest, python, client]
---
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Basics - Platform | OpenBB Docs" />

The OpenBB Platform is a modern investment research platform for everyone.  At its base, the Platform supplies core architecture and services for connecting data providers and extensions, consumable as a Python client and Fast API.  The extension framework provides interoperability between as many, or few, services required.  Optional extras are not included with the base installation, and these include:

    - Charting libraries and views
    - Data cleaning
    - Technical/Quantitative Analysis
    - Community data providers
    - CLI Terminal

## Authorization

Most data connections require API keys, assigned to individual users.  Authorization is not required to initialize the core services.

### OpenBB Hub

Data provider credentials and user preferences can be securely stored on the OpenBB Hub and accessed with a revokable Personal Access Token (PAT).  Login to the [Hub](https://my.openbb.co/) to manage this method of remote authorization.

#### Python Client

Login using the Python client with:

```jupyterpython
from openbb import obb

# Login with personal access token
obb.account.login(pat="your_pat", remember_me=True)

# Login with email and password
obb.account.login(email="your_email", password="your_password", remember_me=True)

# Change a credential
obb.user.credentials.polygon_api_key = "new_key"

# Save account changes
obb.account.save()

# Refresh account with latest changes
obb.account.refresh()

# Logout
obb.account.logout()
```

Set `remember_me` as `False` when logging in to discard all credentials at the end of the session.

#### Fast API

Activate the Python environment and then start the server from a Terminal command line with:

```console
uvicorn openbb_core.api.rest_api:app
```

To use the Fast API documentation page, navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Start a Python session and make a POST request to login.

```python
import requests

url = 'http://127.0.0.1:8000/api/v1/account/token'
headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}
json = f"openbb_hub=true&grant_type=&username={username}&password={password}&scope=&client_id=&client_secret="

response = requests.post(url=url, headers=headers, data=data)

response.json()
```

Format headers for data requests by including the bearer token generated in the response from the login and then make a GET request.

```python
import requests

symbol="SPY"
url = f"http://127.0.0.1:8000/api/v1/stocks/quote?provider=intrinio&symbol={symbol}&source=intrinio_mx"
headers = {"accept": "application/json", "Authorization": f"Bearer {access_token}"}

response = requests.get(url=url, headers=headers)

response.json()
```

### Local Environment

Credentials and user preferences  can be stored locally, in `~/.openbb_platform/`, as a JSON file, `user_settings.json`.  If this file does not exist, create it with any text editor.  The schema below can be copy/pasted if required, providers not listed here are added using the same format:

```json
{
  "credentials": {
    "fmp_api_key": "REPLACE",
    "polygon_api_key": "REPLACE",
    "benzinga_api_key": "REPLACE",
    "fred_api_key": "REPLACE",
    "quandl_api_key": "REPLACE",
    "intrinio_api_key": "REPLACE",
    "alpha_vantage_api_key": "REPLACE",
    }
}
```

The credentials will be read when the Python client is initialized, or when the Fast API is authorized with one of the test users.  There are 2 default users for testing purpose:

- User "openbb"

  - username : openbb
  - password : openbb

- User "finance"

  - username : finance
  - password : finance

Use these, in conjunction with `openbb_hub=false`, to generate an authorization token for the Fast API without logging into Hub.

To inspect the credentials use:

```python
requests.get("http://127.0.0.1:8000/api/v1/user", headers=headers).json()["credentials"]
```

To set keys from the Python client for the current session only, access the Credentials class:

```python
obb.user.credentials.intrinio_api_key = "REPLACE_WITH_KEY"
```
