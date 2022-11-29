---
title: hm
description: OpenBB Terminal Function
---

# hm

Display cryptocurrencies heatmap with daily percentage change [Source: https://coingecko.com] Accepts --category or -c to display only coins of a certain category (default no category to display all coins ranked by market cap). You can look on only top N number of records with --limit.

### Usage

```python
hm [-l LIMIT] [-c CATEGORY]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Display N items | 10 | True | None |
| category | Category (e.g., stablecoins). Empty for no category |  | True | aave-tokens, analytics, arbitrum-ecosystem, artificial-intelligence, asset-backed-tokens, asset-manager, augmented-reality, automated-market-maker-amm, avalanche-ecosystem, axie-infinity, big-data, binance-launchpool, binance-smart-chain, business-platform, business-services, cardano-ecosystem, celo-ecosystem, centralized-exchange-token-cex, charity, cny-stablecoin, collectibles, communication, compound-tokens, cosmos-ecosystem, cryptocurrency, daomaker-ecosystem, decentralized-exchange, decentralized-finance-defi, defi-index, decentralized-derivatives, education, energy, entertainment, etf, eth-2-0-staking, eur-stablecoin, exchange-based-tokens, fan-token, fantom-ecosystem, finance-banking, fractionalized-nft, gambling, gaming, gbp-stablecoin, gig-economy, xdai-ecosystem, governance, guild-scholarship, harmony-ecosystem, healthcare, heco-chain-ecosystem, impossible-launchpad, index-coin, infrastructure, insurance, internet-of-things-iot, investment, iotex-ecosystem, kardiachain-ecosystem, krw-stablecoin, launchpad, layer-1, legal, lending-borrowing, leveraged-token, lp-tokens, manufacturing, marketing, masternodes, media, meme-token, metaverse, mev-protection, mirrored-assets, moonriver-ecosystem, music, near-protocol-ecosystem, nft-index, niftex-shards, non-fungible-tokens-nft, number, oec-ecosystem, ohm-fork, olympus-pro, decentralized-options, oracle, decentralized-perpetuals, play-to-earn, dot-ecosystem, polygon-ecosystem, prediction-markets, privacy-coins, protocol, real-estate, realt-tokens, rebase-tokens, reddit-points, remittance, retail, seigniorage, smart-contract-platform, social-money, software, solana-ecosystem, sports, stablecoins, storage, structured-products, synthetic-assets, synths, technology-science, terra-ecosystem, tokenized-btc, tokenized-gold, tokenized-products, tokenized-stock, tokensets, tourism, usd-stablecoin, us-election-2020, utokens, virtual-reality, wallets, wrapped-tokens, yearn-yfi-partnerships-mergers, yield-aggregator, yield-farming, zilliqa-ecosystem |


---

## Examples

```python
2022 Feb 15, 06:44 (🦋) /crypto/disc/ $ cgtop
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
