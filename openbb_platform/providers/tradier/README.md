# OpenBB Tradier Provider

`openbb-tradier` is a data provider extension for the OpenBB Platform.

## Installation

To install the extension:

```bash
pip install openbb-template
```

## Authorization

This extension requires two authorization fields:

- 'tradier_api_key'
- 'tradier_account_type'

Where the account type is either "sandbox" or "live".

Add these to the file, under 'credentials': `~/.openbb_platform/user_settings.json`
