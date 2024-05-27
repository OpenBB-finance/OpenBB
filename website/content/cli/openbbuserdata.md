---
title: OpenBBUserData Folder
sidebar_position: 8
description: The OpenBBUserData folder is where exports, routines, and other user-related content is saved and stored. Its default location is the home of the system user account.
keywords:
- OpenBBUserData folder
- settings
- data
- preferences
- exports
- CLI
- save
- routines
- xlsx
- csv
- user_settings.json
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="OpenBBUserData Folder | OpenBB Platform CLI Docs" />

The OpenBBUserData folder is where exports, routines, and other user-related content is saved and stored.

:::info
If a new file is placed in the folder (like a Routine) the CLI will need to be reset before auto complete will recognize it.
:::

## Default Location

Its default location is the home of the system user account, similar to the following paths:
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:/Users/<YOUR_USERNAME>/OpenBBUserData`

This folder contains all things user-created. For example:

- Exported files
- Styles and themes
- Routines
- Logs

:::note
**Note:** With a WSL-enabled Windows installation, this folder will be under the Linux partition
:::

## Update Folder Location

The location of this folder can be set by the user by changing the user configuration file: `/home/your-user/.openbb_platform/user_settings.json`.

```json
{
...
"preferences": {
    "data_directory": "/path/to/NewOpenBBUserData",
    "export_directory": "/path/to/NewOpenBBUserData"
},
...
}
```
