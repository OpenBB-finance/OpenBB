---
title: Custom Data
sidebar_position: 3
description: Documentation detailing usage of the OpenBB Terminal for financial data
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
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Custom Data - Data - Usage | OpenBB Terminal Docs" />

The OpenBB Terminal not only allows access to a world of financial data through our data aggregation and standardization. We also allow users to bring their own data to the terminal and export data.

## The OpenBBUserData Folder

The `OpenBBUserData` folder's default location is the home of the system user account. By default this will be the following paths:
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:/Users/<YOUR_USERNAME>/OpenBBUserData`

Within the folder you can find files that you have exported as well as files that you wish to import directly into the OpenBB Terminal. For example, this could be an orderbook which you can store in `OpenBBUserData/portfolio/holdings`.

![OpenBBUserData Folder](https://user-images.githubusercontent.com/85772166/195742985-19f0e420-d8f7-4fea-a145-a0243b8f2ddc.png)

This folder contains all things user-created. For example:

- Screener presets
- Portfolio files
- Exported files
- Files to be imported by various functions
- Styles and themes
- Preferred data sources

:::note
**Note:** With a WSL-enabled Windows installation, this folder will be under the Linux partition
:::

### Update export folder location

The location of this folder can be set by the user from the `/settings` menu. There should be no need to update paths in this menu unless the folders have been moved manually. If the location of the OpenBBUserData folder must be changed, it is best to move the entire existing folder to the new path. The path is then changed under the settings menu with:

```console
/settings/ $ userdata --folder "/complete_path_to/OpenBBUserData"
```

## Import data

Menus, such as [Econometrics](/terminal/menus/econometrics) or [Forecast](/terminal/menus/forecast), allow the user to import their own dataset. Files available to import will be included with the selections made available by auto-complete. In the Econometrics menu, this is activated after pressing the space bar with `load -f`

![Importing Data](https://user-images.githubusercontent.com/85772166/204921760-38742f6c-ec78-4009-9c23-54dcb0504524.png)

Both menus look in the `exports` and `custom_imports` folders within the `/OpenBBUserData` folder.
