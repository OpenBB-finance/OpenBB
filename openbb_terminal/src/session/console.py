from pathlib import Path

from src.config.base_console import (
    BaseConsole,
    RichConsole,
    Theme,
)
from src.config.terminal_style import TerminalStyle
from src.session.settings import get_current_settings
from src.session.user import get_platform_user


class Console(BaseConsole):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print(self, *args, **kwargs):
        """Print to the console."""
        self._reload_console()
        return super().print(*args, **kwargs)

    def _reload_console(self):
        """Reload the console with the current settings."""
        self.settings = get_current_settings()
        terminal_style.apply_console_style(self.settings.RICH_STYLE)
        self._console = RichConsole(
            theme=Theme(terminal_style.console_style), highlight=False, soft_wrap=True
        )


terminal_style = TerminalStyle(
    style=get_current_settings().RICH_STYLE,
    user_styles_directory=Path(get_platform_user().preferences.user_styles_directory),
)
console = Console(style=terminal_style.console_style)
