---
title: Options Pricing
keywords: ["Options", "stocks", "derivatives", "puts", "calls", "oi", "vol", "greeks", "hedge", "gamme", "delta", "theta", "rho", "vanna", "vomma", "phi", "charm", "iv", "volatility", "implied", "realized", "price", "last", "bid", "ask", "expiry", "expiration", "chains", "chain", "put", "call"]
excerpt: "This guide introduces the user to the Options Pricing submenu, within the Options menu."
---

This set of features is for composing hypothetical outcomes through user-defined inputs. There are two columns of inputs: the price for the underlying at the close on expiration and the statistical probability of the outcome.

The Pricing submenu is accessible after selecting an<a href="/terminal/reference/stocks/options/exp" target="_blank" rel="noreferrer noopener">expiration</a> date for the options chain. Type, `pricing`, and press enter for access.

![The Options Pricing Submenu](https://user-images.githubusercontent.com/85772166/172729310-dd341d26-c55e-4e29-a190-3e1eea1a6950.png)

### How to use

Use the `add` command to build the list, and use the `rmv` command to take away any entries.

![Add and remove](https://user-images.githubusercontent.com/85772166/172732199-cb6f0cc9-0713-4bab-8e0c-5cd3e458f74a.png)

`show` will print a table of the inputs. Multiple price points can be added, assuming that probability always sums at 100%.

![Calculated outputs for calls](https://user-images.githubusercontent.com/85772166/172732726-09fcdcda-cb2a-46fd-ba0b-23c3b27c6067.png)

<h2>Examples</h2>

Adding the optional argument, `-p`, will calculate the puts in the chain.

![Calculating for puts](https://user-images.githubusercontent.com/85772166/172733009-5a58a7f2-577d-4599-956e-29df2cdb3f91.png)

Removing the risk-free rate variable makes a substantial difference to the calculated value of an option.

![Puts calculations with RFR = 0](https://user-images.githubusercontent.com/85772166/172733137-8588b7a5-6384-4ba4-9d3c-943a10af280d.png)

RFR as 0 for call options

![RFR as 0 for call options](https://user-images.githubusercontent.com/85772166/172734277-223f855a-8ad1-4f45-ad5b-0a1d92d94290.png)