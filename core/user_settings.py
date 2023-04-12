from openbb_terminal.commands.user import set_prompt

# ...

class UserSettingsMenu:
    def __init__(self):
        self.menu_items = [
            # ... add other menu items here ...
            ConsoleMenuItem("Set prompt text", set_prompt),
        ]
