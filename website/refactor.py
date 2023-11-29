import json
from pathlib import Path
from typing import Callable, List, Literal, Optional

from openbb_core.app.static.package_builder import PathHandler

# Paths
WEBSITE_PATH = Path(__file__).parent.absolute()
CONTENT_PATH = WEBSITE_PATH / "content"


class CommandLib(PathHandler):
    def __init__(self):
        self.route_map = self.build_route_map()

    def get_cmd_list(self) -> List[str]:
        """Get a list of all the commands in the docs."""
        return sorted(self.build_path_list(route_map=self.route_map))

    def get_cmd_func(self, cmd: str) -> Optional[Callable]:
        """Get the func of the command."""
        return getattr(self.route_map.get(cmd, None), "endpoint", None)

    def get_cmd_info(self, cmd: str) -> dict:
        """Get the info for a command."""
        return {}


class Editor:
    """Editor for the website docs."""

    def __init__(
        self,
        directory: Path,
        interface: Literal["excel", "markdown"],
        output: Literal["reference", "data_models"],
        cmd_lib: CommandLib,
    ) -> None:
        """Initialize the editor."""
        self.directory = directory
        self.interface = interface
        self.output = output

        self.target_dir = directory / interface / output
        self.cmd_lib = cmd_lib

    @staticmethod
    def delete(path: Path):
        """Delete all files in a directory."""
        for file in path.glob("*"):
            if file.is_dir():
                Editor.delete(file)
            else:
                file.unlink()

    @staticmethod
    def write(path: Path, content: str):
        with open(path, "w", encoding="utf-8", newline="\n") as f:  # type: ignore
            f.write(content)

    def generate_sidebar(self):
        """Write the group of index.mdx and _category_.json to create a sidebar."""

        def get_card(title: str, description: str, url: str, command: bool):
            return f"""
<ReferenceCard
    title="{title}"
    description="{description}"
    url="{url}"
    command="{str(command).lower()}"
/>"""

        def get_index(path: Path, label: str) -> str:
            md_files = [sub for sub in path.glob("*md")]

            content = f"# {label}\n\n"
            content += "import ReferenceCard from '@site/src/components/General/NewReferenceCard';\n\n"
            content += "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>"
            for md in md_files:
                ref = md.parts.index("reference")
                url = "/".join([*md.parts[ref:-1], md.stem])
                content += get_card(
                    title=md.stem,
                    description=self.cmd_lib.get_cmd_info(md.stem).get(
                        "description", ""
                    ),
                    url=url,
                    command=True,
                )
            content += "\n</ul>\n"
            return content

        def write_mdx_and_category(path: Path, label: str, position: int):
            Editor.write(path=path / "index.mdx", content=get_index(path, label))
            Editor.write(
                path=path / "_category_.json",
                content=json.dumps({"label": label, "position": position}, indent=2),
            )

        def recursive(path: Path):
            position = 1
            for p in path.iterdir():
                if p.is_dir():
                    write_mdx_and_category(p, p.name.title(), position)
                    recursive(p)
                    position += 1

        write_mdx_and_category(self.target_dir, "Reference", 5)
        recursive(self.target_dir)

    def generate_md(self, path: Path, cmd_info: dict):
        def get_header() -> str:
            title = cmd_info["name"]

            header = "---\n"
            header += f"title: {title}\n"
            header += "description: test\n"
            header += "keywords: \n"
            header += "- abc\n"
            header += "- def\n"
            header += "---\n\n"
            return header

        def get_tab() -> str:
            tab = "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
            tab += "import Tabs from '@theme/Tabs';\n"
            tab += "import TabItem from '@theme/TabItem';\n\n"
            return tab

        def get_description() -> str:
            return ""

        def get_signature() -> str:
            return ""

        def get_parameters() -> str:
            return ""

        def get_returns() -> str:
            return ""

        def get_data() -> str:
            return ""

        content = get_header()
        content += get_tab()
        content += get_description()
        content += get_signature()
        content += get_parameters()
        content += get_returns()
        content += get_data()
        self.write(path, content)

    def generate(self):
        """Generate the website reference."""

        self.delete(self.target_dir)

        for cmd in self.cmd_lib.get_cmd_list():
            func = self.cmd_lib.get_cmd_func(cmd)
            func_name = func.__name__ if func else None
            if not func_name:
                continue
            func_name = "index_cmd" if func_name == "index" else func_name

            folder = "/".join(cmd.strip("/").split("/")[:-1])
            path = self.target_dir / folder / f"{func_name}.md"

            cmd_info = self.cmd_lib.get_cmd_info(cmd)
            cmd_info["name"] = func_name

            if self.output == "data_models":
                pass
            elif self.output == "reference":
                path.parent.mkdir(parents=True, exist_ok=True)
                self.generate_md(path, cmd_info)

        self.generate_sidebar()
        print(f"Markdown files generated, check the {self.target_dir} folder.")


if __name__ == "__main__":
    editor = Editor(
        directory=CONTENT_PATH,
        interface="excel",
        output="reference",
        cmd_lib=CommandLib(),
    )
    editor.generate()
