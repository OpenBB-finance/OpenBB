# OpenBB Tradier Provider

This extension integrates the [Tradier](https://tradier.com) data provider into the OpenBB Platform.

## Installation

To install the extension:

```bash
pip install openbb-tradier
```

Documentation available [here](https://docs.openbb.co/platform/developer_guide/contributing).

## Authorization

This extension requires two authorization fields:

- 'tradier_api_key'
- 'tradier_account_type'

Where the account type is either "sandbox" or "live".

Add these to the file, under 'credentials': `~/.openbb_platform/user_settings.json`
