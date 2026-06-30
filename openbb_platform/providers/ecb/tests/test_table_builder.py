"""Unit tests for ``openbb_ecb.utils.table_builder``."""

import asyncio

from openbb_ecb.utils import query_builder
from openbb_ecb.utils.table_builder import _flatten, build_presentation_table

_STRUCTURE = [
    {
        "label": "Assets",
        "code": "L1",
        "codelist_id": "JDF_ROW_LABELS",
        "dimension_id": None,
        "children": [
            {
                "label": "Loans",
                "code": "A20",
                "codelist_id": "CL_ITEM",
                "dimension_id": "ITEM",
                "children": [
                    {
                        "label": "MFI",
                        "code": "1000",
                        "codelist_id": "CL_SEC",
                        "dimension_id": "SECTOR",
                        "children": [],
                    },
                    {
                        "label": "HH",
                        "code": "2250",
                        "codelist_id": "CL_SEC",
                        "dimension_id": "SECTOR",
                        "children": [],
                    },
                ],
            }
        ],
    }
]
_DIMS = [{"id": "FREQ"}, {"id": "ITEM"}, {"id": "SECTOR"}]


class _FakeMeta:
    """Minimal metadata surface used by ``build_presentation_table``."""

    def __init__(self, structure, dims):
        self._structure = structure
        self._dims = dims

    def get_table(self, table_id):
        return {"dataflow_id": "TST"}

    def get_table_structure(self, table_id):
        return self._structure

    def get_dataflow_dimensions(self, dataflow_id):
        return self._dims


def test_flatten_overrides_deepest_code():
    """The deepest code wins for a repeated dimension along the path."""
    structure = [
        {
            "label": "a",
            "code": "A20",
            "codelist_id": "CL_ITEM",
            "dimension_id": "ITEM",
            "children": [
                {
                    "label": "b",
                    "code": "A21",
                    "codelist_id": "CL_ITEM",
                    "dimension_id": "ITEM",
                    "children": [],
                }
            ],
        }
    ]
    rows, node_paths, table_dim_codes = _flatten(structure)
    assert [r["label"] for r in rows] == ["a", "b"]
    assert node_paths[1][1] == {"ITEM": "A21"}  # child overrides parent
    assert table_dim_codes == {"ITEM": {"A20", "A21"}}


def test_build_presentation_table(monkeypatch):
    """Series are fetched, matched to rows, and pivoted into indented title rows."""
    captured = {}

    async def _fetch(flow_ref, key, **kwargs):
        captured["flow"] = flow_ref
        captured["key"] = key
        captured["last_n"] = kwargs.get("last_n")
        return [
            {"ITEM": "A20", "SECTOR": "1000", "OBS_VALUE": 9.0, "date": "2024-01-01"},
            {"ITEM": "A20", "SECTOR": "1000", "OBS_VALUE": 8.0, "date": "2023-10-01"},
            {"ITEM": "A20", "SECTOR": "2250", "OBS_VALUE": 6.0, "date": "2024-01-01"},
            {"ITEM": "A20", "SECTOR": "9999", "OBS_VALUE": 1.0, "date": "2024-01-01"},
            {"ITEM": "A20", "SECTOR": "1000", "OBS_VALUE": None, "date": None},
        ]

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)
    meta = _FakeMeta(_STRUCTURE, _DIMS)
    # ITEM is supplied in context too, exercising the union in the key builder.
    rows = asyncio.run(
        build_presentation_table(
            meta, "T", {"FREQ": "M", "ITEM": "A20"}, use_cache=False, limit=4
        )
    )

    assert captured["flow"] == "TST"
    assert captured["key"] == "M.A20.1000+2250"
    assert captured["last_n"] == 4  # the period limit flows through to the fetch

    def find(label):
        return next(r for r in rows if r["title"].endswith(label))

    # Each row is a `title` (indented by hierarchy level) plus one column per
    # observed period, latest first.
    mfi = find("MFI")
    assert mfi["2024-01-01"] == 9.0 and mfi["2023-10-01"] == 8.0
    assert [k for k in mfi if k != "title"] == ["2024-01-01", "2023-10-01"]
    assert find("HH")["2024-01-01"] == 6.0
    # Level-2 rows are indented; the pure header is not and carries no values.
    assert mfi["title"].startswith(">")
    assert find("Assets")["title"] == "Assets"
    assert find("Assets")["2024-01-01"] is None
    assert find("Loans")["2024-01-01"] is None
