## Update list of coins

### Coingecko

- File: `/data/coingecko_coins.json`
- Endpoint: [https://api.coingecko.com/api/v3/coins/list](https://api.coingecko.com/api/v3/coins/list)

### Coinpaprika

- File: `/data/coinpaprika_coins.json`
- Endpoint: [https://api.coinpaprika.com/v1/coins](https://api.coinpaprika.com/v1/coins)

### Defillama

- File: `/data/defillama_dapps.json`
- Endpoint: [https://api.llama.fi/protocols](https://api.llama.fi/protocols)

```python
import requests
API_URL = "https://api.llama.fi"
url = f"{API_URL}/protocols"
r = requests.get(url)
data = r.json()
protocols = {}
for protocol in data:
    protocols[protocol['slug']] = protocol['name']
```
