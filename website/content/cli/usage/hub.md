---
title: Hub Synchronization
sidebar_position: 6
description: This is a documentation page for OpenBB focusing on the integration of
  OpenBB Platform CLI with OpenBB Hub. Topics covered include registration, login, managing
  API keys, default data sources, theme styles, script routines, and personal access
  tokens.
keywords:
- OpenBB Platform CLI
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

<HeadTitle title="Hub Synchronization - Usage | OpenBB Platform CLI Docs" />

This guide will walk you through the process of integrating the OpenBB Platform CLI with the OpenBB Hub to achieve optimal performance.

## Registration

To get started, you'll need to create an account on the OpenBB Hub by visiting [https://my.openbb.co](https://my.openbb.co)

By registering with the OpenBB Hub, you can easily access our products on multiple devices and maintain consistent settings for an improved user experience. This also enables you to receive updates for the terminal as soon as they become available.

## Login

Once you're successfully registered on the OpenBB Hub, you can log in to access all the benefits it has to offer.

The login credentials you use on the OpenBB Hub will be the same ones you will use to access the OpenBB Platform CLI.

To log in on your account while inside the CLI, simply access the `/account` menu and use the `login` command.

## API Keys

As you may already know, the OpenBB Platform acts as a mediator between users and data providers and does not store any data. This enables us to focus on providing a superior product experience for users, while data vendors can integrate their data sources to create a new revenue channel. However, this does mean that each user must manage their own API keys for each data provider they wish to access.

After having an account on the OpenBB Hub, you can manage your API keys on [this page](https://my.openbb.co/app/platform/credentials).

Upon logging in, the OpenBB Platform CLI will automatically retrieve the API keys associated with your account.

If you have not saved them on the OpenBB Hub, they will be loaded from your local environment by default. However, if an API key is saved on the OpenBB Hub, it will take precedence over the local environment key.

If an API key is updated in the Hub while the OpenBB Terminal is running, you will need to restart the CLI for the changes to take effect.

## Theme Styles

Theme styles correspond to the ability to change your terminal "skin" (i.e. coloring of the `menu`, `commands`, `data source`, `parameters`, `information` and `help`), the charts and tables style.

In the OpenBB Hub, you have the ability to change your preferred themes for the CLI. After customizing as intended, you can then download the theme and apply it to the CLI by adding it to you styles directory (`/home/your-user/OpenBBUserData/styles/user`).

## Script Routines

These are text files with an `.openbb` extension that allow users to create workflows of sequence of commands. And allows to create parameters that can be modified outside the CLI. An example would be the file, "_example.openbb_" looking like:

```text
equity
price
# depict candle chart
historical --symbol $ARGV[0] --chart
```

and then run on the terminal utilizing:

```text
/exe example.openbb -i MSFT
```

The OpenBB Hub allows users to manage their own script routines to be run in the OpenBB Platform CLI.

<img width="1442" alt="Screenshot 2023-04-14 at 7 13 11 PM" src="https://user-images.githubusercontent.com/25267873/232178264-61f383ef-242f-48da-bd32-83fd013a094c.png"/>

In addition, a few script routines will be distributed by the OpenBB Team on [this page](https://my.openbb.co/app/terminal/routines/default). These come primarily from academic content that the team is releasing, but can serve as an example of what you can do.

<img width="1443" alt="Screenshot 2023-04-14 at 7 17 44 PM" src="https://user-images.githubusercontent.com/25267873/232178430-1e870571-26b7-4513-9d14-5ef2e97090b2.png"/>

Note that the "Download" button allows you to download the example file and share with co-workers / colleagues.

To run a routine on the CLI, select `exe --file` from the main menu and the available routines will pop up as auto-completions. For example:

<img width="576" alt="Screenshot 2023-04-14 at 7 23 16 PM" src="https://user-images.githubusercontent.com/25267873/232178635-4626c686-dafb-40c0-911f-60a1d3f8fd13.png"/>

## Personal Access Tokens

Setting up API keys on the OpenBB Hub has an additional benefit: it allows you to generate a personal access token (PAT) that can be used with the OpenBB SDK. With this token, you can programmatically access the data that powers the OpenBB Terminal, without the need to add individual API keys for each user.

You can find and manage your OpenBB PAT [here](https://my.openbb.co/app/platform/pat).

<img width="1427" alt="Screenshot 2023-04-14 at 10 37 44 PM" src="https://user-images.githubusercontent.com/25267873/232185425-672a7eb0-e4ba-4863-8dbb-dd951afd25cc.png"/>

You can log in to the OpenBB Platform CLI using your PAT by running the `login` command on the `account` menu.
