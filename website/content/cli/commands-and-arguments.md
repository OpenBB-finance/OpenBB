---
title: Commands And Arguments
sidebar_position: 4
description: This page explains how to enter commands and arguments into the OpenBB Platform CLI.
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

<HeadTitle title="Commands And Arguments | OpenBB Platform CLI Docs" />

Commands are displayed on-screen in a lighter colour, compared with menu items, and they will not be prefaced with, `>`.

Functions have a variety of parameters that differ by endpoint and provider. The --help dialogue will provide guidance on nuances of any particular command.

The available data sources for each command are displayed on the right side of the screen, and are selected with the `--provider` argument.

## Help arguments

The `help` command shows the current menu. The screen will display all the commands and menus that exist, including a short description for each of these.

Adding `--help`, or `-h`, to any command will display the description and parameters for that particular function.

## Entering Parameters

Parameters are all defined through the same pattern, --argument, followed by a space, and then the value.

If the parameter is a boolean (true/false), there is no value to enter. Adding the --argument flags the parameter to be the opposite of its default state.

Use the auto-complete to prompt choices and reduce the amount of keystrokes required to run a complex function.

## Auto-complete

The OpenBB Platform CLI is equipped with an auto completion engine that presents choices based on the current menu and command. Whenever you start typing, suggestion prompts will appear for existing commands and menus. When the command contains arguments, pressing the `space bar` after typing the command will present the list of available arguments.

This functionality dramatically reduces the number of key strokes required to perform tasks and, in many cases, eliminates the need to consult the help dialogue for reminders. Choices - where they are bound by a defined list - are scrollable with the up and down arrow keys.

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

The `reset` command will reset the CLI to its default state. This is specially useful for development so you can refresh the CLI without having to close and open it again.

### Results

The `results` command will display the stack of `OBBjects` that have been generated during the session, which can be later injected on the data processing commands.
