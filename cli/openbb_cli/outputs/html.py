"""HTML output adapter."""

import tempfile
import webbrowser
from pathlib import Path
from typing import Any

import pandas as pd

from openbb_cli.session import Session

session = Session()


class HtmlOutput:
    """HTML output adapter - generates HTML and opens in default browser."""

    def display(
        self,
        data: Any,
        title: str = "",
        export: bool = False,
        chart: bool = False,
    ) -> None:
        """Display as HTML in default browser."""
        if export:
            return

        if hasattr(data, "model_dump"):
            if session.settings.USE_INTERACTIVE_DF and session.backend is not None:
                try:
                    data.charting.table()
                    return
                except Exception as e:
                    session.console.print(
                        f"[yellow]Interactive table not available: {e}[/yellow]"
                    )

            if chart:
                try:
                    data.show()
                    return
                except Exception as e:
                    session.console.print(
                        f"[yellow]Chart not available, showing table instead: {e}[/yellow]"
                    )

        if hasattr(data, "model_dump"):
            results = data.model_dump().get("results")
            if results is None:
                session.console.print("[yellow]No results to display[/yellow]")
                return

            if isinstance(results, pd.DataFrame):
                df = results
            elif isinstance(results, list):
                df = pd.DataFrame(results)
            elif isinstance(results, dict):
                df = pd.DataFrame([results])
            else:
                df = pd.DataFrame({"value": [results]})
        elif isinstance(data, pd.DataFrame):
            df = data
            if session.settings.USE_INTERACTIVE_DF and session.backend is not None:
                try:
                    session.backend.send_table(
                        df_table=df,
                        title=title,
                        theme=session.user.preferences.table_style,
                    )
                    return
                except Exception:  # noqa: S110
                    pass
        elif isinstance(data, pd.Series):
            df = data.to_frame()
        elif isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, orient="columns")
        elif isinstance(data, (list, tuple)):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame({"value": [data]})

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {df.to_html(index=True, border=0)}
</body>
</html>
"""

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".html", encoding="utf-8"
        ) as f:
            f.write(html_content)
            temp_path = f.name

        webbrowser.open(f"file://{Path(temp_path).as_posix()}")
        session.console.print(f"[green]Opened table in browser: {temp_path}[/green]")
