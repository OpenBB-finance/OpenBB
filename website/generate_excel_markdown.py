import json
import sys
from pathlib import Path
from textwrap import shorten
from typing import Any, Dict, List, Literal

import requests
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.static.package_builder import PathHandler

# Paths
WEBSITE_PATH = Path(__file__).parent.absolute()
CONTENT_PATH = WEBSITE_PATH / "content"
XL_FUNCS_PATH = CONTENT_PATH / "excel" / "functions.json"
SEO_METADATA_PATH = WEBSITE_PATH / "metadata" / "platform_v4_seo_metadata.json"

XL_FUNCS_URL = "https://openbb-excel-add-in.vercel.app/assets/functions.json"


class CommandLib(PathHandler):
    """Command library."""

    MANUAL_MAP = {
        "/last": "/equity/fundamental/latest_attributes",
        "/hist": "/equity/fundamental/historical_attributes",
    }
    XL_TYPE_MAP = {
        "bool": "Boolean",
        "float": "Number",
        "int": "Number",
        "integer": "Number",
        "str": "Text",
        "string": "Text",
    }

    def __init__(self):
        self.pi = ProviderInterface()
        self.route_map = self.build_route_map()
        self.xl_funcs = self.read_xl_funcs()
        self.seo_metadata = self.read_seo_metadata()

        self.update()

    @staticmethod
    def fetch():
        """Fetch the excel functions."""
        r = requests.get(XL_FUNCS_URL, timeout=10)
        with open(XL_FUNCS_PATH, "w") as f:
            json.dump(r.json(), f, indent=2)

    def update(self):
        """Update with manual map."""
        for key, value in self.MANUAL_MAP.items():
            self.route_map[key] = self.route_map[value]

    def read_seo_metadata(self) -> dict:
        """Get the SEO metadata."""
        with open(SEO_METADATA_PATH) as f:
            metadata = json.load(f)
        return {"/" + k.replace(".", "/").lower(): v for k, v in metadata.items()}

    def read_xl_funcs(self) -> Dict[str, dict]:
        """Get a list of all the commands in the docs."""
        with open(XL_FUNCS_PATH) as f:
            funcs = json.load(f)
        return {
            "/" + func["name"].replace(".", "/").lower(): func
            for func in funcs["functions"]
        }

    def to_xl(self, type_: str) -> str:
        """Convert a type to an Excel type."""
        return self.XL_TYPE_MAP.get(type_, type_).title()

    def get_func(self, cmd: str) -> str:
        """Get the func of the command."""
        if cmd in self.route_map:
            return self.xl_funcs.get(cmd, {}).get("name", ".").split(".")[-1].lower()
        return ""

    def get_model(self, cmd: str) -> str:
        """Get the model of the command."""
        route = self.route_map.get(cmd, None)
        if route:
            return route.openapi_extra.get("model", "")
        return ""

    def get_xl_param(self, cmd, param):
        for p in self.xl_funcs[cmd]["parameters"]:
            if p["name"] == param:
                return p
        return None

    def get_parameters(self, cmd: str) -> dict:
        """Get the parameters of the command."""
        parameters = {}
        cmd_info = self.xl_funcs[cmd]
        for p in cmd_info["parameters"]:
            parameters[p["name"]] = {
                "type": self.to_xl(str(p["type"])),
                "description": p["description"].replace("\n", " "),
                "optional": str(p.get("optional", False)).title(),
            }

        return parameters

    def get_data(self, cmd: str) -> dict:
        """Get the data of the command."""
        model_name = self.get_model(cmd)
        if model_name:
            schema = self.pi.return_schema[model_name].model_json_schema()["properties"]
            data = {}
            for name, info in schema.items():
                data[name] = {
                    "description": info.get("description", ""),
                }
            return data

        return {}

    def get_info(self, cmd: str) -> Dict[str, Any]:
        """Get the info for a command."""
        name = self.get_func(cmd)
        if not name:
            return {}
        description = self.xl_funcs[cmd].get("description", "").replace("\n", " ")
        signature_ = (
            "=OBB." + self.xl_funcs[cmd].get("name", "") + "(required;[optional])"
        )
        return_ = self.xl_funcs[cmd].get("result", {}).get("dimensionality", "")
        if model_name := self.get_model(cmd):
            return {
                "name": name,
                "description": description,
                "signature": signature_,
                "return": return_,
                "model_name": model_name,
            }
        return {}


class Editor:
    """Editor for the website docs."""

    def __init__(
        self,
        directory: Path,
        interface: Literal["excel"],
        main_folder: str,
        cmds_folder: str,
        cmd_lib: CommandLib,
    ) -> None:
        """Initialize the editor."""
        self.directory = directory
        self.interface = interface
        self.main_folder = main_folder
        self.cmds_folder = cmds_folder

        self.target_dir = directory / interface / main_folder
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

    def generate_md(self, path: Path, cmd: str):
        cmd_info = self.cmd_lib.get_info(cmd)

        def get_header() -> str:
            header = ""
            metadata = self.cmd_lib.seo_metadata.get(cmd, {})
            if metadata:
                title = metadata["title"]
                description = metadata["description"]
                keywords = metadata["keywords"]
                header = "---\n"
                header += f"title: {title}\n"
                header += f"description: {description}\n"
                header += "keywords: \n"
                for kw in keywords:
                    header += f"- {kw}\n"
                header += "---\n\n"
            return header

        def get_tab() -> str:
            tab = "<!-- markdownlint-disable MD041 -->\n\n"
            # tab += "import Tabs from '@theme/Tabs';\n"
            # tab += "import TabItem from '@theme/TabItem';\n\n"
            return tab

        def get_description() -> str:
            description = cmd_info.get("description", "")
            description += "\n\n"
            return description

        def get_sintax() -> str:
            sig = cmd_info["signature"]
            syntax = "## Syntax\n\n"
            syntax += f"```{self.interface} wordwrap\n"
            syntax += f"{sig}\n"
            syntax += "```\n\n"
            return syntax

        def get_parameters() -> str:
            parameters = "## Parameters\n\n"
            parameters += "| Name | Type | Description | Optional |\n"
            parameters += "| ---- | ---- | ----------- | -------- |\n"
            for field_name, field_info in self.cmd_lib.get_parameters(cmd).items():
                name = field_name
                type_ = field_info["type"]
                description = field_info["description"]
                optional = field_info["optional"]
                parameters += f"| {name} | {type_} | {description} | {optional} |\n"
            parameters += "\n"
            return parameters

        # def get_return_type() -> str:
        #     ret = cmd_info["return"]
        #     return_ = "## Return Type\n\n"
        #     return_ += f"* {ret}\n\n"
        #     return return_

        def get_return_data() -> str:
            data = "## Return Data\n\n"
            data += "| Name | Description |\n"
            data += "| ---- | ----------- |\n"
            for field_name, field_info in self.cmd_lib.get_data(cmd).items():
                name = field_name
                description = field_info["description"]
                data += f"| {name} | {description} |\n"
            return data

        content = get_header()
        content += get_tab()
        content += get_description()
        content += get_sintax()
        content += "---\n\n"
        content += get_parameters()
        content += "---\n\n"
        # content += get_return_type()
        # content += "---\n\n"
        content += get_return_data()
        Editor.write(path, content)

    def generate_sidebar(self):
        """Write the group of index.mdx and _category_.json to create a sidebar."""

        CARD = "import ReferenceCard from '@site/src/components/General/NewReferenceCard';\n\n"
        OPEN_UL = "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>\n"
        CLOSE_UL = "\n</ul>\n\n"

        def get_card(title: str, description: str, url: str, command: bool):
            """Generate a card."""
            description = shorten(description, width=100, placeholder="...")
            card = "<ReferenceCard\n"
            card += f'    title="{title}"\n'
            card += f'    description="{description}"\n'
            card += f'    url="{url}"\n'
            if command:
                card += "    command\n"
            card += "/>"
            return card

        def filter_path(ref: int, md: Path) -> str:
            return "/".join([*md.parts[ref:-1], md.stem])

        def get_cards(
            folder: str,
            files: List[Path],
            command: bool,
            section: str = "",
        ) -> str:
            """Generate the cards for a section."""

            if files:
                content = section
                content += OPEN_UL
                for file in files:
                    t = file.stem
                    title = t if t != self.cmds_folder else t.title()
                    if command:
                        p = (
                            self.cmds_folder
                            if self.cmds_folder in file.parts
                            else folder
                        )
                        cmd = "/" + filter_path(file.parts.index(p) + 1, file)
                        description = (
                            self.cmd_lib.get_info(cmd)
                            .get("description", "")
                            .replace("\n", " ")
                        )
                    else:
                        description = ", ".join([s.stem for s in file.rglob("*")])
                    content += get_card(
                        title=title,
                        description=description,
                        url=filter_path(file.parts.index(folder), file),
                        command=command,
                    )
                content += CLOSE_UL
                return content
            return ""

        def get_index(path: Path, folder: str) -> str:
            """Generate the index.mdx file."""

            content = f"# {folder}\n\n"
            content += CARD

            ### Main folder
            if folder == self.main_folder:
                files = list(path.glob("*"))
                # Put the cmds_folder folder at the end
                index = next(
                    (
                        i
                        for i, path in enumerate(files)
                        if path.stem == self.cmds_folder
                    ),
                    None,
                )
                if index is not None:
                    cmd_folder = files.pop(index)
                    files.append(cmd_folder)
                content += get_cards(folder=folder, files=files, command=True)
                return content

            ### Menus
            content += get_cards(
                folder=folder,
                files=[f for f in path.glob("*") if f.is_dir()],
                command=False,
                section="### Menus\n",
            )

            ### Commands
            content += get_cards(
                folder=folder,
                files=list(path.glob("*md")),
                command=True,
                section="### Commands\n",
            )
            return content

        def format_label(text: str):
            if text == self.main_folder:
                return self.main_folder.title()
            if text == self.cmds_folder:
                return self.cmds_folder.title()
            return text.lower()

        def write_mdx_and_category(path: Path, folder: str, position: int):
            Editor.write(path=path / "index.mdx", content=get_index(path, folder))
            Editor.write(
                path=path / "_category_.json",
                content=json.dumps(
                    {"label": format_label(folder), "position": position}, indent=2
                ),
            )

        def recursive(path: Path):
            position = 1
            for p in path.iterdir():
                if p.is_dir():
                    write_mdx_and_category(p, p.name, position)
                    recursive(p)
                    position += 1

        write_mdx_and_category(self.target_dir, self.main_folder, 5)
        recursive(self.target_dir)

    def go(self):
        """Generate the website reference."""

        self.delete(self.target_dir)
        for cmd in self.cmd_lib.xl_funcs:
            if self.cmd_lib.get_func(cmd):
                folder = "/".join(cmd.split("/")[1:-1])
                if folder:
                    folder = self.cmds_folder + "/" + folder
                filename = cmd.split("/")[-1] + ".md"
                filepath = self.target_dir / folder / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                self.generate_md(filepath, cmd)

        self.generate_sidebar()
        print(f"Markdown files generated, check the {self.target_dir} folder.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        CommandLib.fetch()
    Editor(
        directory=CONTENT_PATH,
        interface="excel",
        main_folder="reference",
        cmds_folder="library",
        cmd_lib=CommandLib(),
    ).go()
