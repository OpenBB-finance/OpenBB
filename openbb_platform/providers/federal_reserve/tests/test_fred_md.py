"""Tests for the FRED-MD / FRED-QD series-description asset and helpers."""

import io
import json
import zipfile

from openbb_federal_reserve.utils import fred_md


def _zip(member: str, header: str, rows: list[str]) -> bytes:
    """Build an in-memory appendix zip with one cp1252-encoded CSV member."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        content = "\n".join([header, *rows])
        archive.writestr(member, content.encode("cp1252"))
    return buffer.getvalue()


_MD_ZIP = _zip(
    fred_md._MD_MEMBER,
    "id,tcode,fred,description,gsi,gsi:description,group",
    [
        "1,5,RPI,Real Personal  Income,M_1,PI,1",
        "2,5,IPB51222s,IP: Residential Utilities,M_2,IP,1",
        "3,6,CPIAUCSL,CPI: All Items,M_3,CPI,7",
        "4,5,,Blank mnemonic skipped,M_4,X,1",
    ],
)
_QD_ZIP = _zip(
    fred_md._QD_MEMBER,
    "ID,SW ID,TCODE,SW Factors,FRED MNEMONIC,SW MNEMONIC,DESCRIPTION,Group",
    ["1,1,5,0,GDPC1,GDP,Real Gross Domestic Product,1"],
)


class TestLoaders:
    """Tests for the committed-asset loaders and builders."""

    def test_load_descriptions_has_both_frequencies(self):
        """The asset exposes monthly and quarterly mnemonic maps."""
        data = fred_md.load_descriptions()
        assert set(data) == {"monthly", "quarterly"}
        assert data["monthly"]["RPI"] == "Real Personal Income"

    def test_series_options_pair_description_and_mnemonic(self):
        """Options carry the description as label and the mnemonic as value."""
        options = fred_md.series_options("monthly")
        assert {"label": "Real Personal Income", "value": "RPI"} in options
        assert len(options) == len(fred_md.load_descriptions()["monthly"])

    def test_columns_defs_lead_with_date_then_series(self):
        """Column defs start with the pinned date, then a header per series."""
        defs = fred_md.columns_defs("quarterly")
        assert defs[0]["field"] == "date"
        assert defs[0]["pinned"] == "left"
        series = defs[1:]
        assert all({"field", "headerName", "headerTooltip"} <= set(d) for d in series)
        fields = {d["field"] for d in series}
        assert fields == set(fred_md.load_descriptions()["quarterly"])


class TestAppendixParsing:
    """Tests for parsing and aligning the raw appendix tables."""

    def test_appendix_map_normalises_and_skips_blank(self):
        """Keys lower-case, whitespace collapses, and blank mnemonics are skipped."""
        out = fred_md._appendix_map(_MD_ZIP, fred_md._MD_MEMBER, "fred", "description")
        assert out["rpi"] == "Real Personal Income"
        assert out["ipb51222s"] == "IP: Residential Utilities"
        assert all(key for key in out)
        assert len(out) == 3

    def test_align_matches_case_insensitively_with_fallback(self):
        """Panel columns map to descriptions caselessly, falling back to the code."""
        appendix = {"rpi": "Real Personal Income", "ipb51222s": "IP: Residential"}
        aligned = fred_md._align("sasdate,RPI,IPB51222S,UNKNOWN", appendix)
        assert aligned == {
            "RPI": "Real Personal Income",
            "IPB51222S": "IP: Residential",
            "UNKNOWN": "UNKNOWN",
        }


class TestGenerate:
    """Tests for building the mapping from appendix bytes and panel headers."""

    def test_generate_with_injected_inputs(self):
        """Injected zips and panel headers build both frequency maps."""
        payload = fred_md.generate(
            md_bytes=_MD_ZIP,
            qd_bytes=_QD_ZIP,
            monthly_csv="sasdate,RPI,IPB51222S\n1/1/2024,1,2",
            quarterly_csv="sasdate,GDPC1\n1/1/2024,1",
        )
        assert payload["monthly"] == {
            "RPI": "Real Personal Income",
            "IPB51222S": "IP: Residential Utilities",
        }
        assert payload["quarterly"] == {"GDPC1": "Real Gross Domestic Product"}

    def test_generate_fetches_when_inputs_omitted(self, monkeypatch):
        """Omitted inputs are fetched from the St. Louis Fed sources."""
        from openbb_federal_reserve.utils import st_louis

        monkeypatch.setattr(
            st_louis,
            "fetch_bytes",
            lambda url: _MD_ZIP if "fred-md_appendix" in url else _QD_ZIP,
        )
        monkeypatch.setattr(
            st_louis,
            "fetch_fred_panel",
            lambda freq: (
                "sasdate,RPI\n1/1/2024,1"
                if freq == "monthly"
                else "sasdate,GDPC1\n1/1/2024,1"
            ),
        )
        payload = fred_md.generate()
        assert payload["monthly"] == {"RPI": "Real Personal Income"}
        assert payload["quarterly"] == {"GDPC1": "Real Gross Domestic Product"}


class TestWriteAsset:
    """Tests for the asset writer and CLI entry point."""

    def test_write_asset_writes_and_refreshes_cache(self, monkeypatch, tmp_path):
        """Writing the asset persists JSON and clears the load cache."""
        target = tmp_path / "fred_md" / "descriptions.json"
        monkeypatch.setattr(fred_md, "ASSET_PATH", target)
        fred_md.load_descriptions.cache_clear()
        path = fred_md.write_asset(
            md_bytes=_MD_ZIP,
            qd_bytes=_QD_ZIP,
            monthly_csv="sasdate,RPI\n1/1/2024,1",
            quarterly_csv="sasdate,GDPC1\n1/1/2024,1",
        )
        assert path == target
        assert (
            json.loads(target.read_text())["monthly"]["RPI"] == "Real Personal Income"
        )
        fred_md.load_descriptions.cache_clear()

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints the series counts."""
        target = tmp_path / "fred_md" / "descriptions.json"
        monkeypatch.setattr(fred_md, "ASSET_PATH", target)
        monkeypatch.setattr(
            fred_md,
            "generate",
            lambda **_: {"monthly": {"RPI": "Real Personal Income"}, "quarterly": {}},
        )
        fred_md.load_descriptions.cache_clear()
        fred_md._main()
        assert "monthly=1 quarterly=0" in capsys.readouterr().out
        fred_md.load_descriptions.cache_clear()


class TestCommittedAsset:
    """Sanity checks on the committed descriptions asset."""

    def test_counts_and_descriptions(self):
        """The asset carries the full panels with a non-empty description each."""
        data = fred_md.load_descriptions()
        assert len(data["monthly"]) == 126
        assert len(data["quarterly"]) == 245
        for series in data.values():
            for mnemonic, description in series.items():
                assert mnemonic.strip()
                assert description.strip()
