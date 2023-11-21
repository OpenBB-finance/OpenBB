import requests
from pathlib import Path


def main() -> bool:
    widgets_json_url = "https://raw.githubusercontent.com/OpenBB-finance/widgets-library/main/widgets.json"

    response = requests.get(widgets_json_url)
    widgets_data = response.json()

    # Process the data into the desired format
    all_widgets = {}
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

    base_path = Path("content/pro/widgets-library")

    for category, widgets in all_widgets.items():
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)

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

    {'Source: ' + ','.join(widget['source']) if widget['source'] else ''}
    """
            with widget_path.open("w") as widget_file:
                widget_file.write(f"{text}\n")

    return True


if __name__ == "__main__":
    main()
