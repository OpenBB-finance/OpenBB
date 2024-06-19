import json
import shutil
import sys
from functools import reduce
from pathlib import Path
from textwrap import shorten
from typing import Any, Dict, List, Literal, Optional

import requests

# Paths
WEBSITE_PATH = Path(__file__).parent.absolute()
CONTENT_PATH = WEBSITE_PATH / "content"
XL_FUNCS_PATH = CONTENT_PATH / "excel" / "functions.json"
XL_OPENBB_FUNCS_PATH = CONTENT_PATH / "excel" / "openbb-functions.json"
XL_PLATFORM_PATH = CONTENT_PATH / "excel" / "openapi.json"
SEO_METADATA_PATH = WEBSITE_PATH / "metadata" / "platform_v4_seo_metadata.json"

# URLs: the platform url should match the backend being used by excel.openbb.co
XL_FUNCS_URL = "https://excel.openbb.co/assets/functions.json"
XL_OPENBB_FUNCS_URL = "https://excel.openbb.co/assets/openbb-functions.json"
XL_PLATFORM_URL = "https://sdk.openbb.co/openapi.json"


class CommandLib:
    """Command library."""

    XL_TYPE_MAP = {
        "bool": "Boolean",
        "float": "Number",
        "int": "Number",
        "integer": "Number",
        "str": "Text",
        "string": "Text",
    }
    API_PREFIX = "/api/v1"

    EXAMPLES: Dict[str, Dict] = {
        "/get": {
            "Example 0": '=OBB.GET({"a","b","c";"d","e","f"})',
            "Example 1": '=OBB.GET({"a","b","c";"d","e","f"},"d","c")',
        },
        "/byod": {
            "Example 0": '=OBB.BYOD("widget_name")',
            "Example 1": '=OBB.BYOD("widget_name","backend_name")',
        },
    }

    def __init__(self):
        self.xl_funcs = self.read_xl_funcs()
        self.xl_openbb_funcs = self.read_xl_openbb_funcs()
        self.openapi = self.read_openapi()
        self.seo_metadata = self.read_seo_metadata()

    @staticmethod
    def fetch_xl_funcs():
        """Fetch the excel functions."""
        r = requests.get(XL_FUNCS_URL, timeout=10)
        with open(XL_FUNCS_PATH, "w") as f:
            json.dump(r.json(), f, indent=2)

    @staticmethod
    def fetch_xl_openbb_funcs():
        """Fetch the openbb version of excel functions."""
        r = requests.get(XL_OPENBB_FUNCS_URL, timeout=10)
        with open(XL_OPENBB_FUNCS_PATH, "w") as f:
            json.dump(r.json(), f, indent=2)

    @staticmethod
    def fetch_openapi():
        """Fetch the openapi.json."""
        r = requests.get(XL_PLATFORM_URL, timeout=10)
        with open(XL_PLATFORM_PATH, "w") as f:
            json.dump(r.json(), f, indent=2)

    @staticmethod
    def _traverse(
        parts: List[str], map_: dict, exclude: Optional[List[str]] = None
    ) -> dict:
        """Traverse the map."""
        parts = [p for p in parts if p not in (exclude or [])]
        try:
            return reduce(lambda x, y: x[y], parts, map_)
        except KeyError:
            return {}

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

    def read_xl_openbb_funcs(self) -> Dict[str, Any]:
        """Read the Excel openbb functions file."""
        with open(XL_OPENBB_FUNCS_PATH) as f:
            funcs = json.load(f)
        return funcs

    def read_openapi(self) -> dict:
        """Get the openapi.json."""
        with open(XL_PLATFORM_PATH) as f:
            return json.load(f)

    def to_xl(self, type_: str) -> str:
        """Convert a type to an Excel type."""
        return self.XL_TYPE_MAP.get(type_, type_).title()

    def get_func(self, cmd: str) -> str:
        """Get the func of the command."""
        return self.xl_funcs.get(cmd, {}).get("name", ".").split(".")[-1].lower()

    def _get_signature(self, cmd: str, parameters: dict, sep: str = ",") -> str:
        """Get the signature of the command."""
        sig = "=OBB." + self.xl_funcs[cmd].get("name", "")
        sig += "("
        for p_name, p_info in parameters.items():
            if p_info["required"]:
                sig += f"{p_name}"
            else:
                sig += f"[{p_name}]"
            sig += sep
        sig = sig.strip(f"{sep} ") + ")"
        return sig

    def _get_parameters(self, cmd: str) -> dict:
        """Get the parameters of the command."""
        parameters = {}
        for p in self.xl_funcs[cmd]["parameters"]:
            parameters[p["name"]] = {
                "type": self.to_xl(str(p["type"])),
                "description": p["description"].replace("\n", " "),
                "required": not p.get("optional", False),
            }

        return parameters

    def _get_data(self, cmd: str) -> dict:
        """Get the data of the command from the openapi."""
        schema = self._traverse(
            [
                "paths",
                self.API_PREFIX + cmd,
                "get",
                "responses",
                "200",
                "content",
                "application/json",
                "schema",
            ],
            self.openapi,
        )
        if "$ref" in schema and (
            inner_schema := self._traverse(
                schema["$ref"].split("/"), self.openapi, ["#"]
            )
        ):
            models = self._traverse(["properties", "results", "anyOf"], inner_schema)[0]
            models = (
                models["items"].get("oneOf", [models["items"]])
                if models.get("type") == "array"
                else [models]
            )

            # Get the available providers from the provider parameter enum
            parameters = self._traverse(
                [
                    "paths",
                    self.API_PREFIX + cmd,
                    "get",
                    "parameters",
                ],
                self.openapi,
            )
            providers = []
            for p in parameters:
                if p.get("name") == "provider":
                    providers = p.get("schema", {}).get("enum", [])
            if providers:
                d = {}
                for i, model in enumerate(models):
                    ref = model.get("$ref", "")
                    model_schema = self._traverse(ref.split("/"), self.openapi, ["#"])
                    provider = providers[i]
                    d[provider] = {
                        name: {
                            "description": info.get("description", "").replace("\n", "")
                        }
                        for name, info in model_schema["properties"].items()
                    }
                return d
        return {}

    def _get_examples(
        self, cmd: str, sig_parameters: Dict, sep: str = ","
    ) -> Dict[str, str]:
        """Get the examples of the command."""
        if cmd in ("/get", "/byod"):
            return self.EXAMPLES[cmd]

        # API examples
        examples = self._traverse(
            ["paths", self.API_PREFIX + cmd, "get", "examples"], self.openapi
        )
        sig = "=OBB." + self.xl_funcs[cmd].get("name", "")
        ex_reference: Dict[str, str] = {}
        for i, ex in enumerate(examples):
            ex_code = ""
            if ex.get("scope") == "api":
                ex_code += sig + "("
                ex_parameters = ex.get("parameters", {})
                for p_name, p_info in sig_parameters.items():
                    p_type = p_info.get("type", {})
                    if p_value := ex_parameters.get(p_name):
                        if p_type == "Text":
                            ex_code += f'"{p_value}"{sep}'
                        elif p_type == "Boolean":
                            p_type = "TRUE" if bool(p_value) else "FALSE"
                            ex_code += f"{p_type}{sep}"
                        else:
                            ex_code += f"{p_value}{sep}"
                    else:
                        ex_code += sep
                ex_code = ex_code.strip(sep)
                ex_code += ")"
            # Some example are repeated, we only want to add them once
            if ex_code not in ex_reference.values():
                ex_reference[f"Example {i}"] = ex_code
        return ex_reference

    def get_info(self, cmd: str) -> Dict[str, Any]:
        """Get the info for a command."""
        name = self.get_func(cmd)
        if not name:
            return {}
        description = self.xl_funcs[cmd].get("description", "").replace("\n", " ")
        parameters = self._get_parameters(cmd)
        function = self.xl_funcs[cmd].get("name", "")
        signature_ = self._get_signature(cmd, parameters)
        data = self._get_data(cmd)
        return_ = self.xl_funcs[cmd].get("result", {}).get("dimensionality", "")
        examples = self._get_examples(cmd, parameters)
        providers = self.xl_openbb_funcs.get(function, {}).get("providers", [])
        return {
            "name": name,
            "description": description,
            "function": function,
            "signature": signature_,
            "parameters": parameters,
            "data": data,
            "return": return_,
            "examples": examples,
            "providers": providers,
        }


class Editor:
    """Editor for the website docs."""

    def __init__(
        self,
        directory: Path,
        interface: Literal["excel"],
        main_folder: str,
        cmd_lib: CommandLib,
    ) -> None:
        """Initialize the editor."""
        self.directory = directory
        self.interface = interface
        self.main_folder = main_folder

        self.target_dir = directory / interface / main_folder
        self.cmd_lib = cmd_lib

    @staticmethod
    def write(path: Path, content: str):
        with open(path, "w", encoding="utf-8", newline="\n") as f:  # type: ignore
            f.write(content)

    def generate_md(self, path: Path, cmd: str, cmd_info: dict):
        def get_header() -> str:
            header = ""
            metadata = self.cmd_lib.seo_metadata.get(cmd, {})
            if metadata:
                title = metadata["title"].upper()
                description = metadata["description"]
                keywords = metadata["keywords"]
                header = "---\n"
                header += f"title: {title}\n"
                header += f"description: {description}\n"
                header += "keywords: \n"
                for kw in keywords:
                    header += f"- {kw}\n"
                header += "---\n\n"
            else:
                title = cmd_info["name"].upper()
                header = "---\n"
                header += f"title: {title}\n"
                header += "---\n\n"
            return header

        def get_head_title() -> str:
            func = cmd_info["function"]
            title = "<!-- markdownlint-disable MD033 -->\n"
            title += "import HeadTitle from '@site/src/components/General/HeadTitle.tsx';\n\n"
            title += f'<HeadTitle title="{func} | OpenBB Add-in for Excel Docs" />\n\n'
            return title

        def get_description() -> str:
            description = cmd_info.get("description", "")
            description += "\n\n"
            return description

        def get_syntax() -> str:
            if sig := cmd_info["signature"]:
                syntax = "## Syntax\n\n"
                syntax += f"```{self.interface}\n"
                syntax += f"{sig}\n"
                syntax += "```\n\n"
                return syntax
            return ""

        def get_parameters() -> str:
            if parameter_schema := cmd_info["parameters"]:
                parameters = "## Parameters\n\n"
                parameters += "| Name | Type | Description | Required |\n"
                parameters += "| ---- | ---- | ----------- | -------- |\n"
                for field_name, field_info in parameter_schema.items():
                    name = field_name
                    type_ = field_info["type"]
                    description = field_info["description"]
                    required = field_info["required"]
                    required_str = str(required).title()
                    if required:
                        parameters += f"| **{name}** | **{type_}** | **{description}** | **{required_str}** |\n"
                    else:
                        parameters += (
                            f"| {name} | {type_} | {description} | {required_str} |\n"
                        )
                parameters += "\n"
                return parameters
            return ""

        def get_data() -> str:
            if data_schema := cmd_info["data"]:
                providers = cmd_info["providers"]
                filtered_data_schema = {
                    k: v for k, v in data_schema.items() if k in providers
                }
                if filtered_data_schema:
                    data = "import Tabs from '@theme/Tabs';\n"
                    data += "import TabItem from '@theme/TabItem';\n\n"
                    data += "## Data\n\n"
                    data += "<Tabs>\n"
                    for provider, fields in filtered_data_schema.items():
                        data += f"<TabItem value='{provider}'>\n\n"
                        data += "| Name | Description |\n"
                        data += "| ---- | ----------- |\n"
                        for name, info in fields.items():
                            description = info["description"]
                            data += f"| {name} | {description} |\n"
                        data += "</TabItem>\n"
                    data += "</Tabs>\n"
                    return data
            return ""

        def get_examples() -> str:
            if cmd_examples := cmd_info["examples"]:
                examples = "## Examples\n\n"
                for _, v in cmd_examples.items():
                    # examples += f"### {k}\n\n"
                    examples += f"```{self.interface}\n"
                    examples += f"{v}\n"
                    examples += "```\n\n"

                return examples
            return ""

        content = get_header()
        content += get_head_title()
        content += get_description()
        content += get_syntax()
        content += get_examples()
        content += "---\n\n"
        content += get_parameters()
        content += "---\n\n"
        content += get_data()
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
                    title = t.upper() if t != self.main_folder else t.title()
                    if command:
                        p = (
                            self.main_folder
                            if self.main_folder in file.parts
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

            cmd_path = filter_path(
                path.parts.index(self.main_folder) + 1, path
            ).replace("/", ".")
            head_title = (
                cmd_path.title() if cmd_path == self.main_folder else cmd_path.upper()
            )

            content = f"# {head_title}\n\n"
            content += CARD

            ### Main folder
            if folder == self.main_folder:
                # sort the folders first and then files to push byod,get to the bottom
                files = sorted(
                    list(path.glob("*")),
                    key=lambda path: ((0, path) if path.is_dir() else (1, path)),
                )
                content += get_cards(
                    folder=folder,
                    files=files,
                    command=False,
                )
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
            return text.upper()

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
            for p in sorted(path.iterdir()):
                if p.is_dir():
                    write_mdx_and_category(p, p.name, position)
                    recursive(p)
                    position += 1

        write_mdx_and_category(self.target_dir, self.main_folder, 6)
        recursive(self.target_dir)

    def dump(self, reference_map: Dict) -> None:
        """Dump the reference structured information to json."""
        with open(self.target_dir / "reference_map.json", "w") as f:
            json.dump(reference_map, f, indent=2)

    def go(self):
        """Generate the website reference."""

        reference_map = {}

        shutil.rmtree(self.target_dir, ignore_errors=True)

        # We start from xl_funcs to make sure only the commands in the add-in are included
        for cmd in self.cmd_lib.xl_funcs:
            if self.cmd_lib.get_func(cmd):
                folder = "/".join(cmd.split("/")[1:-1])
                filename = cmd.split("/")[-1] + ".md"
                filepath = self.target_dir / folder / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                cmd_info = self.cmd_lib.get_info(cmd)
                reference_map[cmd] = cmd_info
                self.generate_md(filepath, cmd, cmd_info)

        self.generate_sidebar()
        self.dump(reference_map)
        print(f"Markdown files generated, check the {self.target_dir} folder.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--no-update":
        pass
    else:
        CommandLib.fetch_xl_funcs()
        CommandLib.fetch_xl_openbb_funcs()
        CommandLib.fetch_openapi()

    Editor(
        directory=CONTENT_PATH,
        interface="excel",
        main_folder="reference",
        cmd_lib=CommandLib(),
    ).go()
