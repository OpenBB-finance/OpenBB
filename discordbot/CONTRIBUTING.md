## Code Structure and Contributing

UNDER DEVELOPMENT!

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
