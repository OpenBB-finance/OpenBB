---
title: Server
sidebar_position: 3
description: Learn about OpenBB Bot's Server plan that offers powerful features such
  as auto posting for Discord, custom charting, and a billboard for advertising. Perfect
  for optimizing your server operations.
keywords:
- OpenBB Bot Server Plan
- Discord Server Optimisation
- Auto Posting in Discord
- OpenBB Auto Posting Categories
- Custom Charting
- OpenBB Bot Billboard
- OpenBB HUB
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Server - Customizing - Usage | OpenBB Bot Docs" />

The Server plan for OpenBB Bot offers three different capabilities - Charting, BillBoard, and Auto Posting. Any server that registers with us on the [OpenBB HUB](https://my.openbb.co) gets access to set up one Auto Posting for free. Once you have paid plan you have full access to all these features.

## Auto Posting (Feeds) (Discord Only)

Auto Posting is our most powerful feature for Discord Servers - We offer the ability to push updates into the server for Flow, Darkpool, or Heatmap/Charts. Once you set up your account you will be able to query the bot directly in your server like below :

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/autopost.png" alt="autoposting openBB" width="40%" height="40%" />

Or you can manage them at the HUB :
<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/autoposting.png" alt="autoposting openBB" width="70%" height="70%" />

We currently offer the following Auto Posting Categories:

| Category | Description |  Choices |
| ---- | ----------- | ------- |
| Flow  | Options Flow for all stocks | Opening, Golden Sweep, Large, Unusual, Weekly, Above Ask/Below Bid, Sell to Open, Buy to Open, Whale |
| Darkpool  | Darkpool Data for the market | Large |
| Heatmap  | Overview of the market | S&P 500, Dow Jones 30, NASDAQ 100, Russell 1000, Russell 2000, Crypto, Heatchart |

For a further breakdown on what each Flow Auto Post entails - See below

| Type | Description |
| ---- | ----------- |
|   Opening   |  "Premium > $200,000" & "Volume > Open Interest"  |
|   Golden Sweep   |   "Premium > $1,000,000" & "Volume > Open Interest" & "Trade Type is SWEEP"  |
|   Large   |     "Premium > $500,000"    |
|   Unusual   |    "Premium > $200,000" & "Unusual" (high ratio of volume to open interest)      |
|   Weekly   |     "Premium > $200,000" & "Days to Expiration < 7"        |
|   Above Ask/Below Bid   |   "Premium > $200,000" & "Side is Above Ask or Below Bid"          |
|   Sell to Open   |     "Premium > $1,000,000" & "Volume > Open Interest" & "Trade Type is Below Bed"        |
|   Buy to Open   |     "Premium > $1,000,000" & "Volume > Open Interest" & "Trade Type is Above Ask"        |
|   Whale   |    "Premium > $1.000,000" & "Days to Expiration < 45"         |


## Auto Posting (Commands) (Discord Only)

Much like Feeds we now offer Commands to be set up as autoposts as well - These behave in the same way but can be setup to autopost bot commands.

Once you set up your account you will be able to query the bot directly in your server like below :
<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/commands+add.png" alt="commands add openBB" width="40%" height="40%" />

Commands as autoposts are a great way to get your community the info they need in a timely manner.

We have allowed even more autoposts to be set up in your server so you can really create a fun environment for all your needs:
<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/autopost+list.png" alt="autopost list openBB" width="40%" height="40%" />

Below are a few examples of autoposts set up as commands in a server :

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/earnings+example.png" alt="earnings command autopost openBB" width="40%" height="40%" />

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/flow+example.png" alt="earnings command autopost openBB" width="40%" height="40%" />

## Charting

Custom charting works the same way as Individual charting but it will apply to your full server. If you want everyone in your server to use the "Classic" theme and have RSI + 50d SMA then it will display that way for all users in your server (unless they have already registered their own individual account).

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/server-charting.png" alt="server charting openBB" width="70%" height="70%" />

## Billboard

Billboard is a way to advertise to your users when they run a command on the bot. Within your server you can set your own text to display on applicable commands as they are run.

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/billboard.png" alt="billboard openBB" width="70%" height="70%" />
