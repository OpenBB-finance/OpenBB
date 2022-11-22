---
title: Introduction to the Stock Screener
keywords: "screen, screener, stock, stocks, historical, overview, valuation, financial, ownership, performance, technical, view, set, preset, presets, ini, scan, compare, tickers, metrics"
date: "2022-06-13"
type: guides
status: publish
excerpt: "This guide introduces the Stock Screener, within the Stocks menu, briefly explains the features, and shows examples in context."
geekdocCollapseSection: true
---

The Stock Screener is a diverse tool for discovery. Screeners are typically deployed in the preliminary phase of research; they provide creative methods for finding individual companies meeting the criteria of the investment thesis. There are categories of statistics to use as metrics to sort the criteria defined in the preset file. The preset files are `.ini` files stored locally in the application folder: `~\Applications\OpenBB\openbb_terminal\stocks\screener\presets\` and they can be modified in any text editor. Create custom presets and share them with the world!

Get to the Stock Screener from the `Stocks` menu by typing `scr` and then pressing `enter`

<img width="1412" alt="The Stock Screener submenu" src="https://user-images.githubusercontent.com/85772166/173902919-2577b42a-f46a-4734-b153-9ccf498e3443.png">

<h2>How to use the Stock Screener</h2>

The default preset is `top_gainers`. Use the commands `view` and `set` to select a new one. The file in the presets folder, `template.ini`, is a blank slate for creating something fresh. Modify individual parameters within the different presets to get more precision from a starting point. To get started, simply choose one of the categories to scour, like `technical`.

<img width="1408" alt="Unusual Volume preset and the Technical category" src="https://user-images.githubusercontent.com/85772166/173902993-33ae5c4d-67bb-46ad-909f-ad376c16b5f9.png">

The columns can be sorted with the optional argument `-s`, and autocomplete will present a list of choices.

<img width="1132" alt="Sorting results" src="https://user-images.githubusercontent.com/85772166/173903096-0643a64f-4482-4de9-832b-d654af532a10.png">

To see a description of each preset, use `view`, and autocomplete will allow the user to scroll presets with the arrow keys to `set` the choice.

<img width="1412" alt="Autocomplete with the set function" src="https://user-images.githubusercontent.com/85772166/173903152-c59f37f7-9b90-47ee-8ad1-87bb5939caa0.png">

Unexpected results can be obtained through combining presets with the category of screen.

<h2>Examples</h2>

Using the `modified_dremin` preset and the `financial` category, then sorting for return-on-investment.

![modified_dremin preset with the financial category](https://user-images.githubusercontent.com/85772166/173903472-79988a7d-999e-454b-a7f9-96b071e3337a.png)

Setting the preset to `short_squeeze_scan` and scanning with the `ownership` category.

![Short squeeze scan and the ownership category](https://user-images.githubusercontent.com/85772166/173903741-4823f6ac-91f0-4e57-9fa1-a465af43a4f9.png)

`set triangle_ascending`, show `techincal` & `overview`

![triangle_ascending preset with technical and overview categories](https://user-images.githubusercontent.com/85772166/173903827-15d6852e-90bf-4ea3-b008-47ce3c482380.png)

Enter `exe stock_screener_demo.openbb` from the main menu to play a demonstration of the Stock Screener in the Terminal.

Back to the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Introduction Guide to the Stocks Menu</a>
