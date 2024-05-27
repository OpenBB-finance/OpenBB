---
title: Community Routines
sidebar_position: 3
description: Page provides a detailed overview of OpenBB's Community
  Routines. It explains how users can create, modify, share, vote, download, and search for investment
  research scripts.
keywords:
- Community Routines
- Investment Research
- Investment Scripts
- Upvotes
- Share Scripts
- Advanced Search
- CLI
- automation
- Hub
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Community Routines - Routines - | OpenBB Platform CLI Docs" />

## Overview

Community Routines are a feature of the [OpenBB Hub](https://my.openbb.co) that provides methods for creating, editing and sharing OpenBB Platform CLI scripts in the cloud.

Users can create routines that are private or public, with public routines able to run directly from a URL.

## Create Routines

- From the sidebar, click on "My Routines".
- Scroll down and click the button, "Create New".
- Enter a name for the routine.
- Select the "public" check box to make it runnable via URL.
- Add tags (optional).
- Add a short description.
- Enter your workflow into the Script box.
- Click the "Create" button.

## Run From URL

To run a routine with a URL, it must be made public. Existing routines can be modified by clicking on the item under, "My Routines". Check the "Public" box to activate.

The URL will follow the pattern, `https://my.openbb.co/u/{username}/routine/{routine-name}`, which can be executed from the CLI with:

```console
/exe --url {URL}
```

## Download

Alternatively, click the "Download" button at the bottom of the routine editor to manually download the file to the machine. Place the file in the `OpenBBUserData/routines` folder and open the CLI. The script will be presented as a choice by auto-complete.
