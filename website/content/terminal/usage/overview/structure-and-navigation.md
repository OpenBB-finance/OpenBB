---
title: Structure and Navigation
sidebar_position: 1
description: Provides a brief overview of how to interact with the OpenBB Terminal
keywords: [finance, terminal, command line interface, cli, menu, commands]
---

## Structure

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/8qjG_SyuQgY?si=kc948AQLp3yrfkgB"
  videoLegend="Short introduction to terminal structure"
/>

The OpenBB Terminal is a Command Line Interface (CLI) application. Functions (commands) are called through the keyboard with results returned as charts, tables, or text.  Charts and tables (if enabled) are displayed in a new window, and are fully interactive, while text prints directly to the Terminal screen.

![The Home Screen](https://user-images.githubusercontent.com/85772166/233247655-2f8d0dae-be68-48ca-9b35-123b5b985cb6.png)

A menu is a collection of commands (and sub-menus). A menu can be distinguished from a command because the former has a `>` on the left. The color of a command and a menu also differ, but these can be changed in OpenBB Hub's theme style.

## Navigation

Navigating through the Terminal menus is similar to traversing folders from any operating system's command line prompt. The `/home` screen is the main directory where everything begins, and the menus are paths branched from the main. Instead of `C:\Users\OpenBB\Documents`, you'll have something like `/stocks/options`. Instead of `cd ..`, you can do `..` to return the menu right above. To go back to the root menu you can do `/`.

Absolute paths are also valid to-and-from any point. From the [`/stocks/options`](https://docs.openbb.co/terminal/usage/intros/stocks/options) menu, you can go directly to [`crypto`](https://docs.openbb.co/terminal/usage/intros/crypto) menu with: `/crypto`. Note the forward slash at the start to denote the "absolute" path.


<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/xy8LElyYmaI?si=psfs7nD9xjb-N1N8"
  videoLegend="Short introduction to navigation"
/>
