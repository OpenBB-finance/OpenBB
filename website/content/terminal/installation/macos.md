---
title: MacOS
sidebar_position: 2
description: Install the OpenBB Terminal on MacOS (Big Sur or later). There are two versions of the installers available for MacOS, Intel-based and Apple Silicon (M1).
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb terminal,
  ]
---

import InstallerButton from "@site/src/components/General/InstallerButton";

Install the OpenBB Terminal on MacOS (Big Sur or later). There are two versions of the installers available for MacOS, Intel-based and Apple Silicon (M1).

<div style={{
  height: 80
}}>
<InstallerButton href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v2.5.1/x86.64.MacOS.OpenBB.Terminal.v2.5.1.dmg" label="Mac Intel Installer" />  <InstallerButton href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v2.5.1/ARM64.MacOS.OpenBB.Terminal.v2.5.1.dmg" label="Mac M1 Installer" />
</div>

<details><summary>Minimum Requirements</summary>

- MacOS Monterey or newer
- Modern CPU (Intel processor made in the last 5 years or Apple Silicon chip)
- At least 4GB of RAM
- At least 5GB of free storage
- Internet connection (cable or 4G mobile)

</details>

:::info Apple Silicon users will need to install Rosetta prior to installation
To understand whether you are using an Apple Sillicon (M1) device or an Intel-based device click on the Apple Icon at the top left of your MacBook and select "About This Mac". Then under "Chip" if it says something like "Apple M1 Pro" or "Apple M1 Max", you know you have an Apple Silicon MacBook. If it says for example "2,3 GHz Quad-Core Intel Core i7" you know that you have an Intel-based MacBook and you can continue by clicking on the "Mac Intel Installer" button.

<details><summary>Rosetta Installation Instructions (Apple Sillicon users only)</summary>

1. Press ⌘ (Command) + SPACE to open spotlight search, and type `Terminal` and hit Return (⏎).
2. Copy and paste the following code in the Terminal and hit ENTER (⏎):

```console
softwareupdate --install-rosetta
```

3. This will start up the Rosetta installation process and you will receive a message regarding the Licence Agreement. Type `A` and hit Return (⏎).
4. After the installation process has finished, you can proceed to the "Mac M1 Installer" button.

</details>
:::

Step by step instructions:

1. Download the DMG file from the links above.
2. Mount the downloaded DMG file by double-clicking on it.
3. Click and drag the OpenBB Terminal folder and hold it over the Applications shortcut. This opens a new Finder window, then drag the OpenBB Terminal folder into the Applications folder.

![MacOS Installation](https://user-images.githubusercontent.com/11668535/173027899-9b25ae4f-1eef-462c-9dc9-86086e9cf197.png)

4. Unmount the installer, by "Ejecting OpenBB Terminal" from, locations, in Finder.

5. Launch the application by double-clicking on the `OpenBB Terminal` application. If everything was successful you should see a screen like the one below:

<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/223194653-a21966e2-cd55-44da-95eb-7c66811f629b.png"><img alt="run_the_terminal" src="https://user-images.githubusercontent.com/46355364/223194653-a21966e2-cd55-44da-95eb-7c66811f629b.png"></img></a></p>

**Note:** During the first launch, a warning message may appear. Click, "Open".

<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/85772166/220201620-1c42bbd4-7509-41fc-8df8-389f34fde58a.png"><img alt="run_the_terminal" src="https://user-images.githubusercontent.com/85772166/220201620-1c42bbd4-7509-41fc-8df8-389f34fde58a.png"></img></a></p>
