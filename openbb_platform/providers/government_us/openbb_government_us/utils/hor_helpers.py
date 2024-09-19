from PyPDF2 import PdfReader
import zipfile
import io
import xml.etree.ElementTree as ET
import aiohttp
import asyncio

import pandas as pd
from typing import Any, List, Optional
from .hor_utils import extract_from_disclosure, extract_transactions

BASE_URL = "https://disclosures-clerk.house.gov/public_disc/financial-pdfs"
FINANCIAL_DOC_URL = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs"


def extract_docids_from_year_disclosures(res: io.BytesIO | None) -> List[dict]:
    """
    Extract disclosures information from an XML file
    :param res: an XML Stream
    :return:  a List of dictionaries containing doc_id, membername, state and date of transaction
    """
    if not res:
        return []
    xml_data = res
    # Parse the XML data from the BytesIO object
    tree = ET.parse(xml_data)
    root = tree.getroot()

    # Find all members with FilingType == "P" and extract their DocID
    doc_dictionary = []
    for member in root.findall("Member"):
        filing_type = member.find("FilingType").text
        if filing_type == "P":
            doc_id = member.find("DocID").text if member.find("DocID") else "N/A"
            if member.find("Last") and member.find("First"):
                membername = f"{member.find('Last').text} {member.find('First').text}"
            else:
                membername = "N/A"
            state = member.find("StateDst").text if member.find("StateDst") else "N/A"
            filing_date = member.find("FilingDate").text if member.find("FilingDate") else "N/A"
            doc_dictionary.append(
                dict(
                    doc_id=doc_id,
                    member=membername,
                    state=state,
                    filing_date=filing_date,
                )
            )
        else:
            pass
    return doc_dictionary


def get_all_docids(content):
    zip_file = io.BytesIO(content)
    xml_stream = None
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        for member in zip_ref.infolist():
            # there are two files the zip, an xml and a txt
            if member.filename.endswith(".xml"):
                xml_stream = io.BytesIO(zip_ref.read(member))

    return extract_docids_from_year_disclosures(xml_stream)


async def aextract_xml_from_zip_url(
    client: aiohttp.ClientSession, url: str, output_file: str
) -> List[dict]:
    """Extracts the XML file containing HOR disclosures for a specific year

    Args:
        url: The URL of the ZIP archive.
        output_file: The path to save the extracted XML file.
    Returns a dictionary of disclosures data containing
         - doc id
         - member name
         - state
         - filing date
         :param client:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }

    try:
        async with client.get(url, headers=headers) as response:
            # Download the ZIP file
            if response.status == 200:
                content = b""
                while True:
                    data = await response.content.read(1024)  # Read up to 1024 bytes
                    if not data:
                        break
                    content += data
        return get_all_docids(content)
    except Exception as e:
        raise Exception(f"Unable to get data from {url}:\n{str(e)}")


def extract_from_pdf(content):
    on_fly_mem_obj = io.BytesIO(content)
    pdf_reader = PdfReader(on_fly_mem_obj)
    return extract_from_disclosure(pdf_reader)


async def aread_pdf_from_url(
    client: aiohttp.ClientSession, year: int, discl_dict: dict
) -> pd.DataFrame:
    """
        Extract transactions from a pdf file
    :param client:  asyncio client
    :param year:  year of disclosures
    :param discl_dict: dictionary containing docid, member info, state etc
    :return:  a DataFrame of disclosures
    """
    disclosure_url = f"{FINANCIAL_DOC_URL}/{year}/{discl_dict['doc_id']}.pdf"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }

    try:

        async with client.get(disclosure_url, headers=headers, timeout=120) as response:
            if response.status == 200:
                content = b""
                while True:
                    data = await response.content.read(1024)  # Read up to 1024 bytes
                    if not data:
                        break
                    content += data

        data = extract_from_pdf(content)
        dfdata = extract_transactions(data["transactions"], discl_dict)
        if dfdata:
            return pd.DataFrame(data=dfdata)
        return pd.DataFrame()
    except Exception as e:
        raise Exception(f"Unable to fetch data from {disclosure_url}:\n{str(e)}")


async def fetch_all_transactions(
    session: aiohttp.ClientSession, year: int, reports: List[dict]
) -> pd.DataFrame:
    """

    :param session: async session
    :param year:   year of disclosures
    :param reports: a list of dictionaries containing information for each disclosures
    :return: a DataFrame of transactions
    """
    tasks = [aread_pdf_from_url(session, year, report) for report in reports]
    all_transactions = await asyncio.gather(*tasks)
    all_transactions_df = pd.concat(all_transactions, ignore_index=True)
    return all_transactions_df


async def get_transactions(year: int) -> pd.DataFrame:
    """
    Retrieve all HOR disclosures
    :param year: year of disclosures
    :return: a DataFrame containing all disclcosures
    """
    zip_name = f"{year}FD.zip"
    url = f"{BASE_URL}/{zip_name}"
    output_file = f"{year}.xml"
    session = aiohttp.ClientSession()
    reports = await aextract_xml_from_zip_url(session, url, output_file)
    all_transactions_df = await fetch_all_transactions(session, year, reports)
    return all_transactions_df.to_dict("records")
