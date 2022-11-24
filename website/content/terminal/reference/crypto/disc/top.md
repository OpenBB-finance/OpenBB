---
title: top
description: OpenBB Terminal Function
---

# top

Display N coins from the data source, if the data source is CoinGecko it can receive a category as argument (-c decentralized-finance-defi or -c stablecoins) and will show only the top coins in that category. can also receive sort arguments (these depend on the source), e.g., --sort Volume [$] You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]} with CoinGecko Number of coins to show: -l 10

### Usage

```python
top [-c CATEGORY] [-l LIMIT] [-s SORTBY [SORTBY ...]] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| category | Category (e.g., stablecoins). Empty for no category. Only works for 'CoinGecko' source. |  | True | aave-tokens, analytics, arbitrum-ecosystem, artificial-intelligence, asset-backed-tokens, asset-manager, augmented-reality, automated-market-maker-amm, avalanche-ecosystem, axie-infinity, big-data, binance-launchpool, binance-smart-chain, business-platform, business-services, cardano-ecosystem, celo-ecosystem, centralized-exchange-token-cex, charity, cny-stablecoin, collectibles, communication, compound-tokens, cosmos-ecosystem, cryptocurrency, daomaker-ecosystem, decentralized-exchange, decentralized-finance-defi, defi-index, decentralized-derivatives, education, energy, entertainment, etf, eth-2-0-staking, eur-stablecoin, exchange-based-tokens, fan-token, fantom-ecosystem, finance-banking, fractionalized-nft, gambling, gaming, gbp-stablecoin, gig-economy, xdai-ecosystem, governance, guild-scholarship, harmony-ecosystem, healthcare, heco-chain-ecosystem, impossible-launchpad, index-coin, infrastructure, insurance, internet-of-things-iot, investment, iotex-ecosystem, kardiachain-ecosystem, krw-stablecoin, launchpad, layer-1, legal, lending-borrowing, leveraged-token, lp-tokens, manufacturing, marketing, masternodes, media, meme-token, metaverse, mev-protection, mirrored-assets, moonriver-ecosystem, music, near-protocol-ecosystem, nft-index, niftex-shards, non-fungible-tokens-nft, number, oec-ecosystem, ohm-fork, olympus-pro, decentralized-options, oracle, decentralized-perpetuals, play-to-earn, dot-ecosystem, polygon-ecosystem, prediction-markets, privacy-coins, protocol, real-estate, realt-tokens, rebase-tokens, reddit-points, remittance, retail, seigniorage, smart-contract-platform, social-money, software, solana-ecosystem, sports, stablecoins, storage, structured-products, synthetic-assets, synths, technology-science, terra-ecosystem, tokenized-btc, tokenized-gold, tokenized-products, tokenized-stock, tokensets, tourism, usd-stablecoin, us-election-2020, utokens, virtual-reality, wallets, wrapped-tokens, yearn-yfi-partnerships-mergers, yield-aggregator, yield-farming, zilliqa-ecosystem |
| limit | Limit of records | 10 | True | None |
| sortby | Sort by given column. Default: Market Cap Rank | Market Cap Rank | True | Symbol, Name, Volume [$], Market Cap, Market Cap Rank, 7D Change [%], 24H Change [%] |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |


---

## Examples

```python
2022 Feb 15, 06:44 (🦋) /crypto/disc/ $ top
┌────────┬──────────────┬────────────┬────────────────┬─────────────────┬───────────────┬────────────────┐
│ Symbol │ Name         │ Volume [$] │ Market Cap [$] │ Market Cap Rank │ 7D Change [%] │ 24H Change [%] │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ btc    │ Bitcoin      │ 20.6B      │ 838.8B         │ 1               │ 0.93          │ 4.77           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ eth    │ Ethereum     │ 14.4B      │ 370.6B         │ 2               │ -1.53         │ 7.77           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ usdt   │ Tether       │ 43.3B      │ 78.5B          │ 3               │ -0.01         │ -0.05          │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ bnb    │ Binance Coin │ 1.8B       │ 72.2B          │ 4               │ -1.01         │ 8.18           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ usdc   │ USD Coin     │ 3B         │ 52.6B          │ 5               │ 0.25          │ 0.17           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ xrp    │ XRP          │ 3.2B       │ 39.9B          │ 6               │ 0.71          │ 5.51           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ ada    │ Cardano      │ 1B         │ 34.9B          │ 7               │ -9.04         │ 5.52           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ sol    │ Solana       │ 1.8B       │ 32.7B          │ 8               │ -12.54        │ 10.07          │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ luna   │ Terra        │ 1B         │ 22.4B          │ 9               │ -5.26         │ 8.67           │
├────────┼──────────────┼────────────┼────────────────┼─────────────────┼───────────────┼────────────────┤
│ AVAX   │ Avalanche    │ 899.9M     │ 21.7B          │ 10              │ 6.28          │ 12.72          │
└────────┴──────────────┴────────────┴────────────────┴─────────────────┴───────────────┴────────────────┘
```
---
