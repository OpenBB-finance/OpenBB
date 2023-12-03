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
    url="/bot/reference/{url}/{cmd["name"]}"
/>\n"""
    return _cmd_cards


def create_nested_subfolder_card(_folder: Path, url: str) -> str:
    nested_card = f"""<ReferenceCard
        title="{_folder.name}"
        description="{' '.join([sub.stem for sub in _folder.glob('**/*.md*') if sub.is_file() and sub.stem != 'index'])}"
        url="/bot/reference/{url}/{_folder.name}"
    />\n"""
    return nested_card


for bot in ["discord", "telegram"]:
    for folder in (Path(__file__).parent / bot).iterdir():
        rel_path = folder.relative_to(Path(__file__).parent / bot)
        cmd_cards: List[Dict[str, str]] = []

        for file in folder.glob("*.md*"):
            if file.stem == "index":
                continue

            desc_regex = re.compile(r"([^>]+)(.*)### Usage", (re.MULTILINE))

            description = desc_regex.search(file.read_text()).group(1).strip()  # type: ignore

            cmd_dict = dict(
                name=file.stem,
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

                subindex.write(
                    create_nested_subfolder_card(subfolder, f"{bot}/{rel_path}")
                )

            subindex.write(
                create_cmd_cards(cmd_cards, f'{bot}/{"/".join(rel_path.parts)}')
            )
            subindex.write("</ul>\n")

    with open(Path(__file__).parent / bot / "index.mdx", "w", **wopen_kwargs) as index:  # type: ignore
        index.write(f"# OpenBB {bot.title()} Reference\n\n{reference_import}\n")

        for folder in (Path(__file__).parent / bot).glob("*"):
            if not folder.is_dir():
                continue

            index.write(create_nested_subfolder_card(folder, bot))
        index.write("</ul>\n")
