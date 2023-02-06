## Update list of coins

### Coingecko

- File: `/data/coingecko_coins.json`
- Endpoint: [https://api.coingecko.com/api/v3/coins/list](https://api.coingecko.com/api/v3/coins/list)

- File: `/data/coingecko_categories.json`
- Endpoint: [https://api.coingecko.com/api/v3/coins/list](https://api.coingecko.com/api/v3/coins/list)
- Code:

```python
new_categories = {}
for category in categories:
    new_categories[category['category_id']] = category['name']
```

### Coinpaprika

- File: `/data/coinpaprika_coins.json`
- Endpoint: [https://api.coinpaprika.com/v1/coins](https://api.coinpaprika.com/v1/coins)

### Defillama

- File: `/data/defillama_dapps.json`
- Endpoint: [https://api.llama.fi/protocols](https://api.llama.fi/protocols)

```python
import request
API_URL = "https://api.llama.fi"
url = f"{API_URL}/protocols"
r = request(url)
data = r.json()
protocols = {}
for protocol in data:
    protocols[protocol['slug']] = protocol['name']
```
