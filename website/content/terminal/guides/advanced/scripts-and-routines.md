---
sidebar_position: 5
title: Scripts & Routines
description: OpenBB Routine files, `.openbb`, are simple scripts for automating processes and repetitive tasks. They represent a 1:1 relationship with any command in the OpenBB Terminal; one line represents one function. A routine file can be created or modified in any basic text editor, the only difference between a plain-text file and an OpenBB Routine file is the `.openbb` file extension. Additionally, routine files can be captured with the macro recorder, controlled with global commands, `record` & `stop`. Upon `stop`, the script is automatically saved to the, `~/OpenBBUserData/routines/`, folder.  Routine files stored there are callable from the main menu, using the `exe` function. By deploying variable arguments - `$ARGV[0]` - to any line in the script, dates, symbols, exported filenames, or any Terminal function argument, scripts become dynamic.
keywords: [scripts, routines, .do file, stata, spss, r studio, python, automation, data collection, aggregation, script, routine, openbb terminal]
---
## OpenBB Routine Files

OpenBB Routine files, `.openbb`, are simple scripts for automating processes and repetitive tasks. They represent a 1:1 relationship with any command in the OpenBB Terminal; one line represents one function. A routine file can be created or modified in any basic text editor, the only difference between a plain-text file and an OpenBB Routine file is the `.openbb` file extension. Additionally, routine files can be captured with the macro recorder, controlled with global commands, `record` & `stop`. Upon `stop`, the script is automatically saved to the, `~/OpenBBUserData/routines/`, folder.  Routine files stored there are callable from the main menu, using the `exe` function. By deploying variable arguments - `$ARGV[0]` - to any line in the script, dates, symbols, exported filenames, or any Terminal function argument, scripts become dynamic.

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

## The Macro Recorder

With the macro recorder, it is easy to get started; just enter `record`. To follow along, copy the block below into the Terminal at the main menu.

```console
record/stocks/load qqq/forecast/expo QQQ/autoselect QQQ/stop
```

![Routines](https://user-images.githubusercontent.com/85772166/219550644-26ecaf27-cbf9-4314-8f3b-d9f20e8fcb88.png)

![Routines](https://user-images.githubusercontent.com/85772166/219550698-3b1cd675-4e1f-4d3e-a630-9ed00b689b2b.png)

The routine has been successfully captured, and the next time the Terminal is opened, this routine will be visible when calling the `exe` function.

![Routines](https://user-images.githubusercontent.com/85772166/221951059-3ccf7235-5b0e-48ba-9f6c-3d0aaadd20cf.png)

## Editing & Inserting Arguments

Let's take a look at the routine file that was just generated. This is what was captured, the recorder interpreted each `/` as a new command:

```console
stocks

load qqq

forecast

expo QQQ

autoselect QQQ
```

A routine file that is locked to any single symbol will likely be less desirable than one which can be applied to any ticker. OpenBB routine files overcome this obstacle by allowing for an unlimited number of variable arguments - `$ARGV[0]` - to be assigned anywhere in the script. Let's go ahead and edit our Routine file to accommodate any symbol.

```console
stocks

load $ARGV[0]

forecast

expo $ARGV[0]

autoselect $ARGV[0]
```

Open the file with a text editor, make the changes, save the file, and then run the `exe` command again; except now, add the `--input` argument with a new ticker. For demonstration purposes, the routine file used in the example has been renamed to be `demo_routine.openbb`. Because the file name was changed, the Terminal will need to be restarted for the new name to be recognized. In subsequent edits, this will not be necessary because the file is read from start-to-finish with every execution.

```console
exe demo_routine.openbb --input SPY
```

![Routines](https://user-images.githubusercontent.com/85772166/219550837-fe6ece69-2336-40fc-8db9-fc7b62b784c6.png)

Additional variables can be assigned to perform other functions, a date for example. Let's modify the routine file to include a start date as part of the `load` function. For those following along at home, modify the second command in the script to be:

```console
load $ARGV[0] --start $ARGV[1]
```

The additional argument is added to the previous `exe` syntax as a comma-separated list.

```console
exe demo_routine.openbb --input SPY,2022-01-01
```

![Routines](https://user-images.githubusercontent.com/85772166/219550901-13205851-a12f-4ef9-85f4-a2bfa24be9c9.png)

This process is limited only to the imagination. Large, reptitive, tasks can be automated by extrapolating on the process above.

## Commenting

Commenting within an OpenBB routine file is how the author of a script can communicate to the end-user. Commented lines - beginning with, "#" - are passed over during execution of the routine. Let's update the example routine file with a few comments to illustrate.

```console
# This routine is a demonstration of the OpenBB routine files.
# Read the docs here: https://docs.openbb.co/terminal/guides/advanced/scripts-and-routines

# Start of routine
stocks

load $ARGV[0] --start $ARGV[1]

forecast

expo $ARGV[0]

autoselect $ARGV[0]

# End of routine
# Please note that the outputs of this routine will be different than the depictions above, because, you are now in the future.
```

For convenience, the routine file constructed in the example above can be downloaded directly [here](https://github.com/OpenBB-finance/OpenBBTerminal/files/10763257/demo_routine.openbb.zip).
