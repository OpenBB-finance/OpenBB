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

The "_Remember me_" feature will save your session to the local machine, so that you do not need to login for the next 30 days. 

If you are not registered, you can skip this by pressing `<ENTER>` and enter as a guest.

If you have logged in successfully your terminal will display your username (e.g. `[didier.lopes]`) followed by the 🦋 flair whereas if you are in guest mode you'll see only the 🐛 flair.

Note: If you are inside the terminal and want to login or logout of your account you can utilize the `/account` menu in the terminal.

## API Keys

### Uploading API Keys to the OpenBB Hub

If you were already an OpenBB user before the OpenBB Terminal 3.0 you might have an `.env` file that contains all your API keys. If that is the case then you just need to drag and drop it in [this page](https://my.openbb.dev/app/terminal/api-keys).

<img width="1441" alt="Screenshot 2023-04-14 at 6 14 55 PM" src="https://user-images.githubusercontent.com/25267873/232176162-b16296d4-0c08-408c-aaa4-f46a6bea1bf3.png">

Otherwise you'll need to follow the instructions by hovering on the ℹ️ for each data source of interest. The icon that follows will take you to the data vendor website to acquire the API key which then you can save on the Hub.

### API Keys on the OpenBB Terminal

Upon login, the OpenBB Terminal will pull the API keys associated with your account.

If you have not set them on the OpenBB Hub, by default they will be loaded from your local environment. However, an API key on the OpenBB Hub will take precedence over one on the user local environment.

Important: Setting a key in the `keys` menu will **NOT** upload it to the OpenBB Hub. This is merely an option to allow the user to manage it's own local environment variables, but OpenBB recommends utilizing the OpenBB Hub for an improved user experience.

If the OpenBB Terminal is running and an API key is updated in the Hub you will need to restart the terminal for the changes to take effect.

If you wish to delete your stored API keys from the OpenBB Hub, you can do so using the command: `/account/clear`. This action will bring up a confirmation prompt and **CANNOT BE UNDONE**.

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
