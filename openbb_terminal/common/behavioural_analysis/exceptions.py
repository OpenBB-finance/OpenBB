from openbb_terminal.rich_config import console


class APITimeoutError(Exception):
    """API Timeout Error"""

    def __init__(self):
        super().__init__()
        console.print("[red]API is not responding - timeout.[/red]\n")
