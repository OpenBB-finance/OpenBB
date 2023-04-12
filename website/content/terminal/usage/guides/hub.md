---
title: Hub Synchronization
sidebar_position:6
description: Walk-through of integrating the OpenBB Terminal with the OpenBB Hub
keywords: [api, keys, api keys, data provider, data, free, openbb_terminal, openbbterminal,
openbb_hub, hub, routines, synchronization, sync, hub sync, hub synchronization, hub sync]
---

This guide will walk you through the process of integrating the OpenBB Terminal with the OpenBB Hub.
When OpenBB Terminal 3.0.0 (or greater) is launched, there will be a new welcome.
On pacakged applications, you will be greeted with the following
```console
  ___                   ____  ____    _____                   _             _
 / _ \ _ __   ___ _ __ | __ )| __ )  |_   _|__ _ __ _ __ ___ (_)_ __   __ _| |
| | | | '_ \ / _ \ '_ \|  _ \|  _ \    | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | |
| |_| | |_) |  __/ | | | |_) | |_) |   | |  __/ |  | | | | | | | | | | (_| | |
 \___/| .__/ \___|_| |_|____/|____/    |_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|
      |_|
                                    @@@
                                    @@@
             @@@@@@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@@
             @@@                 @@@   @@@                 @@@
             @@@@@@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@@
                                 @@@   @@@
                %%%%%%%%%%%%%%%%%@@@   @@@%%%%%%%%%%%%%%%%%
                @@@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@
                @@@              @@@   @@@              @@@
                @@@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@

                Investment research for Everyone, Anywhere.


Register     : https://my.openbb.co/register
Ask support  : https://openbb.co/support

Please enter your credentials or press <ENTER> for guest mode:
> Email: *****
> Password: *****
> Remember me? (y/n):
```

If you are registered on the OpenBB Hub, you can enter your credentials here.  The remember me option will save your session to the local machine, so that you do not need to login for the next 30 days.  If you are not registered, you can skip this by pressing <ENTER>.

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

### Routines
