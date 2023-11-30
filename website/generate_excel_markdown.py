import json
from pathlib import Path
from typing import Literal

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.static.package_builder import PathHandler

# Paths
WEBSITE_PATH = Path(__file__).parent.absolute()
CONTENT_PATH = WEBSITE_PATH / "content"
XL_FUNCS_PATH = CONTENT_PATH / "excel" / "functions.json"
SEO_METADATA = WEBSITE_PATH / "metadata" / "platform_v4_seo_metadata.json"


class CommandLib(PathHandler):
    """Command library."""

    MANUAL_MAP = {
        "/last": "/equity/fundamental/latest_attributes",
        "/hist": "/equity/fundamental/historical_attributes",
    }

    def __init__(self):
        self.pi = ProviderInterface()
        self.route_map = self.build_route_map()
        self.xl_funcs = self.read_xl_funcs()
        self.seo_metadata = self.read_seo_metadata()

        self.update()

    def update(self):
        """Update with manual map."""
        for key, value in self.MANUAL_MAP.items():
            self.route_map[key] = self.route_map[value]

    def read_seo_metadata(self) -> dict:
        """Get the SEO metadata."""
        with open(SEO_METADATA) as f:
            metadata = json.load(f)
        return {"/" + k.replace(".", "/").lower(): v for k, v in metadata.items()}

    def read_xl_funcs(self) -> dict:
        """Get a list of all the commands in the docs."""
        with open(XL_FUNCS_PATH) as f:
            funcs = json.load(f)
        return {
            "/" + func["name"].replace(".", "/").lower(): func
            for func in funcs["functions"]
        }

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
                "type": p["type"],
                "description": p["description"].replace("\n", " "),
                "optional": str(p.get("optional", False)).lower(),
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

    def get_info(self, cmd: str) -> dict:
        """Get the info for a command."""
        name = self.get_func(cmd)
        if not name:
            return {}
        description = self.xl_funcs[cmd].get("description", "").replace("\n", " ")
        signature_ = "=OBB." + self.xl_funcs[cmd].get("name", "")
        signature_ += "(required, [optional])"
        if model_name := self.get_model(cmd):
            return {
                "name": name,
                "description": description,
                "signature": signature_,
                "model_name": model_name,
            }
        return {}


class Editor:
    """Editor for the website docs."""

    def __init__(
        self,
        directory: Path,
        interface: Literal["excel"],
        output: Literal["reference"],
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

        def get_signature() -> str:
            func_def = cmd_info["signature"]
            signature_ = f"```{self.interface} wordwrap\n"
            signature_ += f"{func_def}\n"
            signature_ += "```\n\n"
            signature_ += "---\n\n"
            return signature_

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

        def get_data() -> str:
            data = "## Data\n\n"
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
        content += get_signature()
        content += get_parameters()
        content += get_data()
        self.write(path, content)

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
            """Generate the index.mdx file."""

            def filter_path(ref: int, md: Path) -> str:
                return "/".join([*md.parts[ref:-1], md.stem])

            md_files = list(path.glob("*md"))

            content = f"# {label}\n\n"
            content += "import ReferenceCard from '@site/src/components/General/NewReferenceCard';\n\n"
            content += "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>"
            for md in md_files:
                url = filter_path(md.parts.index(label.lower()), md)
                cmd = "/" + filter_path(md.parts.index("reference") + 1, md)
                description = (
                    self.cmd_lib.get_info(cmd).get("description", "").replace("\n", " ")
                )
                content += get_card(
                    title=md.stem,
                    description=description,
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

    def generate(self):
        """Generate the website reference."""

        self.delete(self.target_dir)
        for cmd in self.cmd_lib.xl_funcs:
            if self.cmd_lib.get_func(cmd):
                folder = "/".join(cmd.split("/")[1:-1])
                filename = cmd.split("/")[-1] + ".md"
                filepath = self.target_dir / folder / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                self.generate_md(filepath, cmd)

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
