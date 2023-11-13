import re
from pathlib import Path
from textwrap import shorten
from typing import Dict, List

reference_import = """import ReferenceCard from "@site/src/components/General/ReferenceCard";

<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
"""
wopen_kwargs = {"encoding": "utf-8", "newline": "\n"}


def create_cmd_cards(cmd_text: List[Dict[str, str]], url: str) -> str:
    _cmd_cards = ""
    for cmd in cmd_text:
        cmd["description"] = shorten(f"{cmd['description']}", 116, placeholder="...")
        _cmd_cards += f"""<ReferenceCard
    title="{cmd["name"]}"
    description="{cmd["description"]}"
    url="{url}/{cmd["name"]}"
/>\n"""
    return _cmd_cards


def create_nested_subfolder_card(_folder: Path, url: str) -> str:
    nested_card = f"""<ReferenceCard
        title="{_folder.name.capitalize()}"
        description="{', '.join([sub.stem for sub in _folder.glob('**/*.md*') if sub.is_file() and sub.stem != 'index'])}"
        url="{url}/{_folder.name}"
    />\n"""
    return nested_card


for bot in [
    "terminal",
    "platform",
    "bot",
    "terminal/usage",
    "terminal/menus",
]:
    for folder in (Path(__file__).parent / bot).iterdir():
        rel_path = folder.relative_to(Path(__file__).parent / bot)
        cmd_cards: List[Dict[str, str]] = []

        print(rel_path)
        print(cmd_cards)

        for file in folder.glob("*.md*"):
            if file.stem == "index":
                continue

            desc_regex = re.compile(r"^---(.*?)---", re.DOTALL | re.MULTILINE)

            description = desc_regex.search(file.read_text(encoding="utf-8")).group(1).strip()  # type: ignore

            pattern = re.compile(r"^(title|description):\s*(.*)$", re.MULTILINE)

            # Find all matches in the text
            matches = pattern.findall(description)

            # Extract title and description values
            title = description = None
            for key, value in matches:
                if key == "title":
                    title = value.strip()
                elif key == "description":
                    description = value.strip()

            cmd_dict = dict(
                name=title,
                description=description,
                url=f"{bot}/{rel_path}",
            )

            cmd_cards.append(cmd_dict)

        if not cmd_cards:
            continue

        with open(
            Path(__file__).parent / bot / rel_path / "index.mdx", "w", **wopen_kwargs  # type: ignore
        ) as subindex:
            subindex.write(f"# {folder.name}\n\n{reference_import}\n")

            for subfolder in folder.glob("*"):
                if not subfolder.is_dir():
                    continue

                subindex.write(create_nested_subfolder_card(subfolder, f"{rel_path}"))
            print(cmd_cards)
            subindex.write(create_cmd_cards(cmd_cards, f'{"/".join(rel_path.parts)}'))
            subindex.write("</ul>\n")

    with open(Path(__file__).parent / bot / "index.mdx", "w", **wopen_kwargs) as index:  # type: ignore
        index.write(f"# OpenBB {bot.title()} Reference\n\n{reference_import}\n")

        for folder in (Path(__file__).parent / bot).glob("*"):
            if not folder.is_dir():
                continue

            index.write(create_nested_subfolder_card(folder, bot))
        index.write("</ul>\n")
