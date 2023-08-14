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
    big sur,
    intel,
    intel-based,
    apple silicon,
    m1,
    dmg file
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="MacOS - Terminal | OpenBB Docs" />

import InstallerButton from "@site/src/components/General/InstallerButton";

Install the OpenBB Terminal on MacOS (Big Sur or later). There are two versions of the installers available for MacOS, Intel-based and Apple Silicon (M1).

<div style={{
  height: 80
}}>
<InstallerButton href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v3.2.1/x86.64.MacOS.OpenBB.Terminal.v3.2.1.pkg" label="Mac Intel Installer" />  <InstallerButton href="https://github.com/OpenBB-finance/OpenBBTerminal/releases/download/v3.2.1/ARM64.MacOS.OpenBB.Terminal.v3.2.1.pkg" label="Mac M1 Installer" />
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

1. Press ⌘ (Command) + SPACE to open spotlight search, and type "Terminal" and hit Return (⏎).
2. Copy and paste the following code in the Terminal and hit ENTER (⏎):

  ```console
  softwareupdate --install-rosetta
  ```

3. This will start up the Rosetta installation process and you will receive a message regarding the Licence Agreement. Type `A` and hit Return (⏎).
4. After the installation process has finished, you can proceed by clicking on the "Mac M1 Installer" button.

</details>
:::

Step by step instructions:

1. Download the PKG file from the links above.

2. Launch the PKG installer by double-clicking on it.
<img width="634" alt="image" src="https://user-images.githubusercontent.com/11668535/234018847-f3e76345-7d4e-445d-a462-64e0d6d902bd.png"></img>

3. Follow the Installer prompt. You will be asked to enter your system password.
<img width="638" alt="image" src="https://user-images.githubusercontent.com/11668535/234032407-8ca009a7-0545-4196-b671-5bcc4c5cea9b.png"></img>

4. This process installs the application into the `/Application/OpenBB Terminal` folder.
<img width="618" alt="image" src="https://user-images.githubusercontent.com/11668535/234034347-cb2a80a0-81bb-4e8d-b91e-b636e161cf32.png"></img>

5. Launch the application by double-clicking on the `OpenBB Terminal` application. If everything was successful you should see a screen like the one below:

<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/223194653-a21966e2-cd55-44da-95eb-7c66811f629b.png"><img alt="run_the_terminal" src="https://user-images.githubusercontent.com/46355364/223194653-a21966e2-cd55-44da-95eb-7c66811f629b.png"></img></a></p>

**Note:** During the first launch, a warning message may appear. Click, "Open". If you get a warning about opening apps from an unverified developer, please follow the instructions on <a href="https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac">this MacOS User Guide page</a> to proceed.

<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/85772166/220201620-1c42bbd4-7509-41fc-8df8-389f34fde58a.png"><img alt="run_the_terminal" src="https://user-images.githubusercontent.com/85772166/220201620-1c42bbd4-7509-41fc-8df8-389f34fde58a.png"></img></a></p>
