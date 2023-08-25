---
title: Forex
keywords: [forex, currency, money, hedge, dollar, euro, pound, currencies, market, openbb terminal, how to, example, fwd, forward rate, oanda, quote]
description: A brief introduction and guide to the Forex menu. It includes descriptions of its functionality, commands, data, outputs, and examples in context.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Forex - Terminal | OpenBB Docs" />

The Forex menu enables you to <a href="/terminal/reference/forex/load" target="_blank" rel="noreferrer noopener">load</a> any combination of currencies (e.g. USDEUR or JPYGBP), show current <a href="/terminal/reference/forex/quote" target="_blank" rel="noreferrer noopener">quote</a> and historical data (<a href="/terminal/reference/forex/candle" target="_blank" rel="noreferrer noopener">candle</a>) as well as forward rates (<a href="/terminal/reference/forex/fwd" target="_blank" rel="noreferrer noopener">fwd</a>). Furthermore, the menu has the ability to also apply <a href="/terminal/usage/intros/common/ta" target="_blank" rel="noreferrer noopener">Technical Analysis</a> and <a href="/terminal/usage/intros/forecast" target="_blank" rel="noreferrer noopener">Forecasting menu</a> while also having an integration with <a href="/terminal/reference#oanda" target="_blank" rel="noreferrer noopener">Oanda</a>.

### How to use

The Forex menu is called upon by typing `forex` which opens the following menu:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218992918-54ea252b-d8b8-46e2-8da7-0b6d471f8a64.png"></img>

For example, you are able to show the quote of the currency pair by using the <a href="/terminal/reference/forex/quote" target="_blank" rel="noreferrer noopener">quote</a> command:

```
2022 Jun 29, 07:04 (🦋) /forex/ $ quote

                     USD/EUR Quote
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    ┃ Realtime Currency Exchange Rate ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ From_Currency Code │ USD                             │
├────────────────────┼─────────────────────────────────┤
│ To_Currency Code   │ EUR                             │
├────────────────────┼─────────────────────────────────┤
│ Last Refreshed     │ 2022-06-29 11:08:00             │
├────────────────────┼─────────────────────────────────┤
│ Exchange Rate      │ 0.94960000                      │
├────────────────────┼─────────────────────────────────┤
│ Bid Price          │ 0.94960000                      │
├────────────────────┼─────────────────────────────────┤
│ Ask Price          │ 0.94960000                      │
└────────────────────┴─────────────────────────────────┘
```

Or show the historical data on the currency pair with <a href="/terminal/reference/forex/candle" target="_blank" rel="noreferrer noopener">candle</a> as follows:

```
(🦋) /forex/ $ candle
```

Which returns the following:

![Candle of USDEUR](https://user-images.githubusercontent.com/46355364/176427844-7b99dc7d-5196-469d-af3a-538c7d7a8a59.png)

Lastly, insights in the forward valuations can also be given with <a href="/terminal/reference/forex/fwd" target="_blank" rel="noreferrer noopener">fwd</a>.

```
(🦋) /forex/ $ fwd

               Forward rates for USD/EUR
┏━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Expirations   ┃ Ask    ┃ Bid    ┃ Mid    ┃ Points    ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ Overnight     │ 0.9499 │ 0.9498 │ 0.9499 │ -0.5750   │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Tomorrow Next │ 0.9499 │ 0.9498 │ 0.9498 │ -0.7250   │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Spot Next     │ 0.9497 │ 0.9496 │ 0.9497 │ -2.3450   │
├───────────────┼────────┼────────┼────────┼───────────┤
│ One Week      │ 0.9495 │ 0.9495 │ 0.9495 │ -4.1550   │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Two Weeks     │ 0.9491 │ 0.9491 │ 0.9491 │ -8.2600   │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Three Weeks   │ 0.9487 │ 0.9486 │ 0.9487 │ -12.4150  │
├───────────────┼────────┼────────┼────────┼───────────┤
│ One Month     │ 0.9481 │ 0.9480 │ 0.9480 │ -18.8850  │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Two Months    │ 0.9459 │ 0.9458 │ 0.9458 │ -40.8200  │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Three Months  │ 0.9436 │ 0.9435 │ 0.9436 │ -63.4650  │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Four Months   │ 0.9415 │ 0.9414 │ 0.9415 │ -84.5500  │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Five Months   │ 0.9394 │ 0.9392 │ 0.9393 │ -106.2650 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Six Months    │ 0.9361 │ 0.9360 │ 0.9360 │ -138.8800 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Seven Months  │ 0.9342 │ 0.9340 │ 0.9341 │ -158.3750 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Eight Months  │ 0.9323 │ 0.9322 │ 0.9322 │ -176.9850 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Nine Months   │ 0.9302 │ 0.9300 │ 0.9301 │ -198.1200 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Ten Months    │ 0.9284 │ 0.9283 │ 0.9284 │ -215.5000 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Eleven Months │ 0.9268 │ 0.9267 │ 0.9268 │ -231.6250 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ One Year      │ 0.9252 │ 0.9250 │ 0.9251 │ -248.6650 │
├───────────────┼────────┼────────┼────────┼───────────┤
│ Two Years     │ 0.9111 │ 0.9106 │ 0.9109 │ -390.6350 │
└───────────────┴────────┴────────┴────────┴───────────┘
```

Furthermore, the ability exists to take the currency pair to the <a href="/terminal/usage/intros/common/ta" target="_blank" rel="noreferrer noopener">Technical Analysis</a> menu by typing `ta`.

### Examples

First, let's start with looking at the currency pair USD and GBP. These are the U.S. Dollars and the Pound sterling. This is done by using the `load` command as follows with the addition that the `-s` command is used to change the start date:

```
(🦋) /forex/ $ load USDGBP -s 2015-01-01
USD-GBP loaded.
```

Then, let's see how this currency pair has changed over the last years with `candle` also adding in the `--ma 60,120` argument:

![Candle with Moving Averages](https://user-images.githubusercontent.com/46355364/176427947-26346800-173b-4195-8a58-1add2a66ae31.png)

Now it's time to take this to the <a href="/terminal/usage/intros/common/qa" target="_blank" rel="noreferrer noopener">Quantitative Analysis</a> menu by typing `qa`. This returns the following. Within this menu we can show some rolling statistics, for example show the rolling values for the mean and standard deviation of the currency pair:

![Rolling Statistics for Forex](https://user-images.githubusercontent.com/46355364/176428039-4dcff70e-84e2-441d-9710-4d3f06af4175.png)

Lastly, more advanced techniques can also be applied regarding seasonality with `decompose`:

```
(🦋) /forex/qa/ $ decompose

Time-Series Level is 0.75
Strength of Trend: 421.7107
Strength of Seasonality: 0.0031
```

![Decompose Seasonality for Forex](https://user-images.githubusercontent.com/46355364/176428079-bdba5c17-5b3c-4e71-a92e-66aae2b787a1.png)
