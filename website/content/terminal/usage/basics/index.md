---
title: Basics
description: The OpenBB Terminal is a modern investment research platform for everyone. It is a desktop application that allows you to access all the data and tools you need to make better investment decisions.
keywords: [basics, installation, commands, menus, your own data, introduction, openbb terminal, explanation, basic usage, usage, how to]
---

The OpenBB Terminal is based off the <a href="https://en.wikipedia.org/wiki/Command-line_interface" target="_blank" rel="noreferrer noopener">Command Line Interface (CLI)</a>
which is installed by default on every computer. By opening the application you have installed from the [Installation Page](/terminal/installation/windows),
you are greeted with the following interface:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/223211150-5c0bce44-98f3-403c-9db1-2344c1ad79d4.png"></img>

The OpenBB Terminal is centered around keyboard input. To navigate and perform analysis you will have to type in the name of the command followed by an `ENTER` (⏎). If you wish to see information about the OpenBB Terminal you can do so by typing `about` and then press `ENTER` (⏎). As you are typing, you will notice that you receive suggestions, by using the `DOWN` (⌄) arrow and pressing `ENTER` (⏎) you can select the command and execute it.

Throughout the entire terminal, the same set of colors are used which all share the same representation. This is structured as follows:

- <b><span style={{color:"#00AAFF"}}>Light Blue</span></b>: represents commands.
- <b><span style={{color:"#005CA9"}}>Dark Blue</span></b>: represents menus, also recognizable by the `>` in front.
- <b><span style={{color:"#EF7D00"}}>Orange</span></b>: represents titles and headers.
- <b><span style={{color:"#FCED00"}}>Yellow</span></b>: represents descriptions of a parameter or variable.
- <b>White</b>: represents text, usually in combination with a description that is in Yellow.

### Explanation of Menus

Menus, depicted in <b><span style={{color:"#005CA9"}}>Dark Blue</span></b>, take you to a new section of the terminal referred to as a menu. For example, if you wish to view information about stocks, you can do so by typing `stocks` and pressing `ENTER` (⏎). This opens a new menu as depicted below.

<img width="800" alt="Explanation of Menus" src="https://user-images.githubusercontent.com/46355364/225117373-93787a40-cb26-4599-86b7-7bd023b31e4b.png"></img>

Depending on the menu you are in, you are presented with a new set of commands and menus you can select. There are interactions in place between each menu. For example, when selecting a company within the `stocks` menu, the terminal will remember your selection when you visit the `fa` or `options` menu. See [Introduction to Stocks](/terminal/usage/intros/stocks).

:::note **About Pipelines**
You can quickly jump between menus by using a forward slash (`/`). For example, if I want to access the options menu, You can type `/stocks/options` to instantly arrive at this menu. You can do this from any location within the OpenBB Terminal!
:::

### Explanation of Commands

Commands, depicted in <b><span style={{color:"#00AAFF"}}>Light Blue</span></b>, execute an action or task. For example,
the commands that you are able to use from any menu in the terminal (see <a href="#explanation-of-menus">Explanation of Menus</a>) are as follows:

- `cls`: clears the screen, by executing this command you are left with an empty screen.
- `help`, `h` or `?`: displays the menu that you are currently on.
- `quit`, `q` or `..`: allows for navigation through the menu. E.g. if you type `stocks` press `ENTER` (⏎) and then
  use `q` and press `ENTER` (⏎) you return to where you started. Validate this by typing `?` and pressing `ENTER` (⏎).
- `support`: allows you to submit bugs, questions and suggestions.
- `about`: this opens the related guide, linking to this website. It also has the ability to open a guide to a specific
  command. For example, within the `stocks` menu, `about candle` opens <a href="/terminal/reference/stocks/candle/" target="_blank" rel="noreferrer noopener">this guide</a>.
- `wiki`: search for a given expression on the Wikipedia without leaving the terminal.

Continuing with the example mentioned at `quit`, revisit the `stocks` menu and look at the commands. At the top you will see a command named <a href="/terminal/reference/stocks/load" target="_blank" rel="noreferrer noopener">load</a>. To understand what this command can do, you can use `load -h` followed by `ENTER` (⏎). The `-h` stands for `help` and every command will have this feature. This will return the following:

```
usage: load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [-p] [-f FILEPATH] [-m] [-w] [--exchange] [--performance] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]
            [--source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}]

Load stock ticker to perform analysis on. When the data source is yf, an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in https://help.yahoo.com/kb/exchanges-data-
providers-yahoo-finance-sln2310.html.

optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-02-11)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2023-02-15)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  -p, --prepost         Pre/After market hours. Only reflected in 'YahooFinance' intraday data. (default: False)
  -f FILEPATH, --file FILEPATH
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  --exchange            Show exchange information. (default: False)
  --performance         Show performance information. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  --source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}
                        Data source to select from (default: YahooFinance)

For more information and examples, use 'about load' to access the related guide.

```

This shows you all **arguments** the command has. These are additional options you can provide to the command. Each default value is also displayed which is used when you do not select this option. For example, if I would use the <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank" rel="noreferrer noopener">stock ticker</a> of Amazon (AMZN, which can also be found with `search amazon`), I can use `load AMZN` which will return the following:

```
(🦋) /stocks/ $ load AMZN

Loading Daily data for AMZN with starting period 2020-02-11.

```

The default values you see within `load -h` have been inputted here. E.g. the starting period is 2020-02-11. I can decide to change these default values by calling the argument and inputting a different value.

Whenever you wish to apply an optional argument, you use the related shortcode, e.g. `-s` or `--start`. Then, if there is an additional word behind the argument (in this case there is, which is `START`) it implies the argument expects you to define a value. Within the documentation you can read that the format must be `YYYY-MM-DD` implying that `2010-01-01` will be valid. If there is not an additional word behind it, it is enough to write down `load AMZN -p` (which refers to the prepost optional argument)

Let's change the starting and ending period of the data that is being loaded in by doing the following:

```
(🦋) /stocks/ $ load AMZN -s 2005-01-01 -e 2010-01-01

Loading Daily data for AMZN with starting period 2005-01-03.

```

We can check that this period has changed by looking into the <a href="https://www.investopedia.com/trading/candlestick-charting-what-is-it/" target="_blank" rel="noreferrer noopener">candle chart</a> with `candle`. This, again shares the same `-h` argument. This results in the following which indeed depicts our selected period.

```
(🦋) /stocks/ $ candle
```

![Candlestick Chart Amazon](https://user-images.githubusercontent.com/46355364/223211728-1317abea-36da-461c-bc3b-140ed7973173.svg)

As mentioned in the <a href="#explanation-of-menus">Explanation of Menus</a>, some information also transfers over to other menus and this includes the loaded market data from <a href="/terminal/reference/stocks/load" target="_blank" rel="noreferrer noopener">load</a>. So, if you would visit the `ta` menu (which stands for <a href="https://www.investopedia.com/terms/t/technicalanalysis.asp" target="_blank" rel="noreferrer noopener">Technical Analysis</a>) you will see that, by running any command, the selected period above is depicted again. Return to the Stocks menu again by using `q` and use it again to return to the home screen which can be shown with `?`.
