---
title: Telegram
sidebar_position: 2
description: A complete guide on how to use the OpenBB Telegram Bot for stock and
  crypto market exploration. Learn how to use slash commands, including /cd, /c3m,
  /flow, and /c for market insights.
keywords:
- Telegram
- /cd command
- /c3m command
- /flow command
- /c command
- OpenBB Telegram Bot
- stock ticker
- crypto symbol
- market exploration
- using bots
- Telegram commands
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Telegram - Usage | OpenBB Bot Docs" />

Now that you have added the bot to your Telegram server you can get started with running commands.

To use it, you need to type slash commands in the chat. A slash command starts with a / followed by a keyword and an optional argument. For example, ```/cd AAPL``` will show you the daily chart for Apple stock.

<div className="flex justify-center h-full w-[800px] rounded-r-[4px]">
  <img
    className="h-full object-cover"
    alt="gif describing step"
    src="https://openbb-assets.s3.amazonaws.com/docs/bot_docs/telegram-gif.gif"
  />
</div>

<details><summary>How do I select commands instead of typing?</summary>
If you are On mobile press and hold to select the command.

On desktop press ```tab``` to select the command.
</details>


To see all the available commands, you can type ```/help``` in the chat. This will show you a list of commands and their descriptions. You can also tap on any command to use it directly. Some of the most popular commands are:

- ```/cd AMD``` Shows the daily chart for a given stock ticker.
- ```/c3m AMD``` Shows the 3-month chart for a given stock ticker.
- ```/flow AMD``` Shows the recent options flow for the given stock ticker.
- ```/c DOGE``` Shows a chart for the crypto symbol provided.

That's it! You're ready to use OpenBB Telegram Bot and explore the markets. Have fun!

Check out the Reference section for more commands or type ```/help``` in your chat to see what else we can do!
