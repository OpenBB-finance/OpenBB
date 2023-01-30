---
sidebar_position: 5
title: Scripts & Routines
description: The .openbb scripts offer the ability to automatically run a set of commands in the form of a **routine**. Furthermore, the scripts can be adapted, and documented, at any moment giving the user full control over the type of analysis you wish to do (and repeat). This can fundamental research, understanding market movements, finding hidden gems and even doing advanced statistical/econometric research.
keywords: [scripts, routines, .do file, stata, spss, r studio, python, automation, data collection, aggregation, script, routine, openbb terminal]
---
The `.openbb` scripts offer the ability to automatically run a set of commands in the form of a **routine**. Furthermore, the scripts can be adapted, and documented, at any moment giving the user full control over the type of analysis you wish to do (and repeat). This can fundamental research, understanding market movements, finding hidden gems and even doing advanced statistical/econometric research. 

The .openbb scripts offer a vast amount of capabilities to export data from the OpenBB Terminal directly into Excel files allowing students, professors, researchers and professionals to collect a a large dataset incredibly quick. For example, the GIF below demonstrates market data collection of all constituents of the S&P 500. Download the routine file [here](https://www.dropbox.com/s/3w8jgtzl0yoq9o9/sp500.openbb?dl=0) and place it in the `routines` folder as found in the `OpenBBUserData` folder and execute with `exe sp500.openbb`. Read on to understand in detail how to create and execute these type of files.

<iframe width="100%" height="450" src="https://www.youtube.com/embed/mKdXGEkgdOM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### Create your own script

Within the OpenBB Terminal, you have the option to record your own session with `record` which converts any commands you run in an .openbb script until you type `stop`. Find a short demonstration below.

<iframe width="100%" height="450" src="https://www.youtube.com/embed/dT_CcnyOpXQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

As shown in the video, scripts and routines reside in the `routines` folder within the `OpenBBUserData` folder (as found [here](https://docs.openbb.co/terminal/guides/advanced/data)) and are automatically shown when you type `exe` from the home screen (`home`).

:::note To manually create your own .openbb script use the following:
1. Download the file that can be used as a template [here](https://www.dropbox.com/s/73g9qx9xgtbb2ec/routines_template.openbb?dl=0).
2. Move the file inside the `routines` folder within the [OpenBBUserData](https://docs.openbb.co/terminal/guides/advanced/data) folder and, optionally, adjust the name to your liking.
3. Open the file with a Text Editor (e.g. Notepad or TextEdit) and adjust the file accordingly.
4. Open up the OpenBB Terminal, and type `exe --file`. The file should then be one of the options.
5. Select the file to run the routine script.
:::

As long as the file remains in the `routines` folder, you will be able to find your file automatically as shown below:

![Script Showcase](https://user-images.githubusercontent.com/46355364/213746605-53cfeb46-13f2-4550-b0fd-9de8a6d06bf1.png)

### Explanation of scripts

The script file follows the following logic:

- **Comments**: any text after a hashtag (`#`) is referred to as a comment. This is used to explain what is happening within the script and is not taking into account when running terminal commands.
- **Commands**: any text *without* a hashtag is being ran inside the OpenBB Terminal. E.g. on the second line it says `stocks` thus within the OpenBB Terminal the script will enter `stocks` and run this for you.

These scripts have a 1-to-1 relationship with how you would normally use the terminal. To get a better understanding of how the terminal is used, please see <a href="https://docs.openbb.co/terminal/guides/basics" target="_blank" rel="noreferrer noopener">Structure of the OpenBB Terminal</a>. The example below can be executed by running `exe --example`.

```
# Go into the stocks context
stocks

# Load a company ticker, e.g. Apple
load AAPL

# Show a candle chart with a 20 day Moving Average
candle --ma 20

# Switch over to the Due Diligence menu
dd

# Show analyst ratings
analyst

# Show price targets charts
pt

# Show future estimations
est

# Return to home
home
```

### Executing a script

By going to the main menu as depicted below (accessible with `home`), the `exe` command can be used. With this command you can run any `.openbb` script. These scripts are located where the application is located inside the `routines` folder as found in the `OpenBBUserData` folder.

Thus, using the earlier mentioned script, we can enter `exe --file routines_template.openbb` which automatically runs all commands within the script file. Thus, it will return a candle chart with a moving average of 20 days, expectations and price targets from analysts and estimated future performance before returning to the home window.

![OpenBB Routine Script Execution](https://user-images.githubusercontent.com/46355364/213746495-6b38ab67-1d90-46b1-898f-9df1ce4063c0.png)

### Custom arguments

Next to that, it is also possible to add in custom arguments to your script making the script more interactive and allow you to do the same analysis for multiple companies. This is done in the following script (and can be downloaded [here](https://www.dropbox.com/s/usooz6y29r1xldb/routines_template_with_inputs.openbb?dl=0):

```
# This script requires you to use arguments. This can be done with the following:
# exe --file routines_template_with_inputs.openbb -i TSLA,AAPL,MSFT

# Go to the stocks menu
stocks

# Load a ticker, given the argument used. E.g. -i TSLA
load $ARGV[0]

# Enter the Technical Analysis (ta) menu
ta

# Show the fibonacci retracement levels
fib

# Enter the comparison analysis (ca) menu
../ca

# Set two extra tickers based on the arguments used. E.g. -i TSLA,AAPL,MSFT
add $ARGV[1],$ARGV[2]

# Plot the historical prices
historical

# Return to home
home
```

This script includes `$ARGV[0]`, `$ARGV[1]` and `$ARGV[2]`. This means that the script requires you to submit three arguments. In this case, they refer to <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank" rel="noreferrer noopener">stock tickers</a>. Therefore, like the script also says, you can include these arguments with `-i` followed by three tickers (e.g. `exe example_with_inputs.openbb -i TSLA,AAPL,MSFT`). This results in the following:

![OpenBB Script with Input](https://user-images.githubusercontent.com/46355364/213747540-1907ffdb-1950-42a7-bb5b-8482777a9763.png)

It is an incredibly simple script, but it gives an understanding what the possibilities are. Do make sure you saved this script in the `routines` folder else you are not able to execute it.
