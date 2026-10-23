"""Tests for SQLiteTable and extract_dataframe in controllers/utils.py."""

import sqlite3
from unittest.mock import Mock

import pandas as pd
import pytest

from openbb_cli.controllers.utils import SQLiteTable, extract_dataframe


@pytest.fixture()
def sample_db(tmp_path):
    """Create a temporary SQLite database with a sample table."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE prices (date TEXT, close REAL, volume INTEGER)")
    cursor.executemany(
        "INSERT INTO prices VALUES (?, ?, ?)",
        [
            ("2024-01-01", 100.0, 1000),
            ("2024-01-02", 101.5, 1500),
            ("2024-01-03", 99.0, 1200),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


class TestSQLiteTable:
    """Tests for the SQLiteTable lazy-loading wrapper."""

    def test_init_stores_attributes(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices", row_count=3)
        assert t.db_path == sample_db
        assert t.table_name == "prices"
        assert t.row_count == 3
        assert t._cached_df is None

    def test_to_dataframe_returns_correct_data(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices", row_count=3)
        df = t.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["date", "close", "volume"]

    def test_to_dataframe_caches_by_default(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices", row_count=3)
        df1 = t.to_dataframe()
        df2 = t.to_dataframe()
        assert df1 is df2

    def test_to_dataframe_no_cache(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices", row_count=3)
        df1 = t.to_dataframe(use_cache=False)
        df2 = t.to_dataframe(use_cache=False)
        assert df1 is not df2
        assert t._cached_df is None

    def test_get_schema(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices")
        schema = t.get_schema()
        assert len(schema) == 3
        col_names = [row[1] for row in schema]
        assert col_names == ["date", "close", "volume"]

    def test_query_with_where(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices")
        df = t.query(where="close > 100")
        assert len(df) == 1
        assert df.iloc[0]["close"] == 101.5

    def test_query_with_limit(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices")
        df = t.query(limit=2)
        assert len(df) == 2

    def test_query_no_filters(self, sample_db):
        t = SQLiteTable(db_path=sample_db, table_name="prices")
        df = t.query()
        assert len(df) == 3

    def test_quoted_name_prevents_injection(self, tmp_path):
        """Table names with special chars are safely quoted."""
        db_path = str(tmp_path / "special.db")
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE "my table" (id INTEGER)')
        conn.execute('INSERT INTO "my table" VALUES (1)')
        conn.commit()
        conn.close()

        t = SQLiteTable(db_path=db_path, table_name="my table")
        df = t.to_dataframe()
        assert len(df) == 1


class TestExtractDataframe:
    """Tests for the extract_dataframe helper."""

    def test_obbject_with_list_results(self):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {
            "results": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        }
        df = extract_dataframe(mock_obj)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["a", "b"]

    def test_obbject_with_dict_results(self):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": {"x": 10, "y": 20}}
        df = extract_dataframe(mock_obj)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_obbject_with_dataframe_results(self):
        expected = pd.DataFrame({"col": [1, 2, 3]})
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": expected}
        df = extract_dataframe(mock_obj)
        pd.testing.assert_frame_equal(df, expected)

    def test_obbject_with_none_results(self):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": None}
        df = extract_dataframe(mock_obj)
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_obbject_with_scalar_results(self):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": 42}
        df = extract_dataframe(mock_obj)
        assert isinstance(df, pd.DataFrame)
        assert df.iloc[0]["value"] == 42

    def test_sqlite_table_results(self, sample_db):
        sqlite_table = SQLiteTable(db_path=sample_db, table_name="prices")
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": sqlite_table}
        df = extract_dataframe(mock_obj)
        assert len(df) == 3

    def test_non_obbject_passthrough_dict(self):
        data = {"a": [1, 2], "b": [3, 4]}
        df = extract_dataframe(data)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_non_obbject_passthrough_list(self):
        data = [{"a": 1}, {"a": 2}]
        df = extract_dataframe(data)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_non_obbject_passthrough_dataframe(self):
        expected = pd.DataFrame({"z": [5]})
        df = extract_dataframe(expected)
        pd.testing.assert_frame_equal(df, expected)
