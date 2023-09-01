from typing import List, Optional, Union

import pandas as pd
from openbb_charting.core.openbb_figure import OpenBBFigure


class OpenBBFigureTable(OpenBBFigure):
    def __init__(
        self,
        tabular_data: pd.DataFrame,
        columnwidth: Optional[List[Union[int, float]]] = None,
    ):
        super().__init__()
        self._tabular_data = tabular_data
        self._columnwidth = columnwidth

    def show(
        self,
        show_index: Optional[bool] = True,
        index_name: Optional[str] = "",
        headers: Optional[Union[List[str], pd.Index]] = None,
        title: Optional[str] = "",
        source: Optional[str] = "",
        external: Optional[bool] = False,
    ) -> Optional["OpenBBFigureTable"]:
        if external:
            return self

        if not self._backend.isatty:
            tmp_fig = self.to_table()
            tmp_fig.show()
            return None
        else:
            # Make a copy of the dataframe to avoid SettingWithCopyWarning
            df = self._tabular_data.copy()

            show_index = not isinstance(df.index, pd.RangeIndex) and show_index
            #  convert non-str that are not timestamp or int into str
            # eg) praw.models.reddit.subreddit.Subreddit
            for col in df.columns:
                try:
                    if not any(
                        isinstance(df[col].iloc[x], pd.Timestamp)
                        for x in range(min(10, len(df)))
                    ):
                        df[col] = pd.to_numeric(df[col], errors="ignore")
                except (ValueError, TypeError):
                    df[col] = df[col].astype(str)

            def _get_headers(_headers: Union[List[str], pd.Index]) -> List[str]:
                """Check if headers are valid and return them."""
                output = _headers
                if isinstance(_headers, pd.Index):
                    output = list(_headers)
                if len(output) != len(df.columns):
                    raise (
                        ValueError(
                            "Length of headers does not match length of DataFrame"
                        )
                    )
                return output

            df_outgoing = df.copy()
            # If headers are provided, use them
            if headers is not None:
                # We check if headers are valid
                df_outgoing.columns = _get_headers(headers)

            if show_index and index_name not in df_outgoing.columns:
                # If index name is provided, we use it
                df_outgoing.index.name = index_name or "Index"
                df_outgoing = df_outgoing.reset_index()

            for col in df_outgoing.columns:
                if not col:
                    df_outgoing = df_outgoing.rename(columns={col: "  "})

            self._backend.send_table(
                df_table=df_outgoing,
                title=title,
                source=source,  # type: ignore
                theme=self._charting_settings.table_style,
            )

            return None

    def to_table(
        self,
        print_index: bool = True,
        **kwargs,
    ) -> "OpenBBFigure":
        data = self._tabular_data
        columnwidth = self._columnwidth

        return super().to_table(data, columnwidth, print_index, **kwargs)
