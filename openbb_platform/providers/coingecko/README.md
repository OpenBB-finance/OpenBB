# CoinGecko Provider

CoinGecko Pro provider package for the OpenBB Platform.

Implemented models:

- `CryptoHistorical`

Primary endpoints:

- `GET /coins/markets` for symbol-to-coin-id resolution.
- `GET /coins/{id}/ohlcv/range` for OHLCV series when available.
- Fallback: `GET /coins/{id}/ohlc/range` + `GET /coins/{id}/market_chart/range`.

