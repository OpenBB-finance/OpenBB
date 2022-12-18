---
title: Importing and Exporting Data
sidebar_position: 3
---

The OpenBB SDK shares the `OpenBBUserData` folder with the Terminal, even with multiple versions installed on the same machine. Portfolio files, screener presets, and Matplotlib style sheets are all shared resources. This folder will be created after the first installation and it is read by subsequent installations. The default location for it is in the root of the operating system user account folder.

The `OpenBBUserData` folder's default location is the home of the system user account. By default this will be the following paths:
- macOS: `Macintosh HD/Users/<YOUR_USERNAME>/OpenBBUserData`
- Windows: `C:/Users/<YOUR_USERNAME>/OpenBBUserData`

Within the folder you can find files that you have exported as well as files that you wish to import directly into the OpenBB Terminal. For example, this could be an orderbook which you can store in `OpenBBUserData/portfolio/holdings`.

<img width="1231" alt="Screen Shot 2022-10-13 at 6 45 01 PM" src="https://user-images.githubusercontent.com/85772166/195742985-19f0e420-d8f7-4fea-a145-a0243b8f2ddc.png"></img>

This folder contains all things user-created which are, among other things screener presets, portfolio files, files exported directly from the code, styles and themes, preferred data sources and API keys.
