```
usage: fun [-m {twitter_followers,gmv_annualized,market_cap,take_rate,revenue,revenue_protocol,tvl,pe,pe_circulating,ps,ps_circulating}]
           [-c {Asset Management,Blockchain,DeFi,Exchange,Gaming,Insurance,Interoperability,Lending,NFT,Other,Prediction Market,Stablecoin}] [-t {24h,7d,30d,90d,180d,365d}] [-a]
           [-l LIMIT] [-h] [--export EXPORT]
```

Display fundamental metrics overview [Source: Token Terminal]

```
optional arguments:
  -m {twitter_followers,gmv_annualized,market_cap,take_rate,revenue,revenue_protocol,tvl,pe,pe_circulating,ps,ps_circulating}, --metric {twitter_followers,gmv_annualized,market_cap,take_rate,revenue,revenue_protocol,tvl,pe,pe_circulating,ps,ps_circulating}
                        Choose metric of interest (default: )
  -c {Asset Management,Blockchain,DeFi,Exchange,Gaming,Insurance,Interoperability,Lending,NFT,Other,Prediction Market,Stablecoin}, --category {Asset Management,Blockchain,DeFi,Exchange,Gaming,Insurance,Interoperability,Lending,NFT,Other,Prediction Market,Stablecoin}
                        Choose category of interest (default: )
  -t {24h,7d,30d,90d,180d,365d}, --timeline {24h,7d,30d,90d,180d,365d}
                        Choose timeline of interest (default: 24h)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -l LIMIT, --limit LIMIT
                        Display N items (default: 10)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Aug 28, 20:02 (🦋) /crypto/ov/ $ fun -m market_cap -c Blockchain
```

<img width="1428" alt="Screenshot 2022-08-29 at 00 07 31" src="https://user-images.githubusercontent.com/25267873/187100287-2d81da1a-0def-49f0-8c1f-fd1b10f40004.png">
