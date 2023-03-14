---
sidebar_position: 3
title: Scripts & Routines
description: OpenBB Routine files, `.openbb`, are simple scripts for automating processes and repetitive tasks. They represent a 1:1 relationship with any command in the OpenBB Terminal; one line represents one function. A routine file can be created or modified in any basic text editor, the only difference between a plain-text file and an OpenBB Routine file is the `.openbb` file extension. Additionally, routine files can be captured with the macro recorder, controlled with global commands, `record` & `stop`. Upon `stop`, the script is automatically saved to the, `~/OpenBBUserData/routines/`, folder.  Routine files stored there are callable from the main menu, using the `exe` function. By deploying variable arguments - `$ARGV[0]` - to any line in the script, dates, symbols, exported filenames, or any Terminal function argument, scripts become dynamic.
keywords: [scripts, routines, .do file, stata, spss, r studio, python, automation, data collection, aggregation, script, routine, openbb terminal]
---
OpenBB Routine Scripts, `.openbb`, are simple scripts for automating processes and repetitive tasks. They represent a 1:1 relationship with any command in the OpenBB Terminal; one line represents one function. A routine file can be created or modified in any basic text editor, the only difference between a plain-text file and an OpenBB Routine file is the `.openbb` file extension. Additionally, routine files can be captured with the macro recorder, controlled with global commands, `record` & `stop`. Upon `stop`, the script is automatically saved to the, `~/OpenBBUserData/routines/`, folder.  Routine files stored there are callable from the main menu, using the `exe` function. By deploying variable arguments - `$ARGV[0]` - to any line in the script, dates, symbols, exported filenames, or any Terminal function argument, scripts become dynamic.

Run a routine file from the main menu, with the `exe` command. Below, the `--help` dialogue is displayed.

```console
usage: exe [--file PATH] [-i ROUTINE_ARGS] [-e] [-h]

Execute automated routine script. For an example, please use `exe --example` and for documentation and to learn how create your own script type `about exe`.

options:
  --file PATH           The path or .openbb file to run. (default: None)
  -i ROUTINE_ARGS, --input ROUTINE_ARGS
                        Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD (default: None)
  -e, --example         Run an example script to understand how routines can be used. (default: False)
  -h, --help            show this help message (default: False)
```

Other software like STATA, SPSS and R-Studio share similar functionality in the area of Econometrics and the OpenBB routine scripts venture into the area of financial analysis and data collection to speed up the process. For example, not only is it possible to automate a set of functionality, it is also possible to export a large amount of data to Excel through the usage of `--export` and `--sheet-name` making data collection efficient, reproducible and customizable.

## The Macro Recorder

As a starting point, you can use the `record` and `stop` functionalitsy. This shares similarities with that of Excel's VBA methods. This means that any command you run will be automatically recorded for the routine script and once you type `stop` it automatically saves the file. For example, if you cope the following code in the OpenBB Terminal and run it, you will see an example.

```console
record/economy/cpi/treasury/index sp500/stop
```

The following shows the script being ran and the charts that are created because of it.

![Routines](https://user-images.githubusercontent.com/46355364/223204998-70d9e5da-f84e-4c22-90c4-576dcf87c1df.png)

After the script is finished, you are able to access the routine file when using `exe --file`. The naming of the file can differ for you based on the time you are executing the script. You can find this script inside the `routines` folder within the `OpenBBUserData` folder (as found [here](https://docs.openbb.co/terminal/guides/advanced/data)) 

![Routines](https://user-images.githubusercontent.com/46355364/223205394-77e7a33d-e9fa-4686-b32f-e8d183b265e6.png)

## Create your own script

As mentioned earlier, the scripts and routines reside in the `routines` folder within the `OpenBBUserData` folder (as found [here](https://docs.openbb.co/terminal/guides/advanced/data)) and are automatically shown when you type `exe` from the home screen (`home`).

:::note To manually create your own .openbb script use the following:
1. Download the file that can be used as a template **[here](https://www.dropbox.com/s/73g9qx9xgtbb2ec/routines_template.openbb?dl=1)**.
2. Move the file inside the `routines` folder within the [OpenBBUserData](https://docs.openbb.co/terminal/guides/advanced/data) folder and, optionally, adjust the name to your liking.
3. Open the file with a Text Editor (e.g. Notepad or TextEdit) and adjust the file accordingly.
4. Open up the OpenBB Terminal, and type `exe --file`. The file should then be one of the options.
5. Select the file to run the routine script.
:::

As long as the file remains in the `routines` folder, you will be able to find your file automatically as shown below. Note that this also shows the script that was created within [The Macro Recorder](#the-macro-recorder) section.

![Script Showcase](https://user-images.githubusercontent.com/46355364/223206633-abebdee3-9221-49b1-a55e-5221572e9781.png)

## Explanation of scripts

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

# Switch over to the Fundamental Analysis menu
fa

# Show Earnings per Share (EPS) estimates
epsfc

# Show price targets charts
pt

# Show future estimations
est

# Return to home
home
```

## Executing a script

By going to the main menu as depicted below (accessible with `home`), the `exe` command can be used. With this command you can run any `.openbb` script. These scripts are located where the application is located inside the `routines` folder as found in the `OpenBBUserData` folder.

Thus, using the earlier mentioned script, we can enter `exe --file routines_template.openbb` which automatically runs all commands within the script file. Thus, it will return a candle chart with a moving average of 20 days, expectations and price targets from analysts and estimated future performance before returning to the home window.

![OpenBB Routine Script Execution](https://user-images.githubusercontent.com/46355364/223207167-dfab3a74-d34d-47d4-bf6e-44944e8fbfa2.png)

## Custom arguments

Next to that, it is also possible to add in custom arguments to your script making the script more interactive and allow you to do the same analysis for multiple companies. This is done in the following script (and can be downloaded [here](https://www.dropbox.com/s/usooz6y29r1xldb/routines_template_with_inputs.openbb?dl=1)):

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

This script includes `$ARGV[0]`, `$ARGV[1]` and `$ARGV[2]`. This means that the script requires you to submit three arguments. In this case, they refer to <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank" rel="noreferrer noopener">stock tickers</a>. Therefore, like the script also says, you can include these arguments with `-i` followed by three tickers (e.g. `routines_template_with_inputs.openbb`). This results in the following:

![OpenBB Script with Input](https://user-images.githubusercontent.com/46355364/223207706-42995834-577f-4747-8185-42a016f441d9.png)

It is a simple script but it gives an understanding what the possibilities are. Do make sure you saved this script in the `routines` folder else you are not able to execute it.