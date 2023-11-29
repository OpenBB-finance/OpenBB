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

    def get_cmd_metadata(self, cmd: str) -> dict:
        """Get the metadata for a command."""
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

    @staticmethod
    def gen_md_section(metadata: dict) -> str:
        return ""

    @staticmethod
    def write_mdx_and_category(target_dir: Path, label: str, position: int):
        Editor.write(path=target_dir / "index.mdx", content="")
        Editor.write(
            path=target_dir / "_category_.json",
            content=json.dumps({"label": label, "position": position}, indent=2),
        )

    def create_header(self, metadata: dict):
        """Generate the markdown for a command."""
        markdown = metadata.get("header", "")

        markdown += "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        markdown += (
            "import Tabs from '@theme/Tabs';\nimport TabItem from '@theme/TabItem';\n\n"
        )

        markdown += self.gen_md_section(metadata)

        return markdown

    def write_md(self, path: Path, metadata: dict):
        markdown = self.create_header(metadata)
        path.write_text("")

    def write_group(self):
        """Write the group of index.mdx and _category_.json"""
        Editor.write_mdx_and_category(self.target_dir, "Reference", 5)

        def recursive(target_dir: Path):
            """Generate category json recursively"""
            position = 1
            for p in target_dir.iterdir():
                if p.is_dir():
                    Editor.write_mdx_and_category(p, p.name.title(), position)
                    recursive(p)
                    position += 1

        recursive(self.target_dir)

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
            filepath = self.target_dir / folder / f"{func_name}.md"

            # metadata = cmd_lib.get_cmd_metadata(cmd)

            if self.output == "data_models":
                pass
            elif self.output == "reference":
                filepath.parent.mkdir(parents=True, exist_ok=True)
                self.write_md(path=filepath, metadata={})
                self.write_group()

            print(f"Markdown files generated, check the {self.target_dir} folder.")


if __name__ == "__main__":
    editor = Editor(
        directory=CONTENT_PATH,
        interface="excel",
        output="reference",
        cmd_lib=CommandLib(),
    )
    editor.generate()
