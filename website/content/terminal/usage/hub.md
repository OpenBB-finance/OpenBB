---
title: Hub Synchronization
sidebar_position: 6
description: This is a documentation page for OpenBB focusing on the integration of
  OpenBB Terminal with OpenBB Hub. Topics covered include registration, login, managing
  API keys, default data sources, theme styles, script routines, and personal access
  tokens.
keywords:
- OpenBB Terminal guide
- OpenBB Hub integration
- Registration process
- Login process
- API Keys management
- Default Data Sources
- Theme Styles
- Script Routines
- Personal Access Tokens
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Hub Synchronization - Usage | OpenBB Terminal Docs" />

This guide will walk you through the process of integrating the OpenBB Terminal with the OpenBB Hub to achieve optimal performance.

## Registration

To get started, you'll need to create an account on the OpenBB Hub by visiting [https://my.openbb.co](https://my.openbb.co)

By registering with the OpenBB Hub, you can easily access our products on multiple devices and maintain consistent settings for an improved user experience. This also enables you to receive updates for the terminal as soon as they become available.

## Login

Once you're successfully registered on the OpenBB Hub, you can log in to access all the benefits it has to offer.

The login credentials you use on the OpenBB Hub will be the same ones you will use to access the OpenBB Terminal.

<img width="1441" alt="Screenshot 2023-04-14 at 3 46 52 PM" src="https://user-images.githubusercontent.com/25267873/232166964-635ff0c0-0e09-4cc2-9f9f-078552cc41c1.png"/>

When OpenBB Terminal 3.0.0 (or greater) is launched, there will be a new welcome message. On packaged applications, you will be greeted with the following:

<img width="473" alt="Screenshot 2023-04-14 at 3 31 51 PM" src="https://user-images.githubusercontent.com/25267873/232165909-682c7301-237c-4a8a-b780-97c944adb625.png"/>

The "Remember me" feature saves your session locally, eliminating the need to log in for 30 days.

If you haven't registered, simply press `<ENTER>` to access the terminal as a guest without using this feature.

Once you have successfully logged in, your username (e.g. [didier.lopes]) along with a 🦋 flair will be displayed on the terminal. However, if you're in guest mode, only the 🐛 flair will be visible.

Note: If you wish to log in or out of your account while inside the terminal, simply access the /account menu.

## API Keys

As you may already know, the OpenBB Terminal acts as a mediator between users and data providers and does not store any data. This enables us to focus on providing a superior product experience for users, while data vendors can integrate their data sources to create a new revenue channel. However, this does mean that each user must manage their own API keys for each data provider they wish to access.

### OpenBB Hub

If you were an OpenBB user prior to the release of OpenBB Terminal 3.0, you may already have an .env file containing all your API keys. If this is the case, simply drag and drop the file onto [this page](https://my.openbb.co/app/terminal/api-keys) to automatically save your keys.

<img width="1441" alt="Screenshot 2023-04-14 at 6 14 55 PM" src="https://user-images.githubusercontent.com/25267873/232176162-b16296d4-0c08-408c-aaa4-f46a6bea1bf3.png"/>

If you are a new user, you'll need to follow the instructions provided by hovering over the ℹ️ icon for each data source you're interested in. The icon will direct you to the data vendor's website to obtain the necessary API key, which can then be saved on the Hub for future use.

### OpenBB Terminal

Upon logging in, the OpenBB Terminal will automatically retrieve the API keys associated with your account.

If you have not saved them on the OpenBB Hub, they will be loaded from your local environment by default. However, if an API key is saved on the OpenBB Hub, it will take precedence over the local environment key.

Important: Note that setting a key in the `keys` menu will **NOT** upload it to the OpenBB Hub. This option is only intended for managing local environment variables. For a superior user experience, OpenBB highly recommends using the OpenBB Hub to manage your API keys.

If an API key is updated in the Hub while the OpenBB Terminal is running, you will need to restart the terminal for the changes to take effect.

To delete your saved API keys from the OpenBB Hub, use the `/account/clear` command. However, please note that this action **CANNOT BE UNDONE** and will prompt a confirmation prompt.

## Default Data Sources

In many cases, there are multiple data vendors offering access to the same data for a given command. At OpenBB, we believe in empowering our users to choose their preferred data source, or the one with whom they already have a commercial relationship. Therefore, we offer the ability for users to select their default data sources for each command.

### OpenBB Hub

In the OpenBB Hub, you can access [this page](https://my.openbb.co/app/terminal/data-sources) which allows you to select the default data sources for all commands.

<img width="1440" alt="Screenshot 2023-04-14 at 6 26 53 PM" src="https://user-images.githubusercontent.com/25267873/232176560-5bee773f-1b9a-4904-8f05-fcaf1342a81d.png"/>

### OpenBB Terminal

Upon login, the OpenBB Terminal will pull the default data sources associated with your account.

If a user wants to adjust any data source directly from the terminal, this is possible by utilizing the `/sources` menu. For instance,

<img width="476" alt="Screenshot 2023-04-14 at 6 39 29 PM" src="https://user-images.githubusercontent.com/25267873/232177024-445494b6-46f2-4a4f-a874-e93132204378.png"/>

That change will be reflected on the OpenBB Hub when refreshing the page.

Note that any changes on the OpenBB Hub will require a restart of the terminal to take effect.

## Theme Styles

Theme styles correspond to the ability to change your terminal "skin" (i.e. colouring of the `menu`, `commands`, `data source`, `parameters`, `information` and `help`), the charts and tables style.

### OpenBB Hub

In the OpenBB Hub, you have the ability to change your preferred themes for the terminal on [this page](https://my.openbb.co/app/terminal/theme?index),

<img width="1427" alt="Screenshot 2023-04-14 at 6 51 50 PM" src="https://user-images.githubusercontent.com/25267873/232177511-d86edd57-fa2f-40a2-b05f-35cbb856bb94.png"/>

and charts and tables on [this page](https://my.openbb.co/app/terminal/theme/charts-tables),

<img width="1421" alt="Screenshot 2023-04-14 at 6 56 46 PM" src="https://user-images.githubusercontent.com/25267873/232177692-89fd6784-dd8b-4cb2-a613-d51f6332e2da.png"/>

### OpenBB Terminal

When you log in to the OpenBB Terminal, the platform automatically applies the theme style associated with your account.

To further customize your experience, you can manage these styles using the `/settings/theme` and `/settings/colors` commands. While managing the theme is straightforward, managing colors can be more complex as it requires moving a special file around. For a smoother experience, we highly recommend managing colors through the improved interface on the OpenBB Hub.

It's important to note that changes to charts and tables take effect immediately, while changes to the terminal theme require a reset to take effect.

## Script Routines

These are text files with an `.openbb` extension that allow users to create workflows of sequence of commands. And allows to create parameters that can be modified outside the terminal. An example would be the file, "_example.openbb_" looking like:

```text
stocks
load $ARGV[0]
# depict candle chart
candle
```

and then run on the terminal utilizing:

```text
/exe example.openbb -i MSFT
```

### OpenBB Hub

The OpenBB Hub allows users to manage their own script routines to be run in the OpenBB Terminal. They can do so on [this page](https://my.openbb.co/app/terminal/routines).

<img width="1442" alt="Screenshot 2023-04-14 at 7 13 11 PM" src="https://user-images.githubusercontent.com/25267873/232178264-61f383ef-242f-48da-bd32-83fd013a094c.png"/>

In addition, a few script routines will be distributed by the OpenBB Team on [this page](https://my.openbb.co/app/terminal/routines/default). These come primarily from academic content that the team is releasing, but can serve as an example of what you can do.

<img width="1443" alt="Screenshot 2023-04-14 at 7 17 44 PM" src="https://user-images.githubusercontent.com/25267873/232178430-1e870571-26b7-4513-9d14-5ef2e97090b2.png"/>

Note that the "Download" button allows you to download the example file and share with co-workers / colleagues.

### OpenBB Terminal

Once you've logged in to your OpenBB Terminal account, your routines will automatically sync and become available for use.

To see the available routines from the Hub, use the `/account/list` command. This command will display both the default OpenBB routines and your personal routines, as shown in the image below:

<img width="1582" alt="Screenshot 2023-04-14 at 7 22 14 PM" src="https://user-images.githubusercontent.com/25267873/232178585-71b9de95-707f-4374-91c8-83e6622f6829.png"/>

To run a routine, select `exe --file` from the main menu and the available routines will pop up as auto-completions. For example:

<img width="576" alt="Screenshot 2023-04-14 at 7 23 16 PM" src="https://user-images.githubusercontent.com/25267873/232178635-4626c686-dafb-40c0-911f-60a1d3f8fd13.png"/>

If you'd like to download a specific routine or upload a locally created .openbb file file, you can use the `account/upload` and `account/download` commands.

You can also delete your locally stored routines, which will then be synced with the OpenBB Hub.

## Personal Access Tokens

Setting up API keys on the OpenBB Hub has an additional benefit: it allows you to generate a personal access token (PAT) that can be used with the OpenBB SDK. With this token, you can programmatically access the data that powers the OpenBB Terminal, without the need to add individual API keys for each user.

### OpenBB Hub

If you go to the bottom of [this page](https://my.openbb.co/app/sdk/api-keys) you can find your OpenBB PAT. This is the API Keys that will be used on the OpenBB SDK and this is the same as the ones set in the OpenBB Terminal.

<img width="1427" alt="Screenshot 2023-04-14 at 10 37 44 PM" src="https://user-images.githubusercontent.com/25267873/232185425-672a7eb0-e4ba-4863-8dbb-dd951afd25cc.png"/>

The bottom of that page also allows to regenerate the PAT.

In addition you can copy-paste the following section

```python
from openbb_terminal.sdk import openbb
openbb.login(token = "<YOUR TOKEN HERE>")
```

### OpenBB Terminal

Although the PAT is not meant to be used in the OpenBB Terminal, you can still manage it in the `/account` menu through the `generate` command. This will delete any previously issued tokens.

Once you have generated a token, an SDK session can be initiated anywhere utilizing:

```python
from openbb_terminal.sdk import openbb
openbb.login(token = "<YOUR TOKEN HERE>")
```

Note that you can also access your account utilizing your credentials, e.g.

```python
openbb.login(email = 'didier.lopes@openbb.finance', password = '****')
```

in addition, if you want to store that information locally you can do so by setting this additional flag.

```python
keep_session = True
```
