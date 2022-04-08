# pylint: skip-file
import asyncio
import os
import sys
from typing import Any

import disnake
from disnake.ext import commands
from fastapi import FastAPI, Request

from bots import config_discordbot as cfg
from bots.groupme.run_groupme import handle_groupme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.loggers import setup_logging
from bots.discord import helpers


app = FastAPI()


MISSING: Any = helpers._MissingSentinel()


@app.get("/")
async def read_root():
    return {"Hello": str(gst_bot.user)}


@app.post("/")
async def write_root(request: Request):
    # TODO: Make this work for more bots
    req_info = await request.body()
    value = handle_groupme(req_info)
    return {"Worked": value}


activity = disnake.Activity(
    type=disnake.ActivityType.watching,
    name="OpenBB Terminal: https://github.com/OpenBB-finance/OpenBBTerminal",
)


if cfg.IMGUR_CLIENT_ID == "REPLACE_ME" or cfg.DISCORD_BOT_TOKEN == "REPLACE_ME":
    logger.info(
        "Update IMGUR_CLIENT_ID or DISCORD_BOT_TOKEN or both in %s \n",
        os.path.join("discordbot", "config_discordbot"),
    )
    sys.exit()
print(f"disnake: {disnake.__version__}\n")


gst_bot = GSTBot()
gst_bot.load_all_extensions("cmds")


async def run():
    try:
        await gst_bot.start(cfg.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        await gst_bot.logout()


asyncio.create_task(run())
