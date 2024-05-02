---
title: Custom Data
sidebar_position: 3
description: Documentation detailing usage of the OpenBB Platform CLI for financial data
  aggregation, standardization, and user data import. It explains the OpenBBUserData
  folder functions, how to modify settings, and how to import or export user data.
keywords:
- financial data
- data aggregation
- data standardization
- OpenBBUserData folder
- import data
- export data
- Econometrics
- Portfolio
- Portfolio Optimization
- settings menu
- export folder location
- userdata command
- user-created files
- CLI
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Custom Data - Data - Usage | OpenBB Platform CLI Docs" />

The OpenBB Platform CLI not only allows access to a world of financial data through our data aggregation and standardization.

## The OpenBBUserData Folder

The `OpenBBUserData` folder's default location is the home of the system user account. By default this will be the following paths:
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:/Users/<YOUR_USERNAME>/OpenBBUserData`

Within the folder you can find files that you have exported.

![OpenBBUserData Folder](https://user-images.githubusercontent.com/85772166/195742985-19f0e420-d8f7-4fea-a145-a0243b8f2ddc.png)

This folder contains all things user-created. For example:

- Exported files
- Styles and themes
- Routines
- Logs

:::note
**Note:** With a WSL-enabled Windows installation, this folder will be under the Linux partition
:::

### Update export folder location

The location of this folder can be set by the user by changing the user configuration file: `/home/your-user/.openbb_platform/user_settings.json`.
