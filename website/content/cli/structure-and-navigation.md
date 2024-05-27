---
title: Structure and Navigation
sidebar_position: 3
description: This page describes the layout and structure of the OpenBB Platform CLI, as well as how to navigate it.
keywords:
- CLI application
- OpenBB Platform CLI
- structure
- navigation
- Command Line Interface
- navigating
- Home
- commands
- menus
- OpenBB Hub Theme Style
- Absolute paths
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Structure and Navigation | OpenBB Platform CLI Docs" />

## Structure

The OpenBB Platform CLI is a Command Line Interface (CLI) application. Functions (commands) are called through the keyboard with results returned as charts, tables, or text.  Charts and tables (if enabled) are displayed in a new window, and are fully interactive, while text prints directly to the Terminal screen.

A menu is a collection of commands (and sub-menus). A menu can be distinguished from a command because the former has a `>` on the left. The color of a command and a menu also differ, but these can be changed in OpenBB Hub's theme style.

## Navigation

Navigating through the CLI menus is similar to traversing folders from any operating system's command line prompt. The `/home` screen is the main directory where everything begins, and the menus are paths branched from the main. Instead of `C:\Users\OpenBB\Documents`, you'll have something like `/equity/price`. Instead of `cd ..`, you can do `..` to return the menu right above. To go back to the root menu you can do `/`.

### Absolute Paths

Absolute paths are also valid to-and-from any point. From the `/equity/price` menu, you can go directly to `crypto` menu with: `/crypto`. Note the forward slash at the start to denote the "absolute" path.

### Home

Return to the Home screen from anywhere by entering any of the following:

- `/`
- `home`
