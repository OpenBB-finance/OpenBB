---
title: Introduction to the Hedge Submenu
keywords: "Options, stocks, derivatives, puts, calls, oi, vol, greeks, hedge, gamme, delta, theta, rho, vanna, vomma, phi, charm, iv, volatility, implied, realized, price, last, bid, ask, expiry, expiration, chains, chain, put, call, strategy"
date: "2022-06-06"
type: guides
status: publish
excerpt: "This guide introduces the Hedge submenu, within the Options menu, providing examples in use."
geekdocCollapseSection: true
---
<h1>Introduction to the Hedge Submenu</h1>

The Hedge menu is designed to help the user calculate positions within the selected expiration chain to be directionally neutral. It is worth reviewing reference material, such as <a href="https://en.wikipedia.org/wiki/Hedge_(finance)#Delta_hedging" target="_blank">Wikipedia</a> or <a href="https://www.investopedia.com/terms/d/deltahedging.asp" target="_blank">Investopedia</a>, before using this feature set.

Enter the submenu after choosing the desired <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/exp/" target="_blank">expiration</a> date by using the command, `hedge`, from the Options menu.

![The Options Hedge Submenu](https://user-images.githubusercontent.com/85772166/172286199-ec6e202d-4955-4557-9ba6-7d4db6fbdd55.png)

<h2>How to use the Hedge Submenu</h2>

The first step is to pick the underlying position for the calculation. Scroll the list populated by autocomplete, or type in the choice.

![Picking underlying position](https://user-images.githubusercontent.com/85772166/172286267-9c164764-271f-4847-adc7-52bfb82e1138.png)

The strike prices for puts and calls are shown with the `list` command. Use this table to add or remove options from the calculation.

![List of strikes](https://user-images.githubusercontent.com/85772166/172286323-62e69fe1-dc37-42a1-8fdb-d3287ff0ac38.png)

Add the first option with the corresponding index number for the strike price, attaching flags for a put and for short, `-s` & `-p`.

![Adding Option A to the calculation](https://user-images.githubusercontent.com/85772166/172286367-a15f57fe-a10f-402c-9bf6-5e7dd34dedb4.png)

The `rmv` command removes added options. With an underlying position and two positions added, `sop` will display the results based on the inputs provided.

![Position sizing for delta neutral](https://user-images.githubusercontent.com/85772166/172286429-a0d6710d-a5a0-49e5-9938-f3b9aaebb236.png)

`plot` will display an options payoff chart, using the provided values.

![Options payoff diagram](https://user-images.githubusercontent.com/85772166/172286525-4ede89ec-4ed7-4843-a0fa-ec306efe3b67.png)

<h2>Examples</h2>

Substituting Option A for a different trade.

![Hedge Example](https://user-images.githubusercontent.com/85772166/172286582-1f5e153a-a900-427a-a7fc-f596648de599.png)

Substuting Option B from the same example above.

![Hedge Example](https://user-images.githubusercontent.com/85772166/172286627-0f6f6a60-d76c-4e24-9fdd-8e65e137097e.png)

Moving Option B down one strike.

![Hedge Example](https://user-images.githubusercontent.com/85772166/172286669-82a98127-fe74-43fd-bcc9-ed874f746bdc.png)

Back to: <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/options/" target="_blank">Introduction To Options</a>

