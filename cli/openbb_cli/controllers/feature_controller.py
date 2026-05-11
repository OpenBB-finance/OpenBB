"""Feature Engineering Controller."""

import argparse
import ast

import pandas as pd

from openbb_cli.controllers.base_controller import BaseController, session
from openbb_cli.controllers.utils import extract_dataframe


class FeatureController(BaseController):
    """Feature Engineering Controller class.

    Provides CRUD operations for columns, tables, and files.
    Allows joining tables and performing pandas query statements.
    """

    CHOICES_COMMANDS = [
        "list",
        "select",
        "info",
        "view",
        "query",
        "colname",
        "coltype",
        "addcol",
        "dropcol",
        "renamecol",
        "modifycol",
        "join",
        "copy",
        "save",
        "delete",
        "results",
    ]

    PATH = "/feature/"
    CHOICES_GENERATION = True

    def __init__(
        self,
        queue: list[str] | None = None,
    ):
        """Initialize Feature Engineering Controller."""
        super().__init__(queue=queue)
        self.current_table: int | None = None
        self.update_completer(self.choices_default)

    def _get_table_indices(self) -> list[str]:
        """Get list of table indices from cache.

        Returns meaningful names (register_key or simplified identifier) for completions.
        Names must not contain spaces, commas, or special characters that get parsed.
        """
        if session.obbject_registry.all:
            names = []
            for idx, data in session.obbject_registry.all.items():
                name = data.get("key", "")

                if not name:
                    name = str(idx)

                names.append(name)
            return names
        return []

    def _resolve_table_identifier(self, identifier: str) -> int | None:
        """Resolve a table identifier (name or index) to numeric index.

        Args:
            identifier: Either a register_key or numeric index

        Returns
        -------
            The numeric index if found, None otherwise
        """
        try:
            idx = int(identifier)
            if idx in session.obbject_registry.all:
                return idx
        except ValueError:
            pass

        for idx, data in session.obbject_registry.all.items():
            if data.get("key") == identifier:
                return idx

        return None

    def _get_column_names(self) -> list[str]:
        """Get column names from current table."""
        if self.current_table is not None:
            result = session.obbject_registry.get(self.current_table)
            if result:
                df = extract_dataframe(result)
                return df.columns.tolist()
        return []

    @property
    def choices_default(self) -> dict:
        """Return default choices with dynamic completions."""
        table_indices = self._get_table_indices()
        column_names = self._get_column_names()

        column_recursive: dict = {"--help": None, "-h": "--help"}
        if column_names:
            for col in column_names:
                column_recursive[col] = {"--help": None, "-h": "--help"}
                for next_col in column_names:
                    if next_col != col:
                        column_recursive[col][next_col] = {
                            "--help": None,
                            "-h": "--help",
                        }

        choices = {
            "list": {
                "--help": None,
                "-h": "--help",
            },
            "select": {
                **{idx: None for idx in table_indices},
                "--help": None,
                "-h": "--help",
            },
            "info": {
                "--help": None,
                "-h": "--help",
            },
            "view": {
                "--head": None,
                "--tail": None,
                "--help": None,
                "-h": "--help",
            },
            "query": {
                **{col: None for col in column_names},
                "--save": None,
                "-s": "--save",
                "--help": None,
                "-h": "--help",
            },
            "colname": {
                "--help": None,
                "-h": "--help",
            },
            "coltype": {
                **{
                    col: {
                        "int64": None,
                        "float64": None,
                        "float32": None,
                        "int32": None,
                        "str": None,
                        "object": None,
                        "bool": None,
                        "datetime64[ns]": None,
                        "category": {
                            "--categories": None,
                            "--ordered": None,
                            "--help": None,
                            "-h": "--help",
                        },
                        "--help": None,
                        "-h": "--help",
                    }
                    for col in column_names
                },
                "--help": None,
                "-h": "--help",
            },
            "addcol": {
                "--help": None,
                "-h": "--help",
            },
            "dropcol": {
                **{
                    col: {
                        **{c: None for c in column_names if c != col},
                        "--help": None,
                        "-h": "--help",
                    }
                    for col in column_names
                },
                "--help": None,
                "-h": "--help",
            },
            "renamecol": {
                **{col: None for col in column_names},
                "--help": None,
                "-h": "--help",
            },
            "modifycol": {
                **{col: None for col in column_names},
                "--help": None,
                "-h": "--help",
            },
            "join": {
                **{
                    idx: {
                        "--on": {col: None for col in column_names},
                        "-o": "--on",
                        "--left-on": {col: None for col in column_names},
                        "-l": "--left-on",
                        "--right-on": None,
                        "-r": "--right-on",
                        "--type": {
                            "inner": None,
                            "left": None,
                            "right": None,
                            "outer": None,
                        },
                        "-t": "--type",
                        "--save": None,
                        "-s": "--save",
                        "--help": None,
                        "-h": "--help",
                    }
                    for idx in table_indices
                },
                "--on": {col: None for col in column_names},
                "-o": "--on",
                "--left-on": {col: None for col in column_names},
                "-l": "--left-on",
                "--right-on": None,
                "-r": "--right-on",
                "--type": {
                    "inner": None,
                    "left": None,
                    "right": None,
                    "outer": None,
                },
                "-t": "--type",
                "--save": None,
                "-s": "--save",
                "--help": None,
                "-h": "--help",
            },
            "copy": {
                "--help": None,
                "-h": "--help",
            },
            "save": {
                "--index": None,
                "-i": "--index",
                "--table": None,
                "-t": "--table",
                "--mode": {
                    "replace": None,
                    "append": None,
                    "fail": None,
                },
                "-m": "--mode",
                "--sheet-name": None,
                "-s": "--sheet-name",
                "--help": None,
                "-h": "--help",
            },
            "delete": {
                **{idx: None for idx in table_indices},
                "--help": None,
                "-h": "--help",
            },
            "results": {
                **{idx: None for idx in table_indices},
                "--index": {idx: None for idx in table_indices},
                "-i": "--index",
                "--key": {idx: None for idx in table_indices},
                "-k": "--key",
                "--chart": None,
                "-c": "--chart",
                "--export": {
                    "csv": None,
                    "json": None,
                    "xlsx": None,
                    "png": None,
                    "jpg": None,
                    "db": None,
                    "sqlite": None,
                    "sqlite3": None,
                },
                "-e": "--export",
                "--sheet-name": None,
                "--help": None,
                "-h": "--help",
            },
            "load": {
                "-f": None,
                "--file": None,
                "--register_key": None,
                "--sheet-name": None,
                "--help": None,
                "-h": "--help",
            },
            "cls": None,
            "home": None,
            "h": None,
            "?": None,
            "help": None,
            "q": None,
            "quit": None,
            "..": None,
            "e": None,
            "exit": None,
            "r": None,
            "reset": None,
            "stop": None,
        }

        return choices

    def print_help(self):
        """Print help."""
        current_table_info = ""
        if self.current_table is not None:
            try:
                result = session.obbject_registry.get(self.current_table)
                if result:
                    df = extract_dataframe(result)
                    metadata = session.obbject_registry.all.get(self.current_table, {})
                    table_name = metadata.get("key", "")
                    if not table_name:
                        table_name = f"Table {self.current_table}"

                    col_list = list(df.columns)
                    col_names = ", ".join(col_list)

                    current_table_info = f"""
[info]Current Selection:[/info]
    [bold green]{table_name}[/bold green] - {df.shape[0]} rows × {df.shape[1]} columns
    [yellow]{col_names}[/yellow]

"""
            except Exception:
                current_table_info = (
                    f"\n[yellow]Selected table {self.current_table}[/yellow]\n\n"
                )

        help_text = (
            "\n[info]Feature Engineering - Data Manipulation Menu[/info]\n"  # noqa: S608
            + current_table_info
            + "\n[cmds]"
            """
    list            list all tables in cache
    select          select a table to work with
    info            show information about current table (shape, dtypes, etc)
    view            display current table

[info]Column Operations:[/info]
    colname         list all column names and types
    coltype         change column data type
    addcol          add new column with expression
    dropcol         drop/delete column(s)
    renamecol       rename column
    modifycol       modify column with expression

[info]Table Operations:[/info]
    query           execute pandas query statement
    join            join current table with another table
    copy            copy current table to new name

[info]File Operations:[/info]
    save            save current table to file (CSV, JSON, Excel)
    delete          delete table from cache
[/cmds]
"""
        )
        session.console.print(text=help_text, menu="Feature")

    def call_list(self, other_args: list[str]):
        """List all tables in the results cache."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="list",
            description="List all tables available in the cache.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not session.obbject_registry.all:
                session.console.print("[yellow]No tables in cache.[/yellow]")
                return

            tables_data = []
            for idx in session.obbject_registry.all:
                result = session.obbject_registry.get(idx)
                if result:
                    df = extract_dataframe(result)
                    tables_data.append(
                        {
                            "Index": idx,
                            "Rows": len(df),
                            "Columns": len(df.columns),
                            "Current": "✓" if idx == self.current_table else "",
                        }
                    )

            if tables_data:
                tables_df = pd.DataFrame(tables_data)
                session.output_adapter.display(
                    data=tables_df,
                    title="Tables in Cache",
                    export=False,
                    chart=False,
                )
            else:
                session.console.print("[yellow]No dataframes in cache.[/yellow]")

    def call_select(self, other_args: list[str]):
        """Select a table to work with."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="select",
            description="Select a table from cache to work with.",
        )
        parser.add_argument(
            "index",
            type=str,
            help="Index or register_key of the table to select",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            result = session.obbject_registry.get(ns_parser.index)

            if result is None:
                try:
                    idx = int(ns_parser.index)
                    result = session.obbject_registry.get(idx)
                except ValueError:
                    pass

            if result:
                for idx, obj in enumerate(reversed(session.obbject_registry.obbjects)):
                    if obj.id == result.id:
                        self.current_table = idx
                        break

                df = extract_dataframe(result)
                table_name = result.extra.get("register_key", "")
                if not table_name:
                    table_name = f"Table {self.current_table}"

                session.console.print(
                    f"[green]Selected table '{table_name}' "
                    f"with shape {df.shape}[/green]"
                )
                self.update_completer(self.choices_default)
            else:
                session.console.print(
                    f"[red]Table '{ns_parser.index}' not found in cache.[/red]"
                )

    def call_info(self, other_args: list[str]):
        """Show information about current table."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Display information about the current table.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            session.console.print(f"\n[bold]Table: {self.current_table}[/bold]")
            session.console.print(
                f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
            )

            info_data = []
            for col in df.columns:
                info_data.append(
                    {
                        "Column": col,
                        "Type": str(df[col].dtype),
                        "Non-Null": df[col].count(),
                        "Null": df[col].isna().sum(),
                    }
                )

            info_df = pd.DataFrame(info_data)
            session.output_adapter.display(
                data=info_df,
                title="Column Information",
                export=False,
                chart=False,
            )

    def call_view(self, other_args: list[str]):
        """Display current table."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="view",
            description="Display the current table.",
        )
        parser.add_argument(
            "--head",
            type=int,
            dest="head",
            help="Show only first N rows",
        )
        parser.add_argument(
            "--tail",
            type=int,
            dest="tail",
            help="Show only last N rows",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            if ns_parser.head:
                df = df.head(ns_parser.head)
            elif ns_parser.tail:
                df = df.tail(ns_parser.tail)

            session.output_adapter.display(
                data=df,
                title=f"Table: {self.current_table}",
                export=False,
                chart=False,
            )

    def call_query(self, other_args: list[str]):
        """Execute pandas query statement."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="query",
            description="Execute pandas operations on the current table. "
            "The current table is available as 'df'. "
            'Examples: query "df.query(\'REF_AREA == \\"CHE\\"\')" or query "df.groupby(\'REF_AREA\').mean()"',
        )
        parser.add_argument(
            "-s",
            "--save",
            action="store_true",
            help="Save the result back to the current table",
        )
        parser.add_argument(
            "expression",
            type=str,
            nargs=argparse.REMAINDER,
            help="Pandas expression - use 'df' to reference the current table",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return

            from openbb_cli.controllers.utils import SQLiteTable

            data_obj = (
                result.model_dump().get("results")
                if hasattr(result, "model_dump")
                else result
            )

            query_str = " ".join(ns_parser.expression).strip()

            if isinstance(data_obj, SQLiteTable):
                sql_query = None

                import re

                simple_filter = re.match(
                    r"df\[df\[['\"](\w+)['\"]\]\s*([><=!]+)\s*([^\]]+)\]", query_str
                )

                if simple_filter:
                    col_name = simple_filter.group(1)
                    operator = simple_filter.group(2)
                    value = simple_filter.group(3).strip()

                    sql_operator = operator
                    if operator == "==":
                        sql_operator = "="

                    if value.startswith(("'", '"')):
                        sql_value = value
                    else:
                        try:
                            sql_value = str(ast.literal_eval(value))  # noqa: S307
                            if (
                                not sql_value.replace(".", "")
                                .replace("-", "")
                                .isdigit()
                            ):
                                sql_value = f"'{sql_value}'"
                        except (ValueError, SyntaxError):
                            sql_value = f"'{value}'"

                    sql_query = f"{col_name} {sql_operator} {sql_value}"

                    try:
                        eval_result = data_obj.query(where=sql_query)

                        session.console.print(
                            f"[green]Query executed on database: {len(eval_result)} rows[/green]"
                        )

                        if ns_parser.save:
                            result.results = eval_result
                            session.console.print(
                                "[green]Table updated with result.[/green]"
                            )
                        else:
                            session.output_adapter.display(
                                data=eval_result,
                                title="Result (SQL optimized)",
                                export=False,
                                chart=False,
                            )
                        return
                    except Exception as sql_e:
                        session.console.print(
                            f"[yellow]SQL optimization failed: {sql_e}. Falling back to pandas.[/yellow]"
                        )

            df = extract_dataframe(result)

            try:
                namespace = {"df": df, "pd": pd}
                for col in df.columns:
                    namespace[col] = df[col]

                eval_result = eval(query_str, namespace)  # noqa: S307

                if isinstance(eval_result, pd.DataFrame):
                    if set(eval_result.columns) == set(df.columns) and len(
                        eval_result
                    ) != len(df):
                        session.console.print(
                            f"[green]Query result: {len(eval_result)} rows (from {len(df)})[/green]"
                        )

                    if ns_parser.save:
                        result.results = eval_result
                        session.console.print(
                            "[green]Table updated with result.[/green]"
                        )
                    else:
                        session.output_adapter.display(
                            data=eval_result,
                            title="Result",
                            export=False,
                            chart=False,
                        )
                elif isinstance(eval_result, pd.Series):
                    session.output_adapter.display(
                        data=eval_result.to_frame(),
                        title="Result",
                        export=False,
                        chart=False,
                    )
                elif (
                    isinstance(eval_result, (list, tuple, set))
                    or hasattr(eval_result, "__iter__")
                    and not isinstance(eval_result, str)
                ):
                    result_df = pd.DataFrame({query_str: list(eval_result)})
                    session.output_adapter.display(
                        data=result_df,
                        title="Result",
                        export=False,
                        chart=False,
                    )
                else:
                    session.console.print(f"\n[bold]Result:[/bold] {eval_result}")
            except Exception as e:
                error_msg = str(e)
                session.console.print(f"[red]Query error: {error_msg}[/red]")
                if "is not defined" in error_msg:
                    session.console.print(
                        "[yellow]Hint: For string comparisons, use quotes around values:[/yellow]\n"
                        '  [cyan]query "df.query(\'REF_AREA == \\"CHE\\"\')"[/cyan]'
                    )
                elif "invalid syntax" in error_msg:
                    session.console.print(
                        "[yellow]Hint: Valid query examples:[/yellow]\n"
                        '  [cyan]query "df.query(\'REF_AREA == \\"CHE\\"\')"[/cyan] (filter rows)\n'
                        "  [cyan]query \"df.query('VALUE > 100')\"[/cyan] (numeric filter)\n"
                        '  [cyan]query "df.query(\'REF_AREA == \\"CHE\\"\').pivot_table(...)"[/cyan] (chained)\n'
                        "  [cyan]query REF_AREA.unique()[/cyan] (column operation)"
                    )

    def call_colname(self, other_args: list[str]):
        """List all column names and their types."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="colname",
            description="List all columns with their data types.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            col_data = []
            for col in df.columns:
                col_data.append(
                    {
                        "Column": col,
                        "Type": str(df[col].dtype),
                    }
                )

            col_df = pd.DataFrame(col_data)
            session.output_adapter.display(
                data=col_df,
                title="Column Names and Types",
                export=False,
                chart=False,
            )

    def call_coltype(self, other_args: list[str]):
        """Change column data type."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="coltype",
            description="Change the data type of a column.",
        )
        parser.add_argument(
            "column",
            type=str,
            help="Column name",
        )
        parser.add_argument(
            "dtype",
            type=str,
            help="New data type (any valid pandas dtype: int64, float32, str, bool, datetime64[ns], category, etc.)",
        )
        parser.add_argument(
            "--categories",
            type=str,
            nargs="+",
            dest="categories",
            help="For category type: list of valid categories (space-separated)",
        )
        parser.add_argument(
            "--ordered",
            action="store_true",
            dest="ordered",
            help="For category type: whether categories are ordered",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            try:
                if "datetime" in ns_parser.dtype.lower():
                    df[ns_parser.column] = pd.to_datetime(df[ns_parser.column])
                elif ns_parser.dtype.lower() == "category":
                    if ns_parser.categories:
                        df[ns_parser.column] = pd.Categorical(
                            df[ns_parser.column],
                            categories=ns_parser.categories,
                            ordered=ns_parser.ordered,
                        )
                    else:
                        df[ns_parser.column] = df[ns_parser.column].astype("category")
                else:
                    df[ns_parser.column] = df[ns_parser.column].astype(ns_parser.dtype)

                result.results = df
                session.console.print(
                    f"[green]Changed column '{ns_parser.column}' to type '{df[ns_parser.column].dtype}'[/green]"
                )
            except Exception as e:
                session.console.print(f"[red]Error changing type: {str(e)}[/red]")

    def call_addcol(self, other_args: list[str]):
        """Add new column with expression."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="addcol",
            description="Add a new column to the current table using an expression.",
        )
        parser.add_argument(
            "name",
            type=str,
            help="Name of the new column",
        )
        parser.add_argument(
            "expression",
            type=str,
            nargs="+",
            help="Expression to create the column (e.g., 'col1 + col2')",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = result.to_dataframe()

            expr_str = " ".join(ns_parser.expression)

            try:
                df[ns_parser.name] = df.eval(expr_str)
                result.results = df
                session.console.print(
                    f"[green]Added column '{ns_parser.name}' with expression: {expr_str}[/green]"
                )
                self.update_completer(self.choices_default)
            except Exception as e:
                session.console.print(f"[red]Error adding column: {str(e)}[/red]")

    def call_dropcol(self, other_args: list[str]):
        """Drop column(s) from current table."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dropcol",
            description="Drop one or more columns from the current table.",
        )
        parser.add_argument(
            "columns",
            type=str,
            nargs="+",
            help="Column name(s) to drop",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            try:
                df = df.drop(columns=ns_parser.columns)
                result.results = df
                session.console.print(
                    f"[green]Dropped column(s): {', '.join(ns_parser.columns)}[/green]"
                )
                self.update_completer(self.choices_default)
            except Exception as e:
                session.console.print(f"[red]Error dropping column: {str(e)}[/red]")

    def call_renamecol(self, other_args: list[str]):
        """Rename a column."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="renamecol",
            description="Rename a column in the current table.",
        )
        parser.add_argument(
            "old_name",
            type=str,
            help="Current column name",
        )
        parser.add_argument(
            "new_name",
            type=str,
            help="New column name",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            try:
                df = df.rename(columns={ns_parser.old_name: ns_parser.new_name})
                result.results = df
                session.console.print(
                    f"[green]Renamed column '{ns_parser.old_name}' to '{ns_parser.new_name}'[/green]"
                )
                self.update_completer(self.choices_default)
            except Exception as e:
                session.console.print(f"[red]Error renaming column: {str(e)}[/red]")

    def call_modifycol(self, other_args: list[str]):
        """Modify column with expression."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="modifycol",
            description="Modify an existing column using an expression.",
        )
        parser.add_argument(
            "name",
            type=str,
            help="Name of the column to modify",
        )
        parser.add_argument(
            "expression",
            type=str,
            nargs="+",
            help="Expression to modify the column (e.g., 'col.astype(str)')",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            expr_str = " ".join(ns_parser.expression)

            try:
                if "." in expr_str and any(
                    method in expr_str
                    for method in ["astype", "str", "dt", "fillna", "replace"]
                ):
                    df[ns_parser.name] = eval(  # noqa: S307
                        f"df['{ns_parser.name}'].{expr_str}", {"df": df}
                    )
                else:
                    df[ns_parser.name] = df.eval(expr_str)
                result.results = df
                session.console.print(
                    f"[green]Modified column '{ns_parser.name}' with expression: {expr_str}[/green]"
                )
            except Exception as e:
                session.console.print(f"[red]Error modifying column: {str(e)}[/red]")

    def call_join(self, other_args: list[str]):
        """Join current table with another table."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="join",
            description="Join the current table with another table from cache.",
        )
        parser.add_argument(
            "table",
            type=str,
            help="Index or name of the table to join with",
        )
        parser.add_argument(
            "-o",
            "--on",
            type=str,
            dest="on",
            help="Column name(s) to join on (comma-separated)",
        )
        parser.add_argument(
            "-l",
            "--left-on",
            type=str,
            dest="left_on",
            help="Column name(s) in left table",
        )
        parser.add_argument(
            "-r",
            "--right-on",
            type=str,
            dest="right_on",
            help="Column name(s) in right table",
        )
        parser.add_argument(
            "-t",
            "--type",
            type=str,
            dest="how",
            default="inner",
            choices=["inner", "left", "right", "outer"],
            help="Type of join",
        )
        parser.add_argument(
            "-s",
            "--save",
            action="store_true",
            help="Save result to current table",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            table_idx = self._resolve_table_identifier(ns_parser.table)

            if table_idx is None:
                session.console.print(
                    f"[red]Table '{ns_parser.table}' not found in cache.[/red]"
                )
                return

            if table_idx not in session.obbject_registry.all:
                session.console.print(
                    f"[red]Table '{table_idx}' not found in cache.[/red]"
                )
                return

            result_left = session.obbject_registry.get(self.current_table)
            result_right = session.obbject_registry.get(table_idx)
            if result_left is None or result_right is None:
                return
            df_left = extract_dataframe(result_left)
            df_right = extract_dataframe(result_right)

            try:
                if ns_parser.on:
                    on_cols = [c.strip() for c in ns_parser.on.split(",")]
                    merged_df = pd.merge(
                        df_left, df_right, on=on_cols, how=ns_parser.how
                    )
                elif ns_parser.left_on and ns_parser.right_on:
                    left_cols = [c.strip() for c in ns_parser.left_on.split(",")]
                    right_cols = [c.strip() for c in ns_parser.right_on.split(",")]
                    merged_df = pd.merge(
                        df_left,
                        df_right,
                        left_on=left_cols,
                        right_on=right_cols,
                        how=ns_parser.how,
                    )
                else:
                    merged_df = pd.merge(
                        df_left,
                        df_right,
                        left_index=True,
                        right_index=True,
                        how=ns_parser.how,
                    )

                session.console.print(
                    f"[green]Join result: {len(merged_df)} rows, {len(merged_df.columns)} columns[/green]"
                )

                if ns_parser.save:
                    result_left.results = merged_df
                    session.console.print(
                        "[green]Table updated with join result.[/green]"
                    )
                else:
                    session.output_adapter.display(
                        data=merged_df.head(20),
                        title="Join Result (first 20 rows)",
                        export=False,
                        chart=False,
                    )

            except Exception as e:
                session.console.print(f"[red]Join error: {str(e)}[/red]")

    def call_copy(self, other_args: list[str]):
        """Copy current table to new name."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="copy",
            description="Copy the current table to a new index in cache.",
        )
        parser.add_argument(
            "name",
            type=str,
            help="Name/index for the new copy",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            from copy import deepcopy

            new_result = deepcopy(result)
            new_result.results = df.copy()
            import uuid

            new_result.id = str(uuid.uuid4())
            new_result.extra["command"] = f"copy from table {self.current_table}"
            new_result.extra["register_key"] = ns_parser.name

            if session.obbject_registry.register(new_result):
                session.console.print(
                    f"[green]Copied table '{self.current_table}' to '{ns_parser.name}'[/green]"
                )
            else:
                session.console.print("[red]Failed to register copied table.[/red]")
            self.update_completer(self.choices_default)

    def call_save(self, other_args: list[str]):
        """Save current table to file."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="save",
            description="Save the current table to a file.",
        )
        parser.add_argument(
            "filename",
            type=str,
            help="Filename to save (with extension: .csv, .json, .xlsx, .db, .sqlite)",
        )
        parser.add_argument(
            "-i",
            "--index",
            action="store_true",
            help="Include index in output",
        )
        parser.add_argument(
            "-t",
            "--table",
            type=str,
            default=None,
            help="Table name for SQLite databases (defaults to 'data')",
        )
        parser.add_argument(
            "-m",
            "--mode",
            type=str,
            choices=["replace", "append", "fail"],
            default="replace",
            help="Write mode: 'replace' (overwrite), 'append' (add rows), 'fail' (error if exists)",
        )
        parser.add_argument(
            "-s",
            "--sheet-name",
            type=str,
            default=None,
            help="Sheet name for Excel files (defaults to 'Sheet1')",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.current_table is None:
                session.console.print(
                    "[yellow]No table selected. Use 'select' command first.[/yellow]"
                )
                return

            result = session.obbject_registry.get(self.current_table)
            if result is None:
                return
            df = extract_dataframe(result)

            from pathlib import Path

            file_path = (
                Path(session.user.preferences.data_directory) / ns_parser.filename
            )

            try:
                if ns_parser.filename.endswith(".csv"):
                    df.to_csv(file_path, index=ns_parser.index)
                    session.console.print(f"[green]Saved table to {file_path}[/green]")
                elif ns_parser.filename.endswith(".json"):
                    df.to_json(file_path, orient="records", indent=2)
                    session.console.print(f"[green]Saved table to {file_path}[/green]")
                elif ns_parser.filename.endswith((".xlsx", ".xls")):
                    from openbb_cli.controllers.utils import save_to_excel

                    sheet_name = (
                        ns_parser.sheet_name if ns_parser.sheet_name else "Sheet1"
                    )
                    save_to_excel(
                        df=df,
                        saved_path=file_path,
                        sheet_name=sheet_name,
                        index=ns_parser.index,
                    )
                    session.console.print(
                        f"[green]Saved sheet '{sheet_name}' to {file_path}[/green]"
                    )
                elif ns_parser.filename.endswith((".db", ".sqlite", ".sqlite3")):
                    import sqlite3

                    table_name = ns_parser.table if ns_parser.table else "data"

                    file_exists = file_path.exists()

                    conn = sqlite3.connect(file_path)
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                            (table_name,),
                        )
                        table_exists = cursor.fetchone() is not None

                        if table_exists:
                            if ns_parser.mode == "fail":
                                session.console.print(
                                    f"[red]Table '{table_name}' already exists. Use --mode replace or --mode append[/red]"
                                )
                                return
                            elif ns_parser.mode == "replace":
                                session.console.print(
                                    f"[yellow]Table '{table_name}' exists. Replacing...[/yellow]"
                                )
                            elif ns_parser.mode == "append":
                                quoted_tbl = '"' + table_name.replace('"', '""') + '"'
                                cursor.execute(f"SELECT COUNT(*) FROM {quoted_tbl}")  # noqa: S608
                                old_count = cursor.fetchone()[0]
                                session.console.print(
                                    f"[cyan]Appending {len(df)} rows to existing {old_count} rows...[/cyan]"
                                )

                        df.to_sql(
                            table_name,
                            conn,
                            if_exists=ns_parser.mode,
                            index=ns_parser.index,
                        )

                        if table_exists and ns_parser.mode == "append":
                            cursor.execute(f"SELECT COUNT(*) FROM {quoted_tbl}")  # noqa: S608
                            new_count = cursor.fetchone()[0]
                            session.console.print(
                                f"[green]Appended {len(df)} rows. Table '{table_name}' now has {new_count} rows[/green]"
                            )
                        elif file_exists:
                            session.console.print(
                                f"[green]Saved table '{table_name}' ({len(df)} rows)"
                                f" to existing database {file_path}[/green]"
                            )
                        else:
                            session.console.print(
                                f"[green]Created new database and saved table"
                                f" '{table_name}' ({len(df)} rows) to {file_path}[/green]"
                            )
                    finally:
                        conn.close()
                else:
                    session.console.print(
                        "[red]Unsupported file format. Use .csv, .json, .xlsx, .db, .sqlite, or .sqlite3[/red]"
                    )
                    return
            except Exception as e:
                session.console.print(f"[red]Error saving file: {str(e)}[/red]")

    def call_delete(self, other_args: list[str]):
        """Delete table from cache."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="delete",
            description="Delete a table from the cache.",
        )
        parser.add_argument(
            "index",
            type=str,
            help="Index or name of the table to delete",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            table_idx = self._resolve_table_identifier(ns_parser.index)

            if table_idx is None:
                session.console.print(
                    f"[red]Table '{ns_parser.index}' not found in cache.[/red]"
                )
                return

            if table_idx in session.obbject_registry.all:
                session.obbject_registry.remove(table_idx)
                if self.current_table == table_idx:
                    self.current_table = None
                session.console.print(f"[green]Deleted table '{table_idx}'[/green]")
                self.update_completer(self.choices_default)
            else:
                session.console.print(
                    f"[red]Table '{ns_parser.index}' not found in cache.[/red]"
                )
