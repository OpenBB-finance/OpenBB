---
title: Commands And Arguments
sidebar_position: 2
description: This page explains how to enter commands and arguments into the OpenBB CLI.
keywords:
- help arguments
- auto-complete
- global commands
- support command
- reset command
- command line interface
- metadata
- cli
- parameters
- functions
- commands
- options
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Commands And Arguments - Usage | OpenBB CLI Docs" />


## Help arguments

The `help` command shows the current menu you are in and all the commands and menus that exist, including a short description for each of these.

This is arguably one of the most helpful commands that the CLI. If you are familiar to navigating in a command line interface, it's the equivalent to `ls -ll`.


## Auto-complete

The OpenBB Platform CLI is equipped with an auto completion engine that presents choices based on the current menu and command. Whenever you start typing, suggestion prompts will appear for existing commands and menus. When the command contains arguments, pressing the `space bar` after typing the command will present the list of available arguments. Note that a menu doesn't has arguments attached.

This functionality dramatically reduces the number of key strokes required to perform tasks and, in many cases, eliminates the need to consult the help dialogue for reminders. Choices - where they are bound by a defined list - are searchable with the up and down arrow keys.

## Global commands

These are commands that can be used throughout the CLI and will work regardless of the menu where they belong.

### Help

`--help`, or `-h` can be attached to any command, as described above.

### CLS

The `cls` command clears the entire CLI screen.

### Quit

The `quit` command (can also use `q` or `..`) allows to leave the current menu to go one menu above. If the user is on the root, that will mean leaving the CLI.

### Exit

The `exit` command allows the user to exit the CLI.

### Reset
