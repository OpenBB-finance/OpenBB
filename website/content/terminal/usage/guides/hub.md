---
title: Hub Synchronization
sidebar_position: 6
description: Walk-through of integrating the OpenBB Terminal with the OpenBB Hub
keywords: [api, keys, api keys, data provider, data, free, openbb_terminal, openbbterminal, openbb_hub, hub, routines, synchronization, sync, hub sync, hub synchronization, hub sync]
---

This guide will walk you through the process of integrating the OpenBB Terminal with the OpenBB Hub.

## Registration

First you want to create an account on OpenBB Hub at: https://my.openbb.dev/.

You'll need to register so the OpenBB Hub can know about you and save your data into our servers. This allows you to be able to boot up our products in multiple devices and keep the same settings, which improves a lot the user experience. The same goes for when a new version of the terminal is released.


## Login

After you are registered on the OpenBB Hub, you can login onto it and benefit from all the advantages that come with it.

The details that you use on this page will be the same ones that are going to be used on the OpenBB Terminal.

<img width="1441" alt="Screenshot 2023-04-14 at 3 46 52 PM" src="https://user-images.githubusercontent.com/25267873/232166964-635ff0c0-0e09-4cc2-9f9f-078552cc41c1.png">

When OpenBB Terminal 3.0.0 (or greater) is launched, there will be a new welcome message. On packaged applications, you will be greeted with the following:

<img width="473" alt="Screenshot 2023-04-14 at 3 31 51 PM" src="https://user-images.githubusercontent.com/25267873/232165909-682c7301-237c-4a8a-b780-97c944adb625.png">

Make sure to utilize the same credentials.

The remember me option will save your session to the local machine, so that you do not need to login for the next 30 days.  If you are not registered, you can skip this by pressing `<ENTER>` and enter as a guest.

If you are running the Terminal from source, this screen can either be reached by running
```console
python terminal.py --login
```
or by using the `account/login` function.

### API Keys

If you have previously uploaded your API keys to the OpenBB Hub, they will be pulled from your account on login.  If you have previously used the OpenBB Terminal and set API keys, but have not put them in the Hub, we will load from the local environment.  Note that setting a key in the `keys` menu will **not** upload it to the Hub.

Note that if you have the terminal running and you update a key in the Hub, you will need to restart the terminal for the changes to take effect.

If you wish to delete your stored API keys from the hub, you can do so using the `account/clear` function.  Note that this action will bring up a confirmation prompt and **cannot be undone**.

### Themes

In the OpenBB Hub, you have the ability to change your preferred themes for your terminal, charts and tables.  When logged in, the terminal will pull a saved theme from your account.  For the terminal theme, this can be activated by using the command: `settings/colors --style hub`.  If you wish to change, you can pass one of `{light,dark,openbb}` to the `--style` flag.  To change the charting style, the `settings/theme` command can be run.

### Default Data Sources

Your selected default data sources will automatically be synced to the terminal on login.
These can still be adjusted in the `sources/` menu, but changes in your terminal will not be synced.
Any changes on the Hub will require a restart of the terminal to take effect.

### Routines

When logged into your account on the OpenBB Terminal, your routines will be synced on login and automatically available for use.
To see what routines are available from the Hub, you can use the `account/list` command, which will show the default OpenBB routines and your personal routines, such as:

```console
2023 Apr 13, 12:48 [jmaslek11] 🦋 /account/ $ list

                        Personal routines - page 1 of 1
┏━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Name ┃ Description                       ┃ Version ┃ Last update         ┃
┡━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ test │ Load apple ticker and plot candle │ 3.0.0   │ 2023-04-13 16:50:28 │
└───┴──────┴───────────────────────────────────┴─────────┴─────────────────────┘

                                                                      Default routines
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Name                              ┃ Description                                                                      ┃ Version ┃ Last update         ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ The Greek Government Debt Crisis  │ This routine script is related to the "OpenBB - The Greek Government Debt        │ 3.0.0   │ 2023-04-05 14:45:27 │
│   │                                   │ Crisis" presentation and allows allows the Greek Debt Crisis to be analyzed      │         │                     │
│   │                                   │ further in Excel.                                                                │         │                     │
├───┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┼─────────┼─────────────────────┤
│ 2 │ The Influence of the Central Bank │ This routine script is related to the "OpenBB - The Influence of the Central     │ 3.0.0   │ -                   │
│   │                                   │ Bank" presentation and allows the Central Bank and Government dataset to be      │         │                     │
│   │                                   │ analyzed further in Excel.                                                       │         │                     │
├───┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────┼─────────┼─────────────────────┤
│ 3 │ Financial Due Diligence          │ This routine script is related to the "OpenBB - Performing Financial Due         │ 3.0.0   │ 2023-04-05 14:44:36 │
│   │                                   │ Diligence" presentation and allows the exact same analysis to be performed as    │         │                     │
│   │                                   │ done in this presentation for any company. This creates a highly detailed Excel  │         │                     │
│   │                                   │ file as seen on the right.                                                       │         │                     │
│   │                                   │                                                                                  │         │                     │
│   │                                   │ This is not only relevant for competitive analysis but also if there is a need   │         │                     │
│   │                                   │ to replicate the analysis for a different company, industry or sector.           │         │                     │
└───┴───────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────┴─────────┴─────────────────────┘
```

In order to run a routine, from the main menu one can run `exe --file` and the available routines will pop up as available auto completions.  If you wish to specify a specific routine to download locally, or to upload a locally created .openbb file, the commands `account/upload` and `account/download` can be used.  Your routines can also be deleted locally.  This will delete on the Hub as well.

### Personal Access Tokens

In order to access your settings in the sdk, we allow you to use a personal access token.  This can either be generated in the Hub or in the terminal.  To generate a new token in the terminal, one can use the `account/generate` command.  This will delete any previously issued tokens.  Once you have generated a token, an SDK session can be initiated anywhere using
```python
from openbb_terminal.sdk import openbb
openbb.login(token = "<YOUR TOKEN HERE>")
```
