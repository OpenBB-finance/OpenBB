from pathlib import Path
from typing import Dict

import requests

# ruff: noqa


def main() -> bool:
    widgets_json_url = "https://raw.githubusercontent.com/OpenBB-finance/widgets-library/main/widgets.json"

    response = requests.get(widgets_json_url, timeout=10)
    widgets_data: Dict[str, Dict[str, dict]] = response.json()

    # Process the data into the desired format
    # New all widgets
    new_all_widgets = {}
    for widget_id, widget_info in widgets_data.items():
        # Skip disabled widgets
        if widget_info.get("disabled", False):
            continue

        category_1 = widget_info.get("category")  # this is a mandatory field
        if category_1:
            # Initialize dict for category_1 within category_root
            if category_1 not in new_all_widgets:
                new_all_widgets[category_1] = {}

            category_2 = widget_info.get("sub_category")  # OPTIONAL field
            if category_2:
                if category_2 not in new_all_widgets[category_1]:
                    new_all_widgets[category_1][category_2] = []

                new_all_widgets[category_1][category_2].append(
                    {
                        "name": widget_info.get("name"),
                        "description": widget_info.get("description"),
                        "source": widget_info.get("source"),
                        "widgetId": widget_info.get("widgetId"),
                    }
                )

            else:
                # The CATEGORYLESS is used to indicate that the widget doesn't has a level 2 category
                if "CATEGORYLESS" not in new_all_widgets[category_1]:
                    new_all_widgets[category_1]["CATEGORYLESS"] = []

                new_all_widgets[category_1]["CATEGORYLESS"].append(
                    {
                        "name": widget_info.get("name"),
                        "description": widget_info.get("description"),
                        "source": widget_info.get("source"),
                        "widgetId": widget_info.get("widgetId"),
                    }
                )
        else:
            print("SHOULD NEVER GET HERE BECAUSE CATEGORY_1 IS A MANDATORY FIELD!")

    website_path = Path(__file__).parent.absolute()
    base_path = website_path / "content" / "pro" / "widgets-library"

    ## Handle category_root level
    index_path = base_path / "index.mdx"

    # Check if the directory exists, if not create it
    if not index_path.parent.exists():
        index_path.parent.mkdir(parents=True)

    # Create content for index file
    text = """# Widgets Library

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 gap-4 -ml-6">
"""
    for category_1, widgets in new_all_widgets.items():
        # Get all elements
        l_elements = list(new_all_widgets[category_1].keys())
        if "CATEGORYLESS" in new_all_widgets[category_1]:
            l_elements.remove("CATEGORYLESS")
            l_elements += [
                k["name"] for k in new_all_widgets[category_1]["CATEGORYLESS"]
            ]

        text += f"""
<NewReferenceCard
    title="{category_1}"
    description="{', '.join(l_elements)}"
    url="/pro/widgets-library/{category_1.lower().replace(' ', '-')}"
/>"""
    text += "\n</ul>"

    # Create index file
    with index_path.open("w", encoding="utf-8", newline="\n") as index_file:
        index_file.write(f"{text}\n")

    ## Handle category_1 level
    for category_1, widgets in new_all_widgets.items():
        # Check if the directory exists, if not create it
        index_path = base_path / category_1.lower().replace(" ", "-") / "index.mdx"
        if not index_path.parent.exists():
            index_path.parent.mkdir(parents=True)

        # Create content for index file
        text = f"""# {category_1}

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 gap-4 -ml-6">
"""
        for category_1, widgets in new_all_widgets.items():
            # Get all elements
            l_elements = list(new_all_widgets[category_1].keys())
            if "CATEGORYLESS" in new_all_widgets[category_1]:
                l_elements.remove("CATEGORYLESS")
                l_elements += [
                    k["name"] for k in new_all_widgets[category_1]["CATEGORYLESS"]
                ]

            text += f"""
<NewReferenceCard
    title="{category_1}"
    description="{', '.join(l_elements)}"
    url="/pro/widgets-library/{category_1.lower().replace(' ', '-')}"
/>"""

        text += "\n</ul>"

        # Check if the path is a directory
        if index_path.is_dir():
            print(f"{index_path} is a directory, not a file.")
            continue

        # Create index file
        with index_path.open("w", encoding="utf-8", newline="\n") as index_file:
            index_file.write(f"{text}\n")

        for category_1, widgets in new_all_widgets.items():
            # Check if the directory exists, if not create it
            index_path = base_path / category_1.lower().replace(" ", "-") / "index.mdx"
            if not index_path.parent.exists():
                index_path.parent.mkdir(parents=True)

            text = f"""# {category_1}

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 gap-4 -ml-6">
"""

            for category_2, widgets in new_all_widgets[category_1].items():
                # Get all elements
                if category_2 != "CATEGORYLESS":
                    text += f"""
<NewReferenceCard
    title="{category_2}"
    description="{', '.join([k['name'] for k in widgets])}"
    url="/pro/widgets-library/{category_1.lower().replace(' ', '-')}/{category_2.lower().replace(' ', '-')}"
/>"""
                else:
                    # Iterate through all the widgets to create 1 command reference for each
                    for w in widgets:
                        text += f"""
<NewReferenceCard
    title="{w['name']}"
    description="{w['description']}"
    url="/pro/widgets-library/{category_1.lower().replace(' ', '-')}/{w['widgetId']}"
    command
/>"""

            text += "\n</ul>"

            # Check if the path is a directory
            index_path = base_path / category_1.lower().replace(" ", "-") / "index.mdx"
            if index_path.is_dir():
                print(f"{index_path} is a directory, not a file.")
                continue

            # Create index file
            with index_path.open("w", encoding="utf-8", newline="\n") as index_file:
                index_file.write(f"{text}\n")

            # Handle category_2 level index
            for category_2, widgets in new_all_widgets[category_1].items():
                if category_2 != "CATEGORYLESS":
                    # Check if the directory exists, if not create it
                    index_path = (
                        base_path
                        / category_1.lower().replace(" ", "-")
                        / category_2.lower().replace(" ", "-")
                        / "index.mdx"
                    )
                    if not index_path.parent.exists():
                        index_path.parent.mkdir(parents=True)

                    text = f"""# {category_2}

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 gap-4 -ml-6">
"""
                    for w in widgets:
                        text += f"""
<NewReferenceCard
    title="{w['name']}"
    description="{w['description']}"
    url="/pro/widgets-library/{category_1.lower().replace(' ', '-')}/{category_2.lower().replace(' ', '-')}/{w['widgetId']}"
    command
/>"""

                    text += "\n</ul>"
                    # Create index file
                    with index_path.open(
                        "w", encoding="utf-8", newline="\n"
                    ) as index_file:
                        index_file.write(f"{text}\n")

                    # Check if the path is a directory
                    index_path = (
                        base_path
                        / category_1.lower().replace(" ", "-")
                        / category_2.lower().replace(" ", "-")
                        / "index.mdx"
                    )
                    if index_path.is_dir():
                        print(f"{index_path} is a directory, not a file.")
                        continue

                # HANDLE ALL FILES BELOW

                # This means that there's no subcategory, i.e. category_2 is non existent
                if category_2 == "CATEGORYLESS":
                    # Create each individual widget file
                    for widget in widgets:
                        widget_path = (
                            base_path
                            / category_1.lower().replace(" ", "-")
                            / f"{widget['widgetId']}.md"
                        )

                        text = f"""---
title: {widget['name']}
description: {widget['description']}
keywords:
- OpenBB
- Terminal Pro
- Investment Research
- Widgets
- {widget['name']}
- {category_1}
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="{widget['name']} - {category_1} | OpenBB Terminal Pro Docs" />

<img
    className="pro-border-gradient"
    src="https://raw.githubusercontent.com/OpenBB-finance/widgets-library/main/{category_1.lower().replace(' ', '_')}/{widget['widgetId']}.png"
    alt="OpenBB Terminal Pro Widgets Library"
/>

{widget['description']}.

{'**Source:** ' + ','.join(widget['source']) if widget['source'] else ''}
"""

                        with widget_path.open(
                            "w", encoding="utf-8", newline="\n"
                        ) as widget_file:
                            widget_file.write(text)

                else:
                    # Create each individual widget file
                    for widget in widgets:
                        widget_path = (
                            base_path
                            / category_1.lower().replace(" ", "-")
                            / category_2.lower().replace(" ", "-")
                            / f"{widget['widgetId']}.md"
                        )

                        text = f"""---
title: {widget['name']}
description: {widget['description']}
keywords:
- OpenBB
- Terminal Pro
- Investment Research
- Widgets
- {widget['name']}
- {category_1}
- {category_2}
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="{widget['name']} - {category_2} - {category_1} | OpenBB Terminal Pro Docs" />

<img
    className="pro-border-gradient"
    src="https://raw.githubusercontent.com/OpenBB-finance/widgets-library/main/{category_1.lower().replace(' ', '_')}/{category_2.lower().replace(' ', '_')}/{widget['widgetId']}.png"
    alt="OpenBB Terminal Pro Widgets Library"
/>

{widget['description']}.

{'**Source:** ' + ','.join(widget['source']) if widget['source'] else ''}
"""

                        with widget_path.open(
                            "w", encoding="utf-8", newline="\n"
                        ) as widget_file:
                            widget_file.write(text)

    return True


if __name__ == "__main__":
    main()
