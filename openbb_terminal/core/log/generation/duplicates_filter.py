# IMPORTATION STANDARD
import logging
from pathlib import Path

# IMPORTATION THIRDPARTY
import pandas as pd

# IMPORTATION INTERNAL


class DuplicatesFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._log_path = Path(logging.getLogger().handlers[0].baseFilename)

    @staticmethod
    def _get_log_df(path: Path) -> pd.DataFrame:
        if path.stat().st_size == 0:
            return pd.DataFrame()
        return pd.read_csv(path, sep="|", header=None)

    @staticmethod
    def _check_message_in_df(
        df: pd.DataFrame,
        record: logging.LogRecord,
    ) -> bool:
        if df.empty:
            return True

        res_message = record.__dict__.get("msg") not in df.iloc[:, -1].values
        res_line = record.__dict__.get("lineno") not in df.iloc[:, -2].values
        res_filename = (
            record.__dict__.get("func_name_override") not in df.iloc[:, -4].values
        )
        res_func_name = record.__dict__.get("filename") not in df.iloc[:, -3].values

        return res_message and res_line and res_filename and res_func_name

    def filter(self, record: logging.LogRecord) -> bool:
        df = self._get_log_df(path=self._log_path)
        return self._check_message_in_df(df=df, record=record)
