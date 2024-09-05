# CFTC Provider Extension

## Installation

Install from PyPI with:

```sh
pip install openbb-cftc
```

Install this extension locally with:

```sh
pip install -e .
```

## Credentials

Credentials are not required, but your IP address may be subject to throttling limits.

API requests made using an application token are not throttled.

Create a free account here: https://evergreen.data.socrata.com/signup

Then, generate the app_token by signing in with the credentials here: https://publicreporting.cftc.gov/profile/edit/developer_settings.

### Credentials Key

If adding a token, use `cftc_app_token` as the key in the `user_settings.json` file. The value expected value is the app_token and not the `secret` or `api_key`.

