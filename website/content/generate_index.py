import re
from pathlib import Path
from textwrap import shorten
from typing import Dict, List

# Importing the ReferenceCard component for use in the generated index
reference_import = """import ReferenceCard from "@site/src/components/General/ReferenceCard";

<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
"""
# Setting the encoding and newline character for file writing
wopen_kwargs = {"encoding": "utf-8", "newline": "\n"}


# Function to create command cards for each command in the provided list
def create_cmd_cards(cmd_text: List[Dict[str, str]], url: str) -> str:
    _cmd_cards = ""
    for cmd in cmd_text:
        # Shortening the description to fit within the card
        cmd["description"] = shorten(f"{cmd['description']}", 116, placeholder="...")
        # Adding the command card to the list
        _cmd_cards += f"""<ReferenceCard
    title="{cmd["name"]}"
    description="{cmd["description"]}"
    url="{url}/{cmd["name"]}"
/>\n"""
    return _cmd_cards


# Function to create a card for each subfolder in the provided folder
def create_nested_subfolder_card(_folder: Path, url: str) -> str:
    # Creating a list of all markdown files in the subfolder
    nested_card = f"""<ReferenceCard
        title="{_folder.name.capitalize()}"
        description="{', '.join([sub.stem for sub in _folder.glob('**/*.md*') if sub.is_file() and sub.stem != 'index'])}"
        url="{url}/{_folder.name}"
    />\n"""
    return nested_card


# Looping through each topfolder to generate the index
for topfolder in [
    "terminal",
    "platform",
    "bot",
    "terminal/usage",
    "terminal/menus",
    "excel",
]:
    # Looping through each folder in the fold directory
    for folder in (Path(__file__).parent / topfolder).iterdir():
        rel_path = folder.relative_to(Path(__file__).parent / topfolder)
        cmd_cards: List[Dict[str, str]] = []

        print(rel_path)
        print(cmd_cards)

        # Looping through each markdown file in the folder
        for file in folder.glob("*.md*"):
            if file.stem == "index":
                continue

            # Regex to extract the description from the file
            desc_regex = re.compile(r"^---(.*?)---", re.DOTALL | re.MULTILINE)

            description = desc_regex.search(file.read_text(encoding="utf-8")).group(1).strip()  # type: ignore

            # Regex to extract the title and description from the description
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

            # Creating a dictionary for the command
            cmd_dict = dict(
                name=title,
                description=description,
                url=f"{topfolder}/{rel_path}",
            )

            # Adding the command to the list of commands
            cmd_cards.append(cmd_dict)

        if not cmd_cards:
            continue

        # Writing the index for the subfolder
        with open(
            Path(__file__).parent / topfolder / rel_path / "index.mdx", "w", **wopen_kwargs  # type: ignore
        ) as subindex:
            subindex.write(f"# {folder.name}\n\n{reference_import}\n")

            # Writing a card for each subfolder in the folder
            for subfolder in folder.glob("*"):
                if not subfolder.is_dir():
                    continue

                subindex.write(create_nested_subfolder_card(subfolder, f"{rel_path}"))
            print(cmd_cards)
            # Writing the command cards to the index
            subindex.write(create_cmd_cards(cmd_cards, f'{"/".join(rel_path.parts)}'))
            subindex.write("</ul>\n")

    # Writing the main index for the topfolder
    with open(Path(__file__).parent / topfolder / "index.mdx", "w", **wopen_kwargs) as index:  # type: ignore
        index.write(f"# OpenBB {topfolder.title()} Reference\n\n{reference_import}\n")

        # Writing a card for each folder in the bot directory
        for folder in (Path(__file__).parent / topfolder).glob("*"):
            if not folder.is_dir():
                continue

            index.write(create_nested_subfolder_card(folder, topfolder))
        index.write("</ul>\n")
