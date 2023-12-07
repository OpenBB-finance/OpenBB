import inspect
import json
import re
import shutil
from pathlib import Path
from textwrap import shorten
from typing import Any, Dict, List, Literal, TextIO, Union

from docstring_parser import parse

from openbb_terminal.core.sdk.trailmap import Trailmap, get_trailmaps
from openbb_terminal.core.session.current_system import set_system_variable

set_system_variable("TEST_MODE", True)
set_system_variable("LOG_COLLECT", False)
website_path = Path(__file__).parent.absolute()
CONTENT_PATH = website_path / "content/sdk/reference"
SEO_META: Dict[str, Dict[str, Union[str, List[str]]]] = json.loads(
    (website_path / "metadata/sdk_v3_seo_metadata.json").read_text()
)

reference_import = (
    'import ReferenceCard from "@site/src/components/General/NewReferenceCard";\n\n'
)

refrence_ul_element = """<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">"""


def get_function_meta(trailmap: Trailmap, trail_type: Literal["model", "view"]):
    """Gets the function meta data."""
    func_attr = trailmap.func_attrs[trail_type]
    if not func_attr.func_unwrapped:
        return None
    doc_parsed = parse(func_attr.long_doc)  # type: ignore
    line = func_attr.lineon
    path = func_attr.full_path
    func_def = func_attr.func_def
    source_code_url = (
        f"https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/{path}#L{line}"
    )
    function_name = trailmap.view if trail_type == "view" else trailmap.model
    params = []
    for param in doc_parsed.params:
        arg_default = (
            func_attr.params[param.arg_name].default
            if param.arg_name in func_attr.params
            else None
        )
        params.append(
            {
                "name": param.arg_name,
                "doc": param.description if param.description else "",
                "type": param.type_name,
                "default": arg_default
                if arg_default is not inspect.Parameter.empty
                else None,
                "optional": bool(arg_default is not inspect.Parameter.empty)
                or param.is_optional,
            }
        )
    if doc_parsed.returns:
        returns = {
            "doc": doc_parsed.returns.description,
            "type": doc_parsed.returns.type_name,
        }
    else:
        returns = None

    examples = []

    for example in doc_parsed.examples:
        examples.append(
            {
                "snippet": example.snippet,
                "description": example.description.strip(),  # type: ignore
            }
        )
    desc = doc_parsed.short_description or doc_parsed.long_description
    cmd_meta = {
        "name": trailmap.class_attr,
        "path": path,
        "function_name": function_name,
        "func_def": func_def,
        "source_code_url": source_code_url,
        "description": desc if desc else "",
        "params": params,
        "returns": returns,
        "examples": examples,
    }

    default_desc = (doc_parsed.short_description or " .").split(".").pop(
        0
    ).strip().replace(":", "") or trailmap.class_attr

    keywords = "\n- ".join(
        k for k in trailmap.location_path + [trailmap.class_attr] if k
    )

    header = f"title: {trailmap.class_attr}\ndescription: {default_desc}\nkeywords:\n- {keywords}"
    key = f"{'.'.join(trailmap.location_path)}.{trailmap.class_attr}"

    if seo_meta := SEO_META.get(key, None):
        keywords = "\n- ".join(seo_meta["keywords"])
        header = f"title: {seo_meta['title']}\ndescription: {seo_meta['description']}\nkeywords:\n- {keywords}"

    cmd_meta[
        "header"
    ] = f"""---\n{header}\n---\n
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="{key} - Reference | OpenBB SDK Docs" />\n\n"""

    return cmd_meta


def generate_markdown(meta_model: dict, meta_view: dict):
    main_model = meta_model
    if not meta_model:
        if not meta_view:
            raise ValueError("No model or view")
        main_model = meta_view
    markdown = main_model["header"]
    if meta_view and meta_model:
        markdown += """import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';\n\n"""

    if meta_view and meta_model:
        markdown += f"""<Tabs>
<TabItem value="model" label="Model" default>\n
{generate_markdown_section(meta_model)}\n
</TabItem>
<TabItem value="view" label="Chart">\n
{generate_markdown_section(meta_view)}\n
</TabItem>
</Tabs>"""
    else:
        markdown += generate_markdown_section(main_model)
    return markdown


def generate_markdown_section(meta: Dict[str, Any]):
    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    # use real description but need to parse it
    markdown = (
        f"{meta['description']}\n\nSource Code: [[link]({meta['source_code_url']})]\n\n"
    )
    markdown += f"```python wordwrap\n{meta['func_def']}\n```\n\n"

    markdown += "---\n\n## Parameters\n\n"
    if meta["params"]:
        markdown += "| Name | Type | Description | Default | Optional |\n"
        markdown += "| ---- | ---- | ----------- | ------- | -------- |\n"
        for param in meta["params"]:
            description = param["doc"].replace("\n", "<br/>") if param["doc"] else ""
            markdown += f"| {param['name']} | {param['type']} | {description} | {param['default']} | {param['optional']} |\n"  # noqa
        markdown += "\n\n"
    else:
        markdown += "This function does not take any parameters.\n\n"

    markdown += "---\n\n## Returns\n\n"
    if meta["returns"]:
        markdown += "| Type | Description |\n"
        markdown += "| ---- | ----------- |\n"
        return_desc = (
            meta["returns"]["doc"].replace("\n", "<br/>")
            if meta["returns"]["doc"]
            else ""
        )
        markdown += f"| {meta['returns']['type']} | {return_desc} |\n"
    else:
        markdown += "This function does not return anything\n\n"

    markdown += "---\n\n## Examples\n\n" if meta["examples"] else ""
    prev_snippet = "  "
    for example in meta["examples"]:
        if isinstance(example["snippet"], str) and ">>>" in example["snippet"]:
            snippet = example["snippet"].replace(">>> ", "")
            markdown += f"```python\n{snippet}\n```\n\n"
            if example["description"] and prev_snippet != "":
                markdown += f"```\n{example['description']}\n```\n"
                prev_snippet = snippet.strip()
            elif example["description"]:
                markdown += f"\n{example['description']}\n\n"
        else:
            if example["description"]:
                markdown += f"\n{example['description']}\n\n"
            prev_snippet = ""

    markdown += "---\n\n"

    return markdown


def create_nested_menus_card(folder: Path, url: str) -> str:
    sub_categories = [
        sub.stem
        for sub in folder.glob("**/**/*.md*")
        if sub.is_file() and sub.stem != "index"
    ]
    categories = shorten(
        ", ".join(sub_categories or [""]), width=116, placeholder="..."
    )
    url = f"/sdk/reference/{url}/{folder.name}".replace("//", "/")

    index_card = f"""<ReferenceCard
    title="{folder.name.replace("_", " ").title()}"
    description="{categories}"
    url="{url}"
/>\n"""
    return index_card


def create_cmd_cards(cmd_text: List[Dict[str, str]]) -> str:
    cmd_cards = ""
    for cmd in cmd_text:
        url = f"/sdk/reference/{cmd['url']}/{cmd['title']}".replace("//", "/")
        description = shorten(f"{cmd['description']}", width=116, placeholder="...")
        cmd_cards += f"""<ReferenceCard
    title="{cmd["title"].replace("_", " ").title()}"
    description="{description.replace('None', '')}"
    url="{url}"
    command
/>\n"""
    return cmd_cards


def write_reference_index(
    reference_cards: Dict[Path, List[Dict[str, str]]],
    fname: str,
    path: Path,
    rel_path: Path,
    f: TextIO,
) -> None:
    """Write to the corresponding index.mdx file for a given folder, with the
    appropriate nested menus and command cards.

    Parameters
    ----------
    reference_cards : Dict[Path, List[Dict[str, str]]]
        Dictionary of command cards to be written to the index.mdx file.
    fname : str
        Name of the index.mdx file.
    path : Path
        Path to the folder to be written.
    rel_path : Path
        Relative path to the folder to be written.
    f : TextIO
        File to write to.
    """
    f.write(f"# {fname}\n\n{reference_import}")
    sub_folders = [sub for sub in path.glob("*") if sub.is_dir()]
    menus = []

    for folder in sub_folders:
        menus.append(create_nested_menus_card(folder, "/".join(rel_path.parts)))

    if menus:
        f.write(f"### Menus\n{refrence_ul_element}\n{''.join(menus)}</ul>\n")

    folder_cmd_cards: List[Dict[str, str]] = reference_cards.get(path, {})  # type: ignore

    if folder_cmd_cards:
        f.writelines(
            [
                f"\n\n### Commands\n{refrence_ul_element}\n",
                create_cmd_cards(folder_cmd_cards),
                "</ul>\n",
            ]
        )


def main() -> bool:
    """Generate markdown files for OpenBB SDK Documentation."""
    print("Loading trailmaps...")
    trailmaps = get_trailmaps()
    kwargs = {"encoding": "utf-8", "newline": "\n"}

    print("Generating markdown files...")
    reference_cards: Dict[Path, List[Dict[str, str]]] = {}

    for file in CONTENT_PATH.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)
    for trailmap in trailmaps:
        try:
            if trailmap.location_path[0] == "root":
                trailmap.location_path[0] = ""

            model_meta = (
                get_function_meta(trailmap, "model") if trailmap.model else None
            )
            view_meta = get_function_meta(trailmap, "view") if trailmap.view else None
            markdown = generate_markdown(model_meta, view_meta)

            if trailmap.class_attr == "index":
                trailmap.class_attr = "index_cmd"

            filepath = (
                CONTENT_PATH
                / "/".join(trailmap.location_path)
                / f"{trailmap.class_attr}.md"
            )
            func = trailmap.func_attrs.get(
                "model", trailmap.func_attrs.get("view", None)
            )

            reference_cards.setdefault(filepath.parent, []).append(
                dict(
                    title=trailmap.class_attr,
                    description=func.short_doc,  # type: ignore
                    url="/".join(trailmap.location_path),
                )
            )

            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", **kwargs) as f:  # type: ignore
                f.write(markdown)

        except Exception as e:
            print(
                f"Error generating {trailmap.location_path} {trailmap.class_attr} - {e}"
            )
            return False

    # Sort reference_cards
    reference_cards = dict(sorted(reference_cards.items(), key=lambda item: item[0]))

    with open(CONTENT_PATH / "index.mdx", "w", **kwargs) as f:  # type: ignore
        fname = "OpenBB SDK Reference"
        rel_path = CONTENT_PATH.relative_to(CONTENT_PATH)
        write_reference_index(reference_cards, fname, CONTENT_PATH, rel_path, f)

    with open(CONTENT_PATH / "_category_.json", "w", **kwargs) as f:  # type: ignore
        """Generate category json"""
        f.write(json.dumps({"label": "Reference", "position": 4}, indent=2))

    def gen_category_json(fname: str, path: Path, position: int = 1):
        """Generate category json"""
        with open(path / "_category_.json", "w", **kwargs) as f:  # type: ignore
            f.write(
                json.dumps({"label": fname.title(), "position": position}, indent=2)
            )

        with open(path / "index.mdx", "w", **kwargs) as f:  # type: ignore
            rel_path = path.relative_to(CONTENT_PATH)
            write_reference_index(reference_cards, fname, path, rel_path, f)

    def gen_category_recursive(nested_path: Path):
        """Generate category json recursively"""
        position = 1
        for folder in nested_path.iterdir():
            if folder.is_dir():
                gen_category_json(folder.name, folder, position)
                gen_category_recursive(folder)  # pylint: disable=cell-var-from-loop
                position += 1

    gen_category_recursive(CONTENT_PATH)
    print("Markdown files generated, check the functions folder")

    return True


def save_metadata() -> Dict[str, Dict[str, Union[str, List[str]]]]:
    """Save SEO metadata to json file."""

    regex = re.compile(
        r"---\ntitle: (.*)\ndescription: (.*)\nkeywords:(.*)\n---\n\nimport HeadTitle",
        re.MULTILINE | re.DOTALL,
    )

    metadata = {}
    for file in CONTENT_PATH.rglob("*/**/*.md"):
        context = file.read_text(encoding="utf-8")
        match = regex.search(context)
        if match:
            title, description, keywords = match.groups()
            key = file.relative_to(CONTENT_PATH).as_posix().removesuffix(".md")
            metadata[key.replace("/", ".")] = {
                "title": title,
                "description": description,
                "keywords": [
                    keyword.strip() for keyword in keywords.split("\n- ") if keyword
                ],
            }

    filepath = website_path / "metadata/sdk_v3_seo_metadata.json"
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    main()
