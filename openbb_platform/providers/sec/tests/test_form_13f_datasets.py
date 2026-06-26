"""Unit tests for SEC Form 13F structured data set helpers."""

from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from openbb_sec.utils.form_13f_datasets import (
    HEADERS,
    Sec13FDataSet,
    download_13f_data_set,
    extract_13f_data_set_zip,
    filter_13f_data_sets,
    parse_13f_data_set_page,
)


def test_parse_13f_data_set_page_extracts_period_links_and_sizes() -> None:
    """The SEC data set listing parser extracts ZIP metadata."""
    html = """
    <html>
      <body>
        <table>
          <tr><th>Data Set</th><th>Size</th></tr>
          <tr>
            <td><a href="/files/form13fdata2024q4.zip">2024 Q4</a></td>
            <td>12.5 MB</td>
          </tr>
          <tr>
            <td><a href="https://www.sec.gov/files/form13fdata2013q2.zip">
              2013 Q2 Form 13F Data Set
            </a></td>
            <td>894 KB</td>
          </tr>
          <tr>
            <td>
              <a href="/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip">
                2026 March April May 13F
              </a>
            </td>
            <td>94.81 MB</td>
          </tr>
        </table>
      </body>
    </html>
    """

    data_sets = parse_13f_data_set_page(html, base_url="https://www.sec.gov")

    assert data_sets == [
        Sec13FDataSet(
            period_label="2024 Q4",
            url="https://www.sec.gov/files/form13fdata2024q4.zip",
            file_name="form13fdata2024q4.zip",
            size_text="12.5 MB",
            size_bytes=13_107_200,
            period_date=date(2024, 12, 31),
        ),
        Sec13FDataSet(
            period_label="2013 Q2 Form 13F Data Set",
            url="https://www.sec.gov/files/form13fdata2013q2.zip",
            file_name="form13fdata2013q2.zip",
            size_text="894 KB",
            size_bytes=915_456,
            period_date=date(2013, 6, 30),
        ),
        Sec13FDataSet(
            period_label="2026 March April May 13F",
            url=(
                "https://www.sec.gov/files/structureddata/data/"
                "form-13f-data-sets/01mar2026-31may2026_form13f.zip"
            ),
            file_name="01mar2026-31may2026_form13f.zip",
            size_text="94.81 MB",
            size_bytes=99_415_490,
            period_date=date(2026, 5, 31),
        ),
    ]


def test_filter_13f_data_sets_defaults_to_recent_five_year_window() -> None:
    """The default filter keeps recent data sets and drops unknown periods."""
    data_sets = [
        Sec13FDataSet(
            "2026 Q1",
            "https://example.test/2026q1.zip",
            "2026q1.zip",
            period_date=date(2026, 3, 31),
        ),
        Sec13FDataSet(
            "2021 Q2",
            "https://example.test/2021q2.zip",
            "2021q2.zip",
            period_date=date(2021, 6, 30),
        ),
        Sec13FDataSet(
            "2020 Q4",
            "https://example.test/2020q4.zip",
            "2020q4.zip",
            period_date=date(2020, 12, 31),
        ),
        Sec13FDataSet("Unknown", "https://example.test/unknown.zip", "unknown.zip"),
    ]

    filtered = filter_13f_data_sets(data_sets, as_of=date(2026, 6, 23))

    assert [item.period_label for item in filtered] == ["2026 Q1", "2021 Q2"]
    assert (
        filter_13f_data_sets(data_sets, as_of=date(2026, 6, 23), all_history=True)
        == data_sets
    )


def test_download_13f_data_set_skips_same_size_file(tmp_path: Path) -> None:
    """Existing files with the expected size are not downloaded again."""
    data_set = Sec13FDataSet(
        period_label="2024 Q4",
        url="https://example.test/form13fdata2024q4.zip",
        file_name="form13fdata2024q4.zip",
        size_bytes=4,
    )
    target = tmp_path / data_set.file_name
    target.write_bytes(b"same")

    downloaded = download_13f_data_set(data_set, tmp_path)

    assert downloaded == target
    assert target.read_bytes() == b"same"


def test_download_13f_data_set_writes_response_content_when_forced(
    tmp_path: Path,
) -> None:
    """Forced downloads overwrite cached raw ZIPs."""
    data_set = Sec13FDataSet(
        period_label="2024 Q4",
        url="https://example.test/form13fdata2024q4.zip",
        file_name="form13fdata2024q4.zip",
        size_bytes=4,
    )
    target = tmp_path / data_set.file_name
    target.write_bytes(b"old!")

    class Response:
        content = b"new!"

        def raise_for_status(self) -> None:
            return None

    with patch(
        "openbb_sec.utils.form_13f_datasets.sec_make_request",
        return_value=Response(),
    ) as request:
        downloaded = download_13f_data_set(data_set, tmp_path, force=True)

    assert downloaded == target
    assert target.read_bytes() == b"new!"
    request.assert_called_once_with(
        data_set.url,
        headers=HEADERS,
        timeout=60,
    )


def test_extract_13f_data_set_zip_normalizes_filers_and_holdings(
    tmp_path: Path,
) -> None:
    """ZIP extraction normalizes submission and information table members."""
    zip_path = tmp_path / "form13fdata2024q4.zip"
    submission_tsv = "\t".join(
        [
            "ACCESSION_NUMBER",
            "CIK",
            "FILINGMANAGER_NAME",
            "REPORTCALENDARORQUARTER",
            "DATEFILED",
        ]
    )
    submission_tsv += "\n0001\t0001000275\tAcme Capital LP\t12-31-2024\t2025-02-14\n"
    info_tsv = "\t".join(
        [
            "ACCESSION_NUMBER",
            "NAMEOFISSUER",
            "CUSIP",
            "VALUE",
            "SSHPRNAMT",
            "SECTOR",
        ]
    )
    info_tsv += "\n0001\tApple Inc\t037833100\t750\t10\tTechnology\n"
    info_tsv += "0001\tMicrosoft Corp\t594918104\t250\t5\tTechnology\n"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as fixture:
        fixture.writestr("SUBMISSION.tsv", submission_tsv)
        fixture.writestr("INFOTABLE.tsv", info_tsv)

    extracted = extract_13f_data_set_zip(zip_path)

    assert extracted.filers == [
        {
            "accession_number": "0001",
            "cik": "0001000275",
            "name": "Acme Capital LP",
            "period_date": date(2024, 12, 31),
            "filed_date": date(2025, 2, 14),
        }
    ]
    assert extracted.holdings == [
        {
            "accession_number": "0001",
            "cik": "0001000275",
            "filer_name": "Acme Capital LP",
            "issuer": "Apple Inc",
            "cusip": "037833100",
            "value": 750.0,
            "shares": 10.0,
            "weight": 0.75,
            "sector": "Technology",
            "period_date": date(2024, 12, 31),
        },
        {
            "accession_number": "0001",
            "cik": "0001000275",
            "filer_name": "Acme Capital LP",
            "issuer": "Microsoft Corp",
            "cusip": "594918104",
            "value": 250.0,
            "shares": 5.0,
            "weight": 0.25,
            "sector": "Technology",
            "period_date": date(2024, 12, 31),
        },
    ]


def test_extract_13f_data_set_zip_merges_submission_and_coverpage(
    tmp_path: Path,
) -> None:
    """ZIP extraction merges current SEC submission and cover page members."""
    zip_path = tmp_path / "2023q4_form13f.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as fixture:
        fixture.writestr(
            "SUBMISSION.tsv",
            "ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tCIK\tPERIODOFREPORT\n"
            "0000051762-23-000005\t31-OCT-2023\t13F-HR\t0000051762\t30-SEP-2023\n",
        )
        fixture.writestr(
            "COVERPAGE.tsv",
            "ACCESSION_NUMBER\tREPORTCALENDARORQUARTER\tFILINGMANAGER_NAME\n"
            "0000051762-23-000005\t30-SEP-2023\tRNC CAPITAL MANAGEMENT LLC\n",
        )
        fixture.writestr(
            "INFOTABLE.tsv",
            "ACCESSION_NUMBER\tNAMEOFISSUER\tCUSIP\tVALUE\tSSHPRNAMT\n"
            "0000051762-23-000005\tABBOTT LABORATORIES\t002824100\t1515058\t15643\n",
        )

    extracted = extract_13f_data_set_zip(zip_path)

    assert extracted.filers == [
        {
            "accession_number": "0000051762-23-000005",
            "cik": "0000051762",
            "name": "RNC CAPITAL MANAGEMENT LLC",
            "period_date": date(2023, 9, 30),
            "filed_date": date(2023, 10, 31),
        }
    ]
    assert extracted.holdings == [
        {
            "accession_number": "0000051762-23-000005",
            "cik": "0000051762",
            "filer_name": "RNC CAPITAL MANAGEMENT LLC",
            "issuer": "ABBOTT LABORATORIES",
            "cusip": "002824100",
            "value": 1515058.0,
            "shares": 15643.0,
            "weight": 1.0,
            "sector": None,
            "period_date": date(2023, 9, 30),
        }
    ]


def test_extract_13f_data_set_zip_handles_csv_member_aliases(
    tmp_path: Path,
) -> None:
    """CSV member aliases are accepted for local fixtures and SEC variants."""
    zip_path = tmp_path / "form13fdata2024q4.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as fixture:
        fixture.writestr(
            "submission.csv",
            "accession_number,cik,filer_name,period,filed_date\n"
            "0002,0002000000,Example Advisors,2024-12-31,2025-02-13\n",
        )
        fixture.writestr(
            "information_table.csv",
            "accession_number,issuer,cusip,value,shares\n"
            "0002,Nvidia Corp,67066G104,1000,2\n",
        )

    extracted = extract_13f_data_set_zip(zip_path)

    assert extracted.filers[0]["name"] == "Example Advisors"
    assert extracted.holdings[0]["issuer"] == "Nvidia Corp"
    assert extracted.holdings[0]["weight"] == 1.0
    assert extracted.holdings[0]["sector"] is None


def test_extract_13f_data_set_zip_rejects_missing_required_members(
    tmp_path: Path,
) -> None:
    """Missing submission or information table members fail fast."""
    zip_path = tmp_path / "bad.zip"
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as fixture:
        fixture.writestr("README.txt", "missing tabular data")
    zip_path.write_bytes(buffer.getvalue())

    with pytest.raises(ValueError, match="submission.*information table"):
        extract_13f_data_set_zip(zip_path)
