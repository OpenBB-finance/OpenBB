"""Rich Module."""

__docformat__ = "numpy"


RICH_TAGS = [
    "[menu]",
    "[/menu]",
    "[cmds]",
    "[/cmds]",
    "[info]",
    "[/info]",
    "[param]",
    "[/param]",
    "[src]",
    "[/src]",
    "[help]",
    "[/help]",
]


class MenuText:
    """Create menu text with rich colors to be displayed by CLI."""

    CMD_NAME_LENGTH = 23
    CMD_DESCRIPTION_LENGTH = 65
    CMD_PROVIDERS_LENGTH = 23
    SECTION_SPACING = 4

    def __init__(self, path: str = ""):
        """Initialize menu help."""
        self.menu_text = ""
        self.menu_path = path
        self.warnings: list[dict[str, str]] = []

    @staticmethod
    def _get_providers(command_path: str) -> list:
        """Return the preferred provider for the given command.

        Parameters
        ----------
        command_path: str
            The command to find the provider for. E.g. "/equity/price/historical

        Returns
        -------
        List
            The list of providers for the given command.
        """
        try:
            from openbb import obb
        except ImportError:
            return []
        command_reference = obb.reference.get("paths", {}).get(command_path, {})  # ty: ignore[unresolved-attribute]
        if command_reference:
            providers = list(command_reference["parameters"].keys())
            return [provider for provider in providers if provider != "standard"]
        return []

    def _format_cmd_name(self, name: str) -> str:
        """Return command name as-is without truncation."""
        return name

    def _format_cmd_description(
        self, name: str, description: str, trim: bool = True
    ) -> str:
        """Truncate command description length if it is too long."""
        if not description or description == f"{self.menu_path}{name}":
            description = ""
        return (
            description[: self.CMD_DESCRIPTION_LENGTH - 3] + "..."
            if len(description) > self.CMD_DESCRIPTION_LENGTH and trim
            else description
        )

    def add_raw(self, text: str, left_spacing: bool = False):
        """Append raw text (without translation)."""
        if left_spacing:
            self.menu_text += f"{self.SECTION_SPACING * ' '}{text}\n"
        else:
            self.menu_text += text

    def add_info(self, text: str):
        """Append information text (after translation)."""
        self.menu_text += f"[info]{text}:[/info]\n"

    def add_cmd(self, name: str, description: str = "", disable: bool = False):
        """Append command text (after translation)."""
        formatted_name = self._format_cmd_name(name)
        name_padding = (self.CMD_NAME_LENGTH - len(formatted_name)) * " "
        providers = self._get_providers(f"{self.menu_path}{name}")
        formatted_description = self._format_cmd_description(
            formatted_name,
            description,
            bool(providers),
        )
        description_padding = (
            self.CMD_DESCRIPTION_LENGTH - len(formatted_description)
        ) * " "
        spacing = self.SECTION_SPACING * " "
        description_padding = (
            self.CMD_DESCRIPTION_LENGTH - len(formatted_description)
        ) * " "
        cmd = f"{spacing}{formatted_name + name_padding}{spacing}{formatted_description + description_padding}"
        cmd = f"[unvl]{cmd}[/unvl]" if disable else f"[cmds]{cmd}[/cmds]"

        if providers:
            cmd += rf"{spacing}[src]\[{', '.join(providers)}][/src]"

        self.menu_text += cmd + "\n"

    def add_menu(
        self,
        name: str,
        description: str = "",
        disable: bool = False,
    ):
        """Append menu text (after translation)."""
        spacing = (self.CMD_NAME_LENGTH - len(name) + self.SECTION_SPACING) * " "

        if not description or description == f"{self.menu_path}{name}":
            description = ""

        if len(description) > self.CMD_DESCRIPTION_LENGTH:
            description = description[: self.CMD_DESCRIPTION_LENGTH - 3] + "..."

        menu = f"{name}{spacing}{description}"
        tag = "unvl" if disable else "menu"
        self.menu_text += f"[{tag}]>   {menu}[/{tag}]\n"

    def add_setting(self, name: str, status: bool = True, description: str = ""):
        """Append menu text (after translation)."""
        spacing = (self.CMD_NAME_LENGTH - len(name) + self.SECTION_SPACING) * " "
        indentation = self.SECTION_SPACING * " "
        color = "green" if status else "red"

        self.menu_text += (
            f"[{color}]{indentation}{name}{spacing}{description}[/{color}]\n"
        )
