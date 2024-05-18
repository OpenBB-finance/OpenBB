---
title: Hub Synchronization
sidebar_position: 6
description: This page outlines the `/account` menu within the OpenBB Platform CLI, and integrations with the OpenBB Hub.
keywords:
- OpenBB Platform CLI
- OpenBB Hub
- Registration
- Login process
- API Keys management
- Theme
- Style
- Dark
- Light
- Script Routines
- Personal Access Tokens
- PAT
- Credentials
- Customization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Hub Synchronization | OpenBB Platform CLI Docs" />

This page outlines the `/account` menu within the OpenBB Platform CLI and integrations with the OpenBB Hub.

## Registration

To get started, you'll need to create an account on the OpenBB Hub by visiting [https://my.openbb.co](https://my.openbb.co)

By registering with the OpenBB Hub, you can easily access our products on multiple devices and maintain consistent settings for an improved user experience.

## Login

Once you're successfully registered on the OpenBB Hub, you can log in to access all the benefits it has to offer.

:::tip
OpenBB recommends logging in via the Personal Access Token (PAT) method. This revokable token allows users to login without transmitting any personally identifiable information, like an email address, which makes it an ideal solution for shared machines and public network connections.
:::

To login, enter the `/account` menu and then use the `login` command with your choice of login method.

### PAT

```console
/account
login --pat REPLACE_WITH_PAT
```

### Email & Password

```console
/account
login --email my@emailaddress.com --password totallysecurepassword
```

## API Keys

The OpenBB Platform acts as a mediator between users and data providers.

With an OpenBB Hub account, you can manage your API keys on [this page](https://my.openbb.co/app/platform/credentials).

Upon logging in, the CLI will automatically retrieve the API keys associated with your account.

If you have not saved them on the OpenBB Hub, they will be loaded from your local environment by default.

:::danger
If an API key is saved on the OpenBB Hub, it will take precedence over the local environment key.
:::

The CLI will need to be restarted, or refreshed, when changes are made on the Hub.

## Theme Styles

Theme styles correspond to the ability to change the terminal "skin" (i.e. coloring of the `menu`, `commands`, `data source`, `parameters`, `information` and `help`), as well as the chart and table styles.

In the OpenBB Hub, you can select the text colours for the CLI. After customizing:
- Download the theme to your styles directory (`/home/your-user/OpenBBUserData/styles/user`).
- Apply it by selecting the style from the `/settings` menu.

```console
/settings
console_style -s openbb_config
```

Replace `openbb_config` with the name of the downloaded (JSON) file.

## Script Routines

The OpenBB Hub allows users to create, edit, manage, and share their script routines that can be run in the OpenBB Platform CLI.

The "Download" button will save the file locally. Add it to `/home/your-user/OpenBBUserData/routines`, for the script to populate as a choice for the `exe` command on next launch.

## Refresh

The `refresh` command will update any changes without the need to logout and login.

```console
/account
refresh
```

## Logout

Logging out will restore any local credentials and preferences defined in the `user_settings.json` file.

```console
/account
logout
```
