"""Rich table output adapter."""

from typing import Any

import pandas as pd

from openbb_cli.controllers.utils import print_rich_table
from openbb_cli.session import Session

session = Session()


class RichTableOutput:
    """Rich table output adapter with truncation for terminal display."""

    def display(  # noqa: PLR0911
        self,
        data: Any,
        title: str = "",
        export: bool = False,
        chart: bool = False,
    ) -> None:
        """Display using rich table with row/column limits."""
        if export:
            return

        if hasattr(data, "model_dump"):
            if chart:
                try:
                    data.show()
                    return
                except Exception as e:
                    session.console.print(f"[yellow]Chart not available: {e}[/yellow]")

            if session.settings.USE_INTERACTIVE_DF and session.backend is not None:
                try:
                    data.charting.table()
                    return
                except Exception as e:
                    session.console.print(
                        f"[yellow]Interactive table not available: {e}[/yellow]"
                    )

            results = data.model_dump(exclude_unset=True, exclude_none=True).get(
                "results"
            )

            if results is None:
                session.console.print("[yellow]No results to display[/yellow]")
                return

            try:
                if isinstance(results, pd.DataFrame):
                    df = results
                elif isinstance(results, list):
                    if not results:
                        session.console.print("[yellow]Empty results[/yellow]")
                        return
                    df = pd.DataFrame(results)
                elif isinstance(results, dict):
                    df = pd.DataFrame([results])
                else:
                    session.console.print(results)
                    return
            except Exception as e:
                session.console.print(f"[yellow]Cannot display as table: {e}[/yellow]")
                session.console.print(results)
                return

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
            if df.empty:
                session.console.print("[yellow]Empty DataFrame[/yellow]")
                return
        elif isinstance(data, pd.Series):
            df = data.to_frame()
        elif isinstance(data, dict):
            try:
                df = pd.DataFrame.from_dict(data, orient="columns")
            except Exception:
                session.console.print(data)
                return
        elif isinstance(data, (list, tuple)):
            if not data:
                session.console.print("[yellow]Empty data[/yellow]")
                return
            try:
                df = pd.DataFrame(data)
            except Exception:
                session.console.print(data)
                return
        else:
            session.console.print(data)
            return

        if isinstance(df.columns, pd.RangeIndex):
            df.columns = [str(i) for i in df.columns]

        print_rich_table(df=df, show_index=True, title=title, export=export)
