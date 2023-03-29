---
title: Options Pricing
keywords: [Options, stocks, derivatives, puts, calls, oi, vol, greeks, hedge, gamme, delta, theta, rho, vanna, vomma, phi, charm, iv, volatility, implied, realized, price, last, bid, ask, expiry, expiration, chains, chain, put, call]
description: This guide introduces the user to the Options Pricing submenu, within the Options menu.
---

This set of features is for composing hypothetical outcomes through user-defined inputs. There are two columns of inputs: the price for the underlying at the close on expiration and the statistical probability of the outcome.

The Pricing submenu is accessible after selecting an<a href="/terminal/reference/stocks/options/exp" target="_blank" rel="noreferrer noopener">expiration</a> date for the options chain. Type, `pricing`, and press enter for access.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218987795-887c2f76-73f3-44ff-a6f5-35b392616186.png"></img>

## How to use

Use the `add` command to build the list, and use the `rmv` command to take away any entries. `show` will print a table of the inputs. Multiple price points can be added, assuming that probability always sums at 100%.

```
(🦋) /stocks/options/pricing/ $ add -p 125 -c 1


(🦋) /stocks/options/pricing/ $ show

Estimated price(s) of MSFT at 2023-02-17
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 125.00 │ 1.00   │
└────────┴────────┘
```

## Examples

Adding the optional argument, `-p`, will calculate the puts in the chain.

```
(🦋) /stocks/options/pricing/ $ rnval -p -m 70 -M 150 -r 1.25

            Risk Neutral Values
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Strike ┃ Last Price ┃ Value ┃ Difference ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ 110.00 │ 0.02       │ 0.00  │ 0.02       │
├────────┼────────────┼───────┼────────────┤
│ 115.00 │ 0.01       │ 0.00  │ 0.01       │
├────────┼────────────┼───────┼────────────┤
│ 120.00 │ 0.01       │ 0.00  │ 0.01       │
├────────┼────────────┼───────┼────────────┤
│ 125.00 │ 0.02       │ 0.00  │ 0.02       │
├────────┼────────────┼───────┼────────────┤
│ 130.00 │ 0.01       │ 4.98  │ -4.97      │
├────────┼────────────┼───────┼────────────┤
│ 135.00 │ 0.01       │ 9.96  │ -9.95      │
├────────┼────────────┼───────┼────────────┤
│ 140.00 │ 0.01       │ 14.93 │ -14.92     │
├────────┼────────────┼───────┼────────────┤
│ 145.00 │ 0.01       │ 19.91 │ -19.90     │
├────────┼────────────┼───────┼────────────┤
│ 150.00 │ 0.01       │ 24.89 │ -24.88     │
└────────┴────────────┴───────┴────────────┘
```
