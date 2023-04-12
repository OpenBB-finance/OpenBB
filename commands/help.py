from openbb_terminal.commands.user import set_prompt

# ...

def get_help_text() -> str:
    # ... add other command help messages here ...
    help_text += "\n\n" + set_prompt.get_help(ctx=None)
    return help_text
