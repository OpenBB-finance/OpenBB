---
title: Server
sidebar_position: 3
description: Learn to customize your OpenBB Bot server experience.
keywords: [discord, telegram, server, customizing, customization, how to, explanation, openbb bot, openbb, guide, bot guide]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Server - Bot | OpenBB Docs" />

## Customizing your Server Bot Experience

The Server plan for OpenBB Bot offers three different capabilities - Charting, BillBoard, and Auto Posting. Any server that registers with us on the [OpenBB HUB](https://my.openbb.co) gets access to set up one Auto Posting for free. Once you have paid plan you have full access to all these features.

## Server

### Auto Posting (Discord Only)

Auto Posting is our most powerful feature for Discord Servers - We offer the ability to push updates into the server for Flow, Darkpool, or Heatmap/Charts. (more to come soon!) Once you set up your account you will be able to query the bot directly in your server like below :

<img src="https://openbb-assets.s3.amazonaws.com/discord/autopost/add.png" alt="autoposting openBB" width="40%" height="40%" />

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

### Charting

Custom charting works the same way as Individual charting but it will apply to your full server. If you want everyone in your server to use the "Classic" theme and have RSI + 50d SMA then it will display that way for all users in your server (unless they have already registered their own individual account).

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/server-charting.png" alt="server charting openBB" width="70%" height="70%" />

### BillBoard

BillBoard is a way to advertise to your users when they run a command on the bot. Within your server you can set your own text to display on applicable commands as they are run.

<img src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/billboard.png" alt="billboard openBB" width="70%" height="70%" />
