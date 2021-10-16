# DiscordBot
Implementation of a discord bot, which is WORK IN PROGRESS

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/GamestonkTerminal/DiscordBot">
    <img src="images/gst_logo_lockup_rGreen_with_letters.png" alt="Logo" width="800" height="276">
  </a>

## Set Up

### Step 1: Getting a discord bot
Go to https://discord.com/developers/applications and click on "New Application" (See Picture 1)
Enter a name for example "Gamestonk Terminal Discord Bot"
Picture 1:
<img src="images/picture_1.png" alt="Logo" width="1183" height="157">
Then go to the bot page:
<img src="images/picture_2.png" alt="Logo" width="1183" height="251">
Then press "Add Bot":
<img src="images/picture_3.png" alt="Logo" width="1183" height="324">
Now go to your applications "OAuth2" Tab:

<img src="images/picture_4.png" alt="Logo" width="455" height="423">
Then copy your Client ID:
<img src="images/picture_5.png" alt="Logo" width="1183" height="301">
Then invite your bot to your discord server by replacing the ENTERCLIENTID with your copied client ID in this url: https://discord.com/oauth2/authorize?client_id=ENTERCLIENTID&scope=bot (You can also do it on via this link generator https://discordapi.com/permissions.html where you can select the proper permissions)
After clicking the link you'll see something similar to this:
<img src="images/picture_6.png" alt="Logo" width="472" height="624">
Register your app <a href="https://imgur.com/signin?redirect=http://api.imgur.com/oauth2/addclient" class="dy ie" rel="noopener ugc nofollow">here</a>. Choose “OAuth 2 authorization without a callback URL”. Registering is free for all open source projects and if your discord bot uses fewer than 1,250 uploads per day. You will receive an client ID and client secret once you submit the form.

### Step 2: Get the scripts to run the GST Discord Bot

(Note this assumes that you already have installed GST for more info about the installation: https://github.com/GamestonkTerminal/GamestonkTerminal#getting-started)

Download the code from this repository.

Then open the config_discordbot.py file and go back to https://discord.com/developers/applications/ and go to your bot page. There you'll have to copy the token
<img src="images/picture_7.png" alt="Logo" width="1183" height="419">

Then change the settings in the config_discordbot.py. Make sure to add the proper filepath to the GamestonkTerminal folder.
Add your discord token and imgur id to your environment variables as "GT_DISCORD_BOT_TOKEN" & "GT_IMGUR_CLIENT_ID" or
change the string in the config. You can also change the command prefix, date format, debug mode and other parameters in the settings
part of the config file.

From the config_discordbot.py file:
```
# Path to the terminal
GST_PATH = os.path.join("~", "Documents", "GamestonkTerminal")
sys.path.append(GST_PATH)

# https://discord.com/developers/applications/
DISCORD_BOT_TOKEN = os.getenv("GT_DISCORD_BOT_TOKEN") or "REPLACE_ME"

# https://apidocs.imgur.com
IMGUR_CLIENT_ID = os.getenv("GT_IMGUR_CLIENT_ID") or "REPLACE_ME"

# Settings
COMMAND_PREFIX = "!"
DATE_FORMAT = "%Y-%m-%d"
COLOR = discord.Color.from_rgb(0, 206, 154)
MENU_TIMEOUT = 30
DEBUG = True

AUTHOR_NAME = "Gamestonk Terminal"
AUTHOR_ICON_URL = (
    "https://github.com/GamestonkTerminal/GamestonkTerminal/"
    "blob/main/images/gst_logo_green_white_background.png?raw=true"
)
```

### Step 3:
Activate your GST virtual environment and go to the place where your main.py file is located and run it.
<img src="images/image.png" alt="Logo" width="1167" height="294">
You're finished! Go to your server and you should see the bot online!!!

## Code Structure and Contributing
The file system is built in the following way:
- Each command is one file with the essential functions for the command and is named COMMANDNAME.py.
- Each context is a directory and has a menu file named CONTEXT_menu.py.
- The menu file works by controlling every command in the context and it contains the menu command.
- discordbot.py can loads every menu file from each context.
- The settings shall be in the config_discordbot.py file (example: API keys).

If a function is often used by multiple files then add them to the helpers.py file. Please try to use the _view files
from the GST to get the data for the commands if possible.

Feel free to contribute to the discord bot, add more contexts, commands or just do other improvements. To see the
current prioritize of the development see the TODO list in the discord bot project
(https://github.com/GamestonkTerminal/GamestonkTerminal/projects/4).

## What if something doesn't work?

Make sure to follow the steps in the download guide. If an error occurs anyway then activate the debug mode in the
config file and see where the error occurs in your terminal. Join the GST discord and report your issue in the #bugs
channel. Otherwise, there's the possibility to open a GitHub issue or message northern-64bit.

