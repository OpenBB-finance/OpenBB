---
title: Hedge
keywords: [options, stocks, derivatives, puts, calls, oi, vol, greeks, hedge, gamme, delta, theta, rho, vanna, vomma, phi, charm, iv, volatility, implied, realized, price, last, bid, ask, expiry, expiration, chains, chain, put, call, strategy, how to, example, expiration]
excerpt: This guide introduces the Hedge submenu, within the Options menu, providing examples in use.
---
The Hedge menu is designed to help the user calculate positions within the selected expiration chain to be directionally neutral. Enter the submenu after choosing the desired <a href="/terminal/reference/stocks/options/exp" target="_blank" rel="noreferrer noopener">expiration</a> date by using the command, `hedge`, from the Options menu.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218986900-da12b720-b7d9-4a80-9943-3060d7f79b62.png"></img>

### How to use

The first step is to pick the underlying position for the calculation. Scroll the list populated by autocomplete, or type in the choice.

```
(🦋) /stocks/options/hedge/ $ pick --pick 130_long_call
```

The strike prices for puts and calls are shown with the `list` command. Use this table to add or remove options from the calculation.

```
(🦋) /stocks/options/hedge/ $ list

    Available Calls and Puts
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Identifier ┃ Calls  ┃ Puts   ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ 0          │ 110.00 │ 110.00 │
├────────────┼────────┼────────┤
│ 1          │ 115.00 │ 115.00 │
├────────────┼────────┼────────┤
│ 2          │ 120.00 │ 120.00 │
├────────────┼────────┼────────┤
│ 3          │ 125.00 │ 125.00 │
├────────────┼────────┼────────┤
│ 4          │ 130.00 │ 130.00 │
├────────────┼────────┼────────┤
│ 5          │ 135.00 │ 135.00 │
├────────────┼────────┼────────┤
│ 6          │ 140.00 │ 140.00 │
├────────────┼────────┼────────┤
│ 7          │ 145.00 │ 145.00 │
├────────────┼────────┼────────┤
│ 8          │ 150.00 │ 150.00 │
├────────────┼────────┼────────┤
│ 9          │ 155.00 │ 155.00 │
├────────────┼────────┼────────┤
│ 10         │ 160.00 │ 160.00 │
├────────────┼────────┼────────┤

<continues>
```

Add the first option with the corresponding index number for the strike price, attaching flags for a put and for short, `-s` & `-p`.

```
(🦋) /stocks/options/hedge/ $ add 70

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃                    ┃ Positions ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Delta              │ 0.00      │
├────────────────────┼───────────┤
│ Gamma              │ 0.00      │
├────────────────────┼───────────┤
│ Vega               │ 0.00      │
├────────────────────┼───────────┤
│ Implied Volatility │ 0.50      │
├────────────────────┼───────────┤
│ Strike Price       │ 350.00    │
└────────────────────┴───────────┘

                   Current Option Positions
┏━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓
┃ Type ┃ Hold ┃ Strike ┃ Implied Volatility ┃ Cost ┃ Currency ┃
┡━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
│ Call │ Long │ 350.00 │ 0.50               │ 0.01 │ USD      │
└──────┴──────┴────────┴────────────────────┴──────┴──────────┘
```

`plot` will display an options payoff chart, using the provided values.

![Figure_1](https://user-images.githubusercontent.com/46355364/218987648-a5218bc4-8c27-49ce-9ca4-4275035d5525.png)
