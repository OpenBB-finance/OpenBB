---
title: Introduction to the Options Menu
keywords: "Options, stocks, derivatives, puts, calls, oi, vol, greeks, voi, volatility, vsurf, chains, parity, binom, screen, pricing, hedge, pcr, info, hist, grhist, plot, parity"
date: "2022-06-07"
type: guides
status: publish
excerpt: "This guide introduces the user to Options submenu, within the Stocks menu."
geekdocCollapseSection: true
---

The Options menu provides the user with a comprehensive set of tools for analyzing equity options. This guide provides an overview of the menu and demonstrates commands in context. Using this menu correctly will require understanding terminology and math specific to the asset class. Wikipedia is a great resource for definitions and for learning about the mechanics of derivatives, read it <a href="https://en.wikipedia.org/wiki/Option_(finance)" target="_blank">here</a>. These are complex, leveraged, financial instruments requiring specialized knoweledge and a different frame-of-mind than the approach of an equities long-only investor. Always conduct thorough due diligence.<br>

<h2>Submenus Available</h2>

At the bottom of the menu, and near the top, there are items prefaced with `>`. Like everywhere else in the OpenBB Terminal, this indicates the presence of a submenu.<br>

  - `screen` is a dedicated options screener that uses `.ini` files from the local installation folder `/OpenBBTerminal/openbb_terminal/stocks/options/presets/`. Refer to the Options Screener Guide <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/screen/" target="_blank">here</a>.

  - `pricing` is another method for calculating options prices. See the guide for this submenu <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/pricing/" target="_blank">here</a>. 

  - `hedge` is a group of features for calculating a delta-neutral position. The guide for this submenu is located <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/hedge/" target="_blank">here</a>.

<h2>How to use the Options Menu</h2>

Navigate to the menu by typing `options`, from the `Stocks` menu, and then pressing enter. Alternatively, absolute path navigation can jump straight there, from anywhere. `/stocks/options`

![The Options Menu](https://user-images.githubusercontent.com/85772166/172717122-a857dd69-6e79-4773-996a-74ea71f8ee86.png)

<h3>Market Coverage and Data Sources</h3>

At the time of writing, OpenBB is able to provide coverage only for US-listed equity and ETF options. While not officially supported, some additional markets and index options may be accessible with yFinance as the source. Coverage will be added as the product grows to incorporate more community contributions but, for now, it is safe to generalize equity options as referring to US-listed companies on a major exchange and are priced in $USD.<br></br>
By default, the Terminal loads a ticker using <a href="https://developer.tradier.com/" target="_blank">Tradier</a> as the source. It's not perfect but the price is right. Sign up for a free developer account and then enter that token using the <a href="https://openbb-finance.github.io/OpenBBTerminal/#accessing-other-sources-of-data-via-api-keys" target="_blank">`keys`</a> function. Alternatively, there is a choice to use yFinance data sets by attaching the argument as shown below. Help dialogues are displayed for any command by adding `-h` to the string. It is worth noting that this load command is different than the load command elsewhere. 
````
(🦋) /stocks/options/ $ load -h
usage: load [-t TICKER] [-s {tr,yf}] [-h]

Load a ticker into option menu

optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s {tr,yf}, --source {tr,yf}
                        Source to get option expirations from (default: None)
  -h, --help            show this help message (default: False)
````

Having the working foundation of knowledge will make most commands, as pictured above, somewhat intuitive. `-h` is attachable to any command to print the help dialogue in the Terminal. Refer to the <a href="https://openbb-finance.github.io/OpenBBTerminal/" target="_blank">user documentation</a> for details on any individual feature. Browse the commands on the left side of the page to read about any particular command.

<h2>Examples</h2>

To begin, a ticker must be loaded with an expiration date selected. Enter these commands to display the list of expiration dates for AAPL options chains.
````
(🦋) /stocks/options/ $ load aapl

(🦋) /stocks/options/ $ exp

   Available expiry dates   
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Identifier ┃ Date       ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 0          │ 2022-05-20 │
├────────────┼────────────┤
│ 1          │ 2022-05-27 │
├────────────┼────────────┤
│ 2          │ 2022-06-03 │
├────────────┼────────────┤
│ 3          │ 2022-06-10 │
├────────────┼────────────┤
│ 4          │ 2022-06-17 │
├────────────┼────────────┤
│ 5          │ 2022-06-24 │
├────────────┼────────────┤
│ 6          │ 2022-07-01 │
├────────────┼────────────┤
│ 7          │ 2022-07-15 │
├────────────┼────────────┤
│ 8          │ 2022-08-19 │
├────────────┼────────────┤
│ 9          │ 2022-09-16 │
├────────────┼────────────┤
│ 10         │ 2022-10-21 │
├────────────┼────────────┤
│ 11         │ 2022-11-18 │
├────────────┼────────────┤
│ 12         │ 2022-12-16 │
├────────────┼────────────┤
│ 13         │ 2023-01-20 │
├────────────┼────────────┤
│ 14         │ 2023-03-17 │
├────────────┼────────────┤
│ 15         │ 2023-06-16 │
├────────────┼────────────┤
│ 16         │ 2023-09-15 │
├────────────┼────────────┤
│ 17         │ 2024-01-19 │
├────────────┼────────────┤
│ 18         │ 2024-06-21 │
└────────────┴────────────┘
````
Choose an expiration date with the corresponding Identifier value on the left.

````
(🦋) /stocks/options/ $ exp 16
Expiration set to 2023-09-15 
````
Setting the chain for analysis will change the text colour at the bottom of the Options menu. These commands require loaded data.

![The Options menu with a loaded ticker and expiration date](https://user-images.githubusercontent.com/85772166/172724623-dbb16566-5dfa-482c-a67e-948e01444ca8.png)

The `info` command displays a table of notable statistics.
````
(🦋) /stocks/options/ $ info

                Options Information                
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Info                  ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Implied Volatility    │   38.07%  (  -1.48%)    │
├───────────────────────┼─────────────────────────┤
│ Historical Volatility │   42.90%                │
├───────────────────────┼─────────────────────────┤
│ IV Percentile         │   95%                   │
├───────────────────────┼─────────────────────────┤
│ IV Rank               │   78.41%                │
├───────────────────────┼─────────────────────────┤
│ IV High               │   43.37% on 04/26/22    │
├───────────────────────┼─────────────────────────┤
│ IV Low                │   18.80% on 06/11/21    │
├───────────────────────┼─────────────────────────┤
│ Put/Call Vol Ratio    │  0.81                   │
├───────────────────────┼─────────────────────────┤
│ Today's Volume        │  2,045,793              │
├───────────────────────┼─────────────────────────┤
│ Volume Avg (30-Day)   │  1,293,501              │
├───────────────────────┼─────────────────────────┤
│ Put/Call OI Ratio     │  0.88                   │
├───────────────────────┼─────────────────────────┤
│ Today's Open Interest │  8,226,541              │
├───────────────────────┼─────────────────────────┤
│ Open Int (30-Day)     │  7,576,733              │
└───────────────────────┴─────────────────────────┘
````
An adjustable-period put/call ratio chart is called according to the timeline selected by the user.

  - Length of 180 days:<br>
````
(🦋) /stocks/options/ $ pcr 180
````
![180 day window for put/call ratio](https://user-images.githubusercontent.com/85772166/172721035-2c1b3191-430a-4bb4-86be-f932abb87215.png)

  - Length of 90 days:<br>
````
(🦋) /stocks/options/ $ pcr 90
````
![90 day window for put/call ratio](https://user-images.githubusercontent.com/85772166/172721388-4fa23c20-6813-4bcd-bc4f-964ff8562112.png)

  - Length of 30 days:<br>
````
(🦋) /stocks/options/ $ pcr 30
````
![30 day window for put/call ratio](https://user-images.githubusercontent.com/85772166/172721482-d7d32681-850e-4d01-b9bb-ca9a59bf83e6.png)

  - Length of 10 days:<br>
````
(🦋) /stocks/options/ $ pcr 10
````
![10 day window for put/call ratio](https://user-images.githubusercontent.com/85772166/172721584-a953166e-b923-4bb6-ab98-ee777f087add.png)

The chain's open interest and current volume can be visualized with, `voi`
````
(🦋) /stocks/options/ $ voi
````
![Volume & Open Interest](https://user-images.githubusercontent.com/85772166/172721788-cc801a19-9625-4180-b948-46d4a51da343.png)

The `chains` command will display pricing, volume, open interest, and greeks data as a snapshot.
````
(🦋) /stocks/options/ $ chains
````
![chains command](https://user-images.githubusercontent.com/85772166/172721931-7d1b98f6-ebc5-44ae-8feb-e045f963c40c.png)

Narrow the focus with min/max filters:
````
(🦋) /stocks/options/ $ chains -m 50 -M 100
````
![Chains command with min/max filters](https://user-images.githubusercontent.com/85772166/172722075-565c0465-18ac-4426-98a7-54eaa331ef81.png)

Additional Greeks are accessible through the command, `greeks`
````
(🦋) /stocks/options/ $ greeks
````
![greeks command](https://user-images.githubusercontent.com/85772166/172722192-37dafb44-5267-495a-b158-afaabd911593.png)

See the effects of monetary policy by adjusting for the risk-free rate of return, and factor in dividend payments.

 <a href="https://www.investopedia.com/ask/answers/042215/what-does-positive-theta-mean-credit-spreads.asp" target="_blank">Investopedia</a>
```
"Credit spreads naturally carry a positive theta, meaning they benefit from the passage of time."
```
````
(🦋) /stocks/options/ $ greeks -d 0.67 -r 1 -m 50 -M 200 -a
````
Greeks for Apple Sep/23 calls, using a RFR of 1% and dividend yield of 0.67%

![Options greeks with adjustments](https://user-images.githubusercontent.com/85772166/172722357-6389fdc7-19ed-4960-900c-9bd9953630e2.png)

`binom` will calculate options values using <a href="https://en.wikipedia.org/wiki/Binomial_options_pricing_model" target="_blank">binomial pricing models</a>.

Display a probabilities distribution chart using the optional argument `--plot`
````
(🦋) /stocks/options/ $ binom --plot
````
![Probabilities distribution using binomial pricing, for AAPL options expiring Sep/23](https://user-images.githubusercontent.com/85772166/172722694-9a4b782e-9ec5-4b47-a31a-e5b9dd04eeba.png)

Visualize the volume of puts and calls in a chain with `vol`
````
(🦋) /stocks/options/ $ vol -m 0 -M 250
````
![Puts and calls volume for AAPL 09/23 expiration](https://user-images.githubusercontent.com/85772166/172722818-1cdf1d8c-2a8a-4ede-a455-041b3066dcb3.png)

Plot the open interest in a similar fashion with `oi`
````
(🦋) /stocks/options/ $ oi
````
![Open interest for AAPL expiring 2023-09-15](https://user-images.githubusercontent.com/85772166/172722959-edab3c32-a3f3-47db-80be-a33e382ddd9a.png)

Historical OHLC pricing for individual contracts can be viewed with `hist`
````
(🦋) /stocks/options/ $ hist -p -s 70
````
![Price history for AAPL $70 put expiring 2023-09-15](https://user-images.githubusercontent.com/85772166/172723074-cd013225-9fc9-4eeb-adeb-ccc8a99f661a.png)

Plot the hisotorical greek data with, `grhist`
````
(🦋) /stocks/options/ $ grhist -s 70 -p -g rho
````
![Historical Rho for $70 09/23 AAPL Put](https://user-images.githubusercontent.com/85772166/172723243-71b7e323-c3c4-4c7e-a463-f56d916a87fe.png)

`plot` gives the user flexibility to chart different variables.
````
(🦋) /stocks/options/ $ plot -p -x ltd -y s
````
![Stike vs Last Trade Date for Apple puts expiring Sep/23](https://user-images.githubusercontent.com/85772166/172723361-e57c656a-2202-4822-abc0-080c5f99d3e4.png)

Show the volatility surface of the entire chain using the command, `vsurf`
````
(🦋) /stocks/options/ $ vsurf
````
![Volatility surface of QQQ](https://user-images.githubusercontent.com/85772166/172723670-f1e3bc37-2655-4414-b0cb-3e173b48825d.png)

<h2>Additional Resources for Equity Options</h2>

<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/screen/" target="_blank">Introduction to the Options Screener</a>

<a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/hedge/" target="_blank">Introduction to the Options Hedge Menu</a>

<a href="https://www.investopedia.com/options-basics-tutorial-4583012" target="_blank">Investopedia's Options Basics Tutorial</a>
