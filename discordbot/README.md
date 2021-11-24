# Discord Bot - WORK IN PROGRESS

- [Discord Bot - WORK IN PROGRESS](#discord-bot---work-in-progress)
  - [Install Requirements](#install-requirements)
  - [Registering Applications](#registering-applications)
    - [DISCORD](#discord)
    - [IMGUR](#imgur)
    - [HEROKU](#heroku)
  - [Discord Configs](#discord-configs)
    - [Advanced](#advanced)
  - [Run Locally](#run-locally)
  - [Contributing](#contributing)
  - [Bugs](#bugs)

## Install Requirements

This tutorial assumes that you have successfully installed Gamestonk Terminal.

Next, go into the discordbot folder with `cd discordbot` and install the following packages:

```text
pip install discord
pip install discord_components
pip install pyimgur
pip install python-dotenv
```

## Registering Applications

### DISCORD

1. Login into your discord account in <https://discord.com/developers/applications>
2. On the "Applications" tab, select "New Application" and name it something like "GST Bot". This will create a new application.
3. For creating a bot, we need to go into the "GST Bot" application previously created, and on the "Bot" tab select
   "Add Bot".
4. Allow privileged gateway intents by enabling MESSAGE CONTENT INTENT under the bot tab.
5. Next we need to obtain the "Client ID". For that we choose the "OAuth2" tab and copy our "Client ID" under "Client".
6. At this stage the bot is created and we are ready to invite it to one of our servers. To do so we need to access:
<https://discord.com/oauth2/authorize?client_id=CLIENTID&scope=bot>, where **CLIENTID** is replaced by the value copied above.
7. If everything went well, you should see a window popup where the Bot that was just created asks to which of your own
   servers do you want to add it to.

**NOTE:** If you haven't managed the bot permissions on the Bot tab previously you can do it via this link generator
<https://discordapi.com/permissions.html>

### IMGUR

1. Login into your <https://imgur.com> account. Create one if you don't have it.
2. Access <https://api.imgur.com/oauth2/addclient> to create your application.
3. Select "OAuth 2 authorization without a callback URL" when creating such.
4. You will receive a client ID and client secret once you submit the form.

**NOTE:** Registering is free for all open source projects and if your discord bot uses fewer than 1250 uploads per day.

### HEROKU

1. Replace the general requirements.txt with the one in the discordbot folder.
2. Create a Heroku account at: <https://signup.heroku.com/>.
3. Click 'Create a new app'.
4. Go to the 'Settings' page, and then find Config Vars.
5. Add GT_DISCORD_BOT_TOKEN and GT_IMGUR_CLIENT_ID with their associated values.
6. Go to the repository:<https://github.com/GamestonkTerminal/GamestonkTerminal> and fork it if you have not already
   done so.
7. On the 'Deploy' page select Github as the deployment method.
8. Select 'enable automatic deploys' if you would like for the server to update every time you update your fork.
9. Go to the 'Resources' tab and turn on the worker by pressing the pencil to edit and then pressing the toggle button.

**NOTE:** If you only want the bot to run in the cloud you are done, if you would like it to run on your local machine
read below.

## Discord Configs

In order to config the discord bot you will need to edit the
[config_discordbot.py](gamestonk_terminal/config_discordbot.py) file.

1. Edit the path to the terminal by changing the variable `GST_PATH`. E.g.

   ```python
   GST_PATH = os.path.join("~", "Documents", "GamestonkTerminal")
   sys.path.append(GST_PATH)
   ```

2. Update `DISCORD_BOT_TOKEN` using discord bot CLIENT ID obtained previously in [discord](#discord).

3. Update `IMGUR_CLIENT_ID` using imgur application CLIENT ID obtained previously in [imgur](#imgur).

### Advanced

Other parameters that can be configured are:

- **DEBUG**: Shows a debug message on the terminal console of what's happening on the discord bot from the server side.
- **COMMAND_PREFIX**: Command prefix to be used when calling the bot from the discord server.
- **DATE_FORMAT**: Selects date format to be used as parameter on the discord bot.
- **COLOR**: Changes color of the bot messages replies on the discord server.
- **MENU_TIMEOUT**: Timeout in seconds to allow user to select options when a menu command is invoked from the discord bot.
- **AUTHOR_NAME**: Name of the discord bot in the server.
- **AUTHOR_ICON_URL**: Icon displayed on the discord bot replies on the server.

## Run Locally

Just run the discord bot from this folder with:

```text
python discordbot.py
```

Now, you should be ready to invoke the discord bot from server using something like:

```text
!stocks.dps TSLA
```

<img width="1211" alt="Screenshot 2021-10-18 at 00 21 30" src="https://user-images.githubusercontent.com/25267873/137649138-8d8158c5-1b76-49bc-928f-694d7005d94d.png">

## Contributing

See more in [CONTRIBUTING.md](discordbot/CONTRIBUTING.md).

## Bugs

If when trying to run the discord bot you receive the following error

```text
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

The solution is to browse to `Applications/Python 3.x` and double-click `Install Certificates.command`.

If an error occurs, use `DEBUG=True` on the [config_discordbot.py](gamestonk_terminal/config_discordbot.py) file.

Then, report what is the issue with the console output attached either by:

- [Opening an issue on github](https://github.com/GamestonkTerminal/GamestonkTerminal/issues/new/choose)
- Contacting either `DidierRLopes` (@SexyYear) or `northern-64bit`
