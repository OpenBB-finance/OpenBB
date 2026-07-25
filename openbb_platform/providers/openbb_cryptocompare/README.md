# OpenBB CryptoCompare Provider

Real-time and historical cryptocurrency market data from [CryptoCompare](https://www.cryptocompare.com).

## Models

| Model | Endpoint | Description |
|---|---|---|
| CryptoQuote | /data/pricemultifull | Real-time price quotes |
| CryptoHistorical | /data/v2/histoday | Historical daily price data |
| CryptoSearch | /data/blockchain/list | Cryptocurrency search/lookup |

## Installation

```bash
pip install openbb-cryptocompare
```

## Usage

```python
from openbb_core.app import OpenBB

ob = OpenBB()

# Real-time quotes
btc_quote = ob.crypto.quote(
    symbol="BTC",
    provider="cryptocompare",
)

# Historical data
btc_hist = ob.crypto.historical(
    symbol="BTC",
    provider="cryptocompare",
    limit=30,
)

# Search
coins = ob.crypto.search(
    query="BTC",
    provider="cryptocompare",
)
```

## API Key

Free tier (100k calls/month) does not require an API key.
For higher rate limits, set environment variable:
`OPENBB_CRYPTOCOMPARE_API_KEY`
