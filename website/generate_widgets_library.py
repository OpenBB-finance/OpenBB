from pathlib import Path
from typing import Dict

import requests


def main() -> bool:
    widgets_json_url = "https://raw.githubusercontent.com/OpenBB-finance/widgets-library/main/widgets.json"

    response = requests.get(widgets_json_url, timeout=10)
    widgets_data: Dict[str, Dict[str, dict]] = response.json()

    # Process the data into the desired format
    all_widgets: Dict[str, list] = {}
    for widget_id, widget_info in widgets_data.items():
        if widget_info.get("disabled", False):
            continue

        category = widget_info.get("category")
        if category:
            if category not in all_widgets:
                all_widgets[category] = []

            all_widgets[category].append(
                {
                    "name": widget_info.get("name"),
                    "description": widget_info.get("description"),
                    "source": widget_info.get("source"),
                    "widgetId": widget_info.get("widgetId"),
                }
            )

    # Create the category index file
    text = """# Widgets Library

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 gap-4 -ml-6">
"""
    for category, widgets in all_widgets.items():
        text += f"""
<NewReferenceCard
    title="{category}"
    description="{', '.join([widget['name'] for widget in widgets])}"
    url="/pro/widgets-library/{category}"
/>"""
    text += "\n</ul>"

    website_path = Path(__file__).parent.absolute()
    base_path = website_path / "content" / "pro" / "widgets-library"

    index_path = base_path / "index.mdx"
    with index_path.open("w", encoding="utf-8", newline="\n") as index_file:
        index_file.write(f"{text}\n")

    for category, widgets in all_widgets.items():
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        # Create the category index file
        text = f"""# {category}

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
"""
        for widget in widgets:
            text += f"""
<NewReferenceCard
    title="{widget['name']}"
    description="{widget['description']}"
    url="/pro/widgets-library/{category}/{widget['widgetId']}"
    command
/>"""
        text += "\n</ul>"

        index_path = category_path / "index.mdx"
        with index_path.open("w", encoding="utf-8", newline="\n") as index_file:
            index_file.write(f"{text}\n")

        # Create each individual widget file
        for widget in widgets:
            widget_path = category_path / f"{widget['widgetId']}.md"

            text = f"""---
title: {widget['name']}
description: {widget['description']}
keywords:
- OpenBB
- Terminal Pro
- Investment Research
- Widgets
- {widget['name']}
- {category}
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="{widget['name']} - {category} | OpenBB Terminal Pro Docs" />

<img
    src="https://raw.githubusercontent.com/OpenBB-finance/widgets-library/main/{category}/{widget['widgetId']}.png"
    alt="OpenBB Terminal Pro Widgets Library"
/>

{widget['description']}.

{'**Source:** ' + ','.join(widget['source']) if widget['source'] else ''}
"""
            with widget_path.open("w", encoding="utf-8", newline="\n") as widget_file:
                widget_file.write(f"{text}\n")

    return True


if __name__ == "__main__":
    main()
