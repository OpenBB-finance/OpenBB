---
title: Keyboard Hotkey Macros
sidebar_position: 6
description: Create keyboard hotkey macros to run a sequence of commands
keywords:
  [
    keyboard,
    macros,
    commands,
    pipeline,
    excel,
    customizable,
    hotkey,
    remap,
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Keyboard Hotkey Macros - Terminal | OpenBB Docs" />

This document will explain how you can set hotkeys macros on your customizable keyboard which allow you to perform investment research in a few seconds.

## Introduction to Routines

The OpenBB Terminal is a powerful open source investment research platform.

The more proefficient you get on the platform, the faster and more efficiently you are able to do investment research.

One of the concepts that OpenBB introduced early on was the concept of script routines. Read more [here](https://docs.openbb.co/terminal/usage/guides/scripts-and-routines).

**TL;DR: You can create MACROS like in Excel to run a sequence of commands.**

E.g. by running `exe script.openbb` the following sequence could be executed

```console
stocks/load AAPL/candle --ma 20/fa/epsfc/pt/est
```

which would lead to:

<img width="1441" alt="image" src="https://user-images.githubusercontent.com/25267873/236659876-e119c820-b9ed-40e7-bb8d-5510fe862149.png" />

This allows to automate the process of investment research, and can improve user's experience by a significant margin.

## Supported Configurators

1. [VIA](#via)

## VIA

This document will explain how you can set hotkeys on your customizable keyboard using [VIA](https://www.caniusevia.com/).

Here is a list of VIA's supported keyboards: [https://www.caniusevia.com/docs/supported_keyboards](https://www.caniusevia.com/docs/supported_keyboards)

Note: We were in the market looking for a keyboard that could be highliy customizable for the needs of OpenBB power users. This is when we stumbled upon Keychron and the VIA configurator which allows users to intuitively remap any key on the keyboard, and create numerous macro commands, shortcuts, or key combinations.
Here's a post from Keychron on VIA: [Why VIA is one of the most essential features for a custom keyboard?](https://www.keychron.com/blogs/news/why-qmk-via-is-one-of-the-most-essential-features-for-a-custom-keyboard)

For the purpose of this example, the command pipeline we are creating has the following sequence of commands: `dps/psi/../fa/pt/income/..`

1. Try VIA [here](https://usevia.app/). The following screen should popup

![VIA](https://user-images.githubusercontent.com/25267873/236660856-f92ac602-cde9-48e6-8029-c083fbb75ff9.png)

2. Select the Layer you are interested in altering. As we're not looking forward to remap any of the existing main keys, we need to go to layer 2, 3 or 4. In my case, with a Keychron Q2, I know that Layer 4 can be accessed by pressing on "Fn2". Thus, I select that layer.

![Layer](https://user-images.githubusercontent.com/25267873/236660841-09203874-8a8e-4393-8674-357aad67a22b.png)

3. Most keys should have a triangle upside down which simbolizes that they don't have any functionality. You want to select one of those keys to contain your hotkey routine. After that selection you want to remap the key functionality, hence in the **KEYMAP settings** below you click on MACROS tab and select "MO". Now the screen should look like this:

![Layer](https://user-images.githubusercontent.com/25267873/236660948-a148582e-f928-4f12-ae54-9bdd3adfd020.png)

4. Now we want to change what "MO" does and for that we select the **MACROS settings** below. Then we can select "M0" and insert `dps/psi/../fa/pt/income/..{KC_ENT}`. The screen should look like this:

![Macro](https://user-images.githubusercontent.com/25267873/236661126-eeb5dc7c-2c01-4a43-ab64-12c470e864ce.png)

Note that the `{KC_ENT}` will ensure that the command is run on the terminal.

5. Save. To ensure that everything is correct you can go into the **KEYMAP settings** and click on the hotkey that you just created to see if it contains the sequence of commands, the following sequence should appear:

![Save](https://user-images.githubusercontent.com/25267873/236661232-4f9119de-af37-49a2-948d-cfd6d650ed92.png)

6. Finally, we are ready to test it on the [OpenBB Terminal](https://my.openbb.co/app/terminal). After going into `stocks` and doing `load AAPL`, I pressed "Fn2'+Z which lead to:

![Test](https://user-images.githubusercontent.com/25267873/236660272-290fe586-7663-4cd6-bfc0-80b7f8f2efd1.png)

PS: If you prefer to see this in video format, you can do so by checking the following video.

<p align="center">
   <a href="https://www.youtube.com/watch?v=cgeN3Ep2nEw" rel="Keychron x OpenBB Demo">
      <img src="https://user-images.githubusercontent.com/25267873/236660025-581d0e4f-df5e-4461-b2b9-70154c1bdf89.png" alt="Didier demonstrating Keychron x OpenBB" width="100%"/>
   </a>
</p>

Hope you enjoy this tutorial, and please let us know what type of MACROS are you setting up.
