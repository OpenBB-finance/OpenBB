# Keychron Macros

This document will explain how you can set hotkeys on your Keychron keyboard which allow you to perform investment research in a few seconds. If you prefer to see this in video format, you can do so by checking the following video.

<p align="center">
   <a href="https://www.youtube.com/watch?v=cgeN3Ep2nEw" rel="Keychron x OpenBB Demo">
      <img src="https://user-images.githubusercontent.com/25267873/236660025-581d0e4f-df5e-4461-b2b9-70154c1bdf89.png" alt="Didier demonstrating Keychron x OpenBB" width="100%"/>
   </a>
</p>

## Introduction to Routines

The OpenBB Terminal is a powerful open source investment research platform.

The more proefficient you get on the platform, the faster and more efficiently you are able to do investment research.

One of the concepts that OpenBB introduced early on was the concept of script routines. Read more [here[(https://docs.openbb.co/terminal/usage/guides/scripts-and-routines).

**TL;DR: You can create MACROS like in Excel to run a sequence of commands.**

E.g. by running `exe script.openbb` the following sequence could be executed

```
stocks/load AAPL/candle --ma 20/fa/epsfc/pt/est
```

which would lead to:

![image](https://user-images.githubusercontent.com/25267873/236659876-e119c820-b9ed-40e7-bb8d-5510fe862149.png)

This allows to automate the process of investment research, and can improve user's experience by a significant margin.

## Why Keychron

We were in the market looking for a keyboard that could be highliy customizable for the needs of OpenBB power users. This is when we stumbled upon Keychron and the VIA configurator which allows users to intuitively remap any key on the keyboard, and create numerous macro commands, shortcuts, or key combinations.

[Why VIA is one of the most essential features for a custom keyboard?](https://www.keychron.com/blogs/news/why-qmk-via-is-one-of-the-most-essential-features-for-a-custom-keyboard)


## Setting up hotkey on Keychron 

For the purpose of this example, the command pipeline we are creating has the following sequence of commands: `dps/psi/../fa/pt/income/..`

This is what the output of running that in the [OpenBB Terminal](https://my.openbb.co/app/terminal) produced:

<img width="1784" alt="Screenshot 2023-05-06 at 10 53 49 PM" src="https://user-images.githubusercontent.com/25267873/236660272-290fe586-7663-4cd6-bfc0-80b7f8f2efd1.png">


