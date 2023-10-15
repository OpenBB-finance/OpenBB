"""SEC Helpers module"""
from datetime import timedelta
from typing import Literal

import pandas as pd
import requests
import requests_cache

sec_session_companies = requests_cache.CachedSession(
    "OpenBB_SEC_Companies", expire_after=timedelta(days=7), use_cache_dir=True
)


SEC_HEADERS = {
    "User-Agent": "my real company name definitelynot@fakecompany.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov",
}


FORM_TYPES = Literal[
    "1",
    "1-A",
    "1-A POS",
    "1-A-W",
    "1-E",
    "1-E AD",
    "1-K",
    "1-SA",
    "1-U",
    "1-Z",
    "1-Z-W",
    "10-12B",
    "10-12G",
    "10-D",
    "10-K",
    "10-KT",
    "10-Q",
    "10-QT",
    "11-K",
    "11-KT",
    "13F-HR",
    "13F-NT",
    "13FCONP",
    "144",
    "15-12B",
    "15-12G",
    "15-15D",
    "15F-12B",
    "15F-12G",
    "15F-15D",
    "18-12B",
    "18-K",
    "19B-4E",
    "2-A",
    "2-AF",
    "2-E",
    "20-F",
    "20FR12B",
    "20FR12G",
    "24F-2NT",
    "25",
    "25-NSE",
    "253G1",
    "253G2",
    "253G3",
    "253G4",
    "3",
    "305B2",
    "34-12H",
    "4",
    "40-17F1",
    "40-17F2",
    "40-17G",
    "40-17GCS",
    "40-202A",
    "40-203A",
    "40-206A",
    "40-24B2",
    "40-33",
    "40-6B",
    "40-8B25",
    "40-8F-2",
    "40-APP",
    "40-F",
    "40-OIP",
    "40FR12B",
    "40FR12G",
    "424A",
    "424B1",
    "424B2",
    "424B3",
    "424B4",
    "424B5",
    "424B7",
    "424B8",
    "424H",
    "425",
    "485APOS",
    "485BPOS",
    "485BXT",
    "486APOS",
    "486BPOS",
    "486BXT",
    "487",
    "497",
    "497AD",
    "497H2",
    "497J",
    "497K",
    "497VPI",
    "497VPU",
    "5",
    "6-K",
    "6B NTC",
    "6B ORDR",
    "8-A12B",
    "8-A12G",
    "8-K",
    "8-K12B",
    "8-K12G3",
    "8-K15D5",
    "8-M",
    "8F-2 NTC",
    "8F-2 ORDR",
    "9-M",
    "ABS-15G",
    "ABS-EE",
    "ADN-MTL",
    "ADV-E",
    "ADV-H-C",
    "ADV-H-T",
    "ADV-NR",
    "ANNLRPT",
    "APP NTC",
    "APP ORDR",
    "APP WD",
    "APP WDG",
    "ARS",
    "ATS-N",
    "ATS-N-C",
    "ATS-N/UA",
    "AW",
    "AW WD",
    "C",
    "C-AR",
    "C-AR-W",
    "C-TR",
    "C-TR-W",
    "C-U",
    "C-U-W",
    "C-W",
    "CB",
    "CERT",
    "CERTARCA",
    "CERTBATS",
    "CERTCBO",
    "CERTNAS",
    "CERTNYS",
    "CERTPAC",
    "CFPORTAL",
    "CFPORTAL-W",
    "CORRESP",
    "CT ORDER",
    "D",
    "DEF 14A",
    "DEF 14C",
    "DEFA14A",
    "DEFA14C",
    "DEFC14A",
    "DEFC14C",
    "DEFM14A",
    "DEFM14C",
    "DEFN14A",
    "DEFR14A",
    "DEFR14C",
    "DEL AM",
    "DFAN14A",
    "DFRN14A",
    "DOS",
    "DOSLTR",
    "DRS",
    "DRSLTR",
    "DSTRBRPT",
    "EFFECT",
    "F-1",
    "F-10",
    "F-10EF",
    "F-10POS",
    "F-1MEF",
    "F-3",
    "F-3ASR",
    "F-3D",
    "F-3DPOS",
    "F-3MEF",
    "F-4",
    "F-4 POS",
    "F-4MEF",
    "F-6",
    "F-6 POS",
    "F-6EF",
    "F-7",
    "F-7 POS",
    "F-8",
    "F-8 POS",
    "F-80",
    "F-80POS",
    "F-9",
    "F-9 POS",
    "F-N",
    "F-X",
    "FOCUSN",
    "FWP",
    "G-405",
    "G-405N",
    "G-FIN",
    "G-FINW",
    "IRANNOTICE",
    "MA",
    "MA-A",
    "MA-I",
    "MA-W",
    "MSD",
    "MSDCO",
    "MSDW",
    "N-1",
    "N-14",
    "N-14 8C",
    "N-14MEF",
    "N-18F1",
    "N-1A",
    "N-2",
    "N-2 POSASR",
    "N-23C-2",
    "N-23C3A",
    "N-23C3B",
    "N-23C3C",
    "N-2ASR",
    "N-2MEF",
    "N-30B-2",
    "N-30D",
    "N-4",
    "N-5",
    "N-54A",
    "N-54C",
    "N-6",
    "N-6F",
    "N-8A",
    "N-8B-2",
    "N-8F",
    "N-8F NTC",
    "N-8F ORDR",
    "N-CEN",
    "N-CR",
    "N-CSR",
    "N-CSRS",
    "N-MFP",
    "N-MFP1",
    "N-MFP2",
    "N-PX",
    "N-Q",
    "N-VP",
    "N-VPFS",
    "NO ACT",
    "NPORT-EX",
    "NPORT-NP",
    "NPORT-P",
    "NRSRO-CE",
    "NRSRO-UPD",
    "NSAR-A",
    "NSAR-AT",
    "NSAR-B",
    "NSAR-BT",
    "NSAR-U",
    "NT 10-D",
    "NT 10-K",
    "NT 10-Q",
    "NT 11-K",
    "NT 20-F",
    "NT N-CEN",
    "NT N-MFP",
    "NT N-MFP1",
    "NT N-MFP2",
    "NT NPORT-EX",
    "NT NPORT-P",
    "NT-NCEN",
    "NT-NCSR",
    "NT-NSAR",
    "NTFNCEN",
    "NTFNCSR",
    "NTFNSAR",
    "NTN 10D",
    "NTN 10K",
    "NTN 10Q",
    "NTN 20F",
    "OIP NTC",
    "OIP ORDR",
    "POS 8C",
    "POS AM",
    "POS AMI",
    "POS EX",
    "POS462B",
    "POS462C",
    "POSASR",
    "PRE 14A",
    "PRE 14C",
    "PREC14A",
    "PREC14C",
    "PREM14A",
    "PREM14C",
    "PREN14A",
    "PRER14A",
    "PRER14C",
    "PRRN14A",
    "PX14A6G",
    "PX14A6N",
    "QRTLYRPT",
    "QUALIF",
    "REG-NR",
    "REVOKED",
    "RW",
    "RW WD",
    "S-1",
    "S-11",
    "S-11MEF",
    "S-1MEF",
    "S-20",
    "S-3",
    "S-3ASR",
    "S-3D",
    "S-3DPOS",
    "S-3MEF",
    "S-4",
    "S-4 POS",
    "S-4EF",
    "S-4MEF",
    "S-6",
    "S-8",
    "S-8 POS",
    "S-B",
    "S-BMEF",
    "SBSE",
    "SBSE-A",
    "SBSE-BD",
    "SBSE-C",
    "SBSE-W",
    "SC 13D",
    "SC 13E1",
    "SC 13E3",
    "SC 13G",
    "SC 14D9",
    "SC 14F1",
    "SC 14N",
    "SC TO-C",
    "SC TO-I",
    "SC TO-T",
    "SC13E4F",
    "SC14D1F",
    "SC14D9C",
    "SC14D9F",
    "SD",
    "SDR",
    "SE",
    "SEC ACTION",
    "SEC STAFF ACTION",
    "SEC STAFF LETTER",
    "SF-1",
    "SF-3",
    "SL",
    "SP 15D2",
    "STOP ORDER",
    "SUPPL",
    "T-3",
    "TA-1",
    "TA-2",
    "TA-W",
    "TACO",
    "TH",
    "TTW",
    "UNDER",
    "UPLOAD",
    "WDL-REQ",
    "X-17A-5",
]


def get_all_companies(use_cache: bool = True) -> pd.DataFrame:
    """Gets all company names, tickers, and CIK numbers registered with the SEC.
    Companies are sorted by market cap.

    Returns
    -------
    pd.DataFrame: Pandas DataFrame with columns for Symbol, Company Name, and CIK Number.

    Example
    -------
    >>> tickers = get_all_companies()
    """

    url = "https://www.sec.gov/files/company_tickers.json"

    r = (
        sec_session_companies.get(url, headers=SEC_HEADERS, timeout=5)
        if use_cache is True
        else requests.get(url, headers=SEC_HEADERS, timeout=5)
    )
    df = pd.DataFrame(r.json()).transpose()
    cols = ["cik", "symbol", "name"]
    df.columns = cols
    return df.astype(str)


def get_all_ciks(use_cache: bool = True) -> pd.DataFrame:
    """Gets a list of entity names and their CIK number."""

    HEADERS = {
        "User-Agent": "my real company name definitelynot@fakecompany.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
    }
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    r = (
        sec_session_companies.get(url, headers=HEADERS, timeout=5)
        if use_cache is True
        else requests.get(url, headers=HEADERS, timeout=5)
    )
    data = r.text
    lines = data.split("\n")
    data_list = []
    delimiter = ":"
    for line in lines:
        row = line.split(delimiter)
        data_list.append(row)
    df = pd.DataFrame(data_list)
    df = df.iloc[:, 0:2]
    cols = ["Institution", "CIK Number"]
    df.columns = cols
    df = df.dropna()

    return df


def search_institutions(keyword: str) -> pd.DataFrame:
    """Search for an institution by name.  It is case-insensitive."""
    institutions = get_all_ciks()
    hp = institutions["Institution"].str.contains(keyword, case=False)
    return institutions[hp]


def symbol_map(symbol: str, use_cache: bool = True) -> str:
    """Returns the CIK number of a ticker symbol for querying the SEC API."""

    symbol = symbol.upper().replace(".", "-")
    symbols = get_all_companies(use_cache=use_cache)

    if symbol not in symbols["symbol"].to_list():
        return ""

    cik = symbols[symbols["symbol"] == symbol]["cik"].iloc[0]
    cik_: str = ""
    temp = 10 - len(cik)
    for i in range(temp):
        cik_ = cik_ + "0"

    return str(cik_ + cik)


def catching_diff_url_formats(ftd_urls: list) -> list:
    """Catches if URL for SEC data is one of the few URLS that are not in the
    standard format. Catches are for either specific date ranges that have a different
    format or singular URLs that have a different format.

    Parameters
    ----------
    ftd_urls : list
        list of urls of sec data

    Returns
    -------
    list
        list of ftd urls
    """
    feb_mar_apr_catch = ["202002", "202003", "202004"]
    for i, ftd_url in enumerate(ftd_urls):
        # URLs with dates prior to the first half of June 2017 have different formats
        if int(ftd_url[58:64]) < 201706 or "201706a" in ftd_url:
            ftd_urls[i] = ftd_url.replace(
                "fails-deliver-data",
                "frequently-requested-foia-document-fails-deliver-data",
            )
        # URLs between february, march, and april of 2020 have different formats
        elif any(x in ftd_urls[i] for x in feb_mar_apr_catch):
            ftd_urls[i] = ftd_url.replace(
                "data/fails-deliver-data", "node/add/data_distribution"
            )
        # First half of october 2019 has a different format
        elif (
            ftd_url
            == "https://www.sec.gov/files/data/fails-deliver-data/cnsfails201910a.zip"
        ):
            ftd_urls[
                i
            ] = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails201910a_0.zip"

    return ftd_urls
