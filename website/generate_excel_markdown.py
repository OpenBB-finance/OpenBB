import json
import shutil
import sys
from pathlib import Path
from textwrap import shorten
from typing import Any, Dict, List, Literal

import requests

# Paths
WEBSITE_PATH = Path(__file__).parent.absolute()
CONTENT_PATH = WEBSITE_PATH / "content"
XL_FUNCS_PATH = CONTENT_PATH / "excel" / "functions.json"
XL_PLATFORM_PATH = CONTENT_PATH / "excel" / "openapi.json"
SEO_METADATA_PATH = WEBSITE_PATH / "metadata" / "platform_v4_seo_metadata.json"

# URLs: the platorm url should match the backend being used by excel.openbb.co
XL_FUNCS_URL = "https://excel.openbb.co/assets/functions.json"
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

    # These examples will be generated in the core, but we keep them here meanwhile
    EXAMPLE_PARAMS: Dict[str, Dict] = {
        "/byod": {
            "widget": '"widget_name"',
        },
        "crypto": {
            "symbol": '"BTCUSD"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "query": '"coin"',
        },
        "currency": {
            "symbol": '"EURUSD"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
        },
        "derivatives": {
            "symbol": '"AAPL"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
        },
        "economy": {
            "countries": '"united_states"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "units": '"growth_previous"',
            "frequency": '"quarterly"',
            "harmonized": "TRUE",
            "query": '"gdp"',
            "symbol": '"GFDGDPA188S"',
            "limit": 5,
            "period": '"quarter"',
            "type": '"real"',
            "adjusted": "TRUE",
        },
        "equity": {
            "symbol": '"AAPL"',
            "tag": '"ebitda"',
            "query": '"ebitda"',
            "year": 2022,
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "limit": 5,
            "form_type": '"10-K"',
            "period": '"annual"',
            "frequency": '"quarterly"',
            "type": "",
            "sort": '"desc"',
            "structure": '"flat"',
            "date": '"2023-05-07"',
            "page": 1,
            "interval": '"1d"',
            "is_symbol": "FALSE",
        },
        "/equity/fundamental/reported_financials": {
            "symbol": '"AAPL"',
            "period": '"annual"',
            "statement_type": '"balance"',
            "limit": 5,
        },
        "etf": {
            "symbol": '"SPY"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "query": '"global"',
        },
        "fixedincome": {
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "maturity": '"90d"',
            "category": '"nonfinancial"',
            "grade": '"aa"',
            "date": '"2023-05-07"',
            "yield_curve": '"spot"',
            "index_type": '"yield"',
            "inflation_adjusted": "TRUE",
            "interest_rate_type": '"deposit"',
        },
        "index": {
            "symbol": '"^GSPC"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "index": '"sp500"',
        },
        "news": {
            "symbol": '"AAPL"',
            "symbols": '"AAPL,MSFT"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "limit": 5,
        },
        "regulators": {
            "symbol": '"AAPL"',
            "start_date": '"2023-01-01"',
            "end_date": '"2023-12-31"',
            "query": '"AAPL"',
        },
    }

    def __init__(self):
        self.xl_funcs = self.read_xl_funcs()
        self.openapi = self.read_openapi()
        self.seo_metadata = self.read_seo_metadata()

    @staticmethod
    def fetch_xl_funcs():
        """Fetch the excel functions."""
        r = requests.get(XL_FUNCS_URL, timeout=10)
        with open(XL_FUNCS_PATH, "w") as f:
            json.dump(r.json(), f, indent=2)

    @staticmethod
    def fetch_openapi():
        """Fetch the openapi.json."""
        r = requests.get(XL_PLATFORM_URL, timeout=10)
        with open(XL_PLATFORM_PATH, "w") as f:
            json.dump(r.json(), f, indent=2)

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
        model = (
            self.openapi.get("paths", {})
            .get(f"/api/v1{cmd}", {})
            .get("get", {})
            .get("model")
        )
        if model:
            schema = self.openapi["components"]["schemas"][model]["properties"]
            data = {}
            for name, info in schema.items():
                data[name] = {
                    "description": info.get("description", "").replace("\n", " "),
                }
            return data
        return {}

    def _get_examples(
        self, cmd: str, signature_: str, parameters: dict, sep: str = ","
    ) -> dict:
        """Get the examples of the command."""
        sig = signature_.split("(")[0] + "("
        category = signature_.split(".")[1].lower()

        def get_p_value(cmd, p_name) -> str:
            if cmd in self.EXAMPLE_PARAMS:
                return self.EXAMPLE_PARAMS[cmd].get(p_name, "")
            return self.EXAMPLE_PARAMS.get(category, {}).get(p_name, "")

        required_eg = sig
        for p_name, p_info in parameters.items():
            if p_info["required"]:
                p_value = get_p_value(cmd, p_name)
                required_eg += f"{p_value}{sep}"
        required_eg = required_eg.strip(f"{sep} ") + ")"

        standard_eg = sig
        for p_name, p_info in parameters.items():
            if p_name == "provider":
                break
            p_value = get_p_value(cmd, p_name)
            standard_eg += f"{p_value}{sep}"
        standard_eg = standard_eg.strip(f"{sep} ") + ")"

        if required_eg == standard_eg:
            return {"A. Required": required_eg}
        # Uncomment to add standard examples
        # return {"A. Required": required_eg, "B. Standard": standard_eg}
        return {"A. Required": required_eg}

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
        examples = self._get_examples(cmd, signature_, parameters)
        return {
            "name": name,
            "description": description,
            "function": function,
            "signature": signature_,
            "parameters": parameters,
            "data": data,
            "return": return_,
            "examples": examples,
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
                syntax += f"```{self.interface} wordwrap\n"
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

        def get_return_data() -> str:
            if data_schema := cmd_info["data"]:
                data = "## Return Data\n\n"
                data += "| Name | Description |\n"
                data += "| ---- | ----------- |\n"
                for field_name, field_info in data_schema.items():
                    name = field_name
                    description = field_info["description"]
                    data += f"| {name} | {description} |\n"
                return data
            return ""

        def get_examples() -> str:
            if cmd_examples := cmd_info["examples"]:
                examples = "### Example\n\n"
                for _, v in cmd_examples.items():
                    # examples += f"### {k}\n\n"
                    examples += f"```{self.interface} wordwrap\n"
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
                files = list(path.glob("*"))
                # Put the cmds_folder folder at the end
                index = next(
                    (
                        i
                        for i, path in enumerate(files)
                        if path.stem == self.main_folder
                    ),
                    None,
                )
                if index is not None:
                    cmd_folder = files.pop(index)
                    files.append(cmd_folder)
                content += get_cards(folder=folder, files=files, command=False)
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
            for p in path.iterdir():
                if p.is_dir():
                    write_mdx_and_category(p, p.name, position)
                    recursive(p)
                    position += 1

        write_mdx_and_category(self.target_dir, self.main_folder, 5)
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
        CommandLib.fetch_openapi()

    Editor(
        directory=CONTENT_PATH,
        interface="excel",
        main_folder="reference",
        cmd_lib=CommandLib(),
    ).go()
