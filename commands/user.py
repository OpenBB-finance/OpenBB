rom openbb_terminal.core.config.user_preferences import (
    get_local_user,
    set_local_user_preference,
)

# ...

@click.command()
@click.argument("prompt_text")
def set_prompt(prompt_text: str):
    user = get_local_user()
    set_local_user_preference(user, "PROMPT_TEXT", prompt_text)
    console.print(f"Prompt text set to '{prompt_text}'")
