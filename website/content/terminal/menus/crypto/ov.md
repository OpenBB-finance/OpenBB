---
title: Overview
description: This page provides an introduction to the Overview sub-menu, within the Crypto menu, of the OpenBB Terminal. The menu provides general insights and current statistics for the digital asset universe.
keywords:
- crypto
- coingecko
- coinpaprika
- cryptopanic
- bitcoin rainbow
- tokenterminal
- blockchaincenter
- rekt
- withdrawalfees
- bitcoin
- overview
- market
- indexes
- indices
- derivatives
- stablecoins
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Overview - Crypto - Menus | OpenBB Terminal Docs" />

The Overview sub-menu provides general insights and current statistics for the digital asset universe.

## Usage

Enter the Overview menu from the Crypto menu by typing, `ov`, into the Terminal.  Or, with the absolute path:

```console
/crypto/ov
```

![Screenshot 2023-10-31 at 12 51 06 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/c756cef5-4dfc-4098-a1a8-2fdf231c5f29)

### Global

This command will display a pie chart of the market cap distribution across categories.

```console
/crypto/ov/global --pie
```

![Screenshot 2023-10-31 at 1 00 12 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f5b174f9-dd4a-45db-b033-f892187a292d)

Without the `--pie` argument, a table of statistics will be returned.

```console
/crypto/ov/global --source CoinPaprika
```

| Metric                       | Value               |
|:-----------------------------|:--------------------|
| market_cap_usd               | 1311005992664       |
| volume_24h_usd               | 80507355044         |
| bitcoin_dominance_percentage | 51.45               |
| cryptocurrencies_number      | 8647                |
| market_cap_ath_value         | 3629384273801       |
| market_cap_ath_date          | 2021-10-27 07:40:00 |
| volume_24h_ath_value         | 16460384024873      |
| volume_24h_ath_date          | 2022-12-03 07:55:00 |
| volume_24h_percent_from_ath  | -99.51              |
| volume_24h_percent_to_ath    | 9999.99             |
| market_cap_change_24h        | 0.22                |
| volume_24h_change_24h        | -0.03               |
| last_updated                 | 2023-10-31 13:08:03 |

```console
/crypto/ov/global --source CoinGecko
```

| Metric                               |        Value |
|:-------------------------------------|-------------:|
| Active Cryptocurrencies              | 10669        |
| Upcoming Icos                        |     0        |
| Ongoing Icos                         |    49        |
| Ended Icos                           |  3376        |
| Markets                              |   915        |
| Market Cap Change Percentage 24H Usd |     0.388704 |
| Btc Market Cap In Pct                |    50.9577   |
| Eth Market Cap In Pct                |    16.4667   |
| Altcoin Market Cap In Pct            |    32.5756   |


### Info

`info` populates a table comparing key statistics.

```console
/crypto/ov/info --limit 5
```

|   rank | name         | symbol   |        price |   volume_24h |   circulating_supply |   total_supply |   max_supply |   market_cap |   beta_value |   ath_price |
|-------:|:-------------|:---------|-------------:|-------------:|---------------------:|---------------:|-------------:|-------------:|-------------:|------------:|
|      1 | Bitcoin      | BTC      | 34549.1      |  4358348411.915434 |             19529500 |       19529494 |     21000000 | 674727548248 |   1.08882    | 68692.1     |
|      2 | Ethereum     | ETH      |  1810.87     |  5255905608.761287 |            120269517 |      120269517 |            0 | 217792941980 |   1.14074    |  4864.11    |
|      3 | Tether       | USDT     |     1.00039  |  30909958617.638874  |          84663138137 |    87870794561 |            0 |  84696158663 |  -0.00166159 |     1.21549 |
|      4 | Binance Coin | BNB      |   225.853    |  364485823.712885 |            151703660 |      151070177 |    200000000 |  34262746244 |   0.858213   |   690.568   |
|      5 | XRP          | XRP      |     0.598955 |  1706798672.187495  |          53560508378 |    99988331658 | 100000000000 |  32080335199 |   1.01748    |     3.84194 |


