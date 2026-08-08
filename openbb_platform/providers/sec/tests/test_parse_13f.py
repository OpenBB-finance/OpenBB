"""Test parsing of SEC Form 13F-HR Complete Submission TXT files."""

import pytest
from bs4 import BeautifulSoup
from openbb_sec.utils.parse_13f import parse_13f_hr, prepare_13f_xml

# A Complete Submission TXT file is SGML-wrapped and not well-formed XML, so
# soup-ing it directly makes lxml fall back to recover mode, which silently
# drops character entities such as '&amp;'. This fixture reproduces that
# envelope, including '&' in element text and in an attribute value.
SGML_FILING = """<SEC-DOCUMENT>0001234567-26-000001.txt : 20260401
<SEC-HEADER>0001234567-26-000001.hdr.sgml : 20260401
<ACCESSION-NUMBER>0001234567-26-000001
<TYPE>13F-HR
</SEC-HEADER>
<DOCUMENT>
<TYPE>13F-HR
<SEQUENCE>1
<XML>
<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission>
<headerData>
<submissionType>13F-HR</submissionType>
<filerInfo>
<periodOfReport>03-31-2026</periodOfReport>
</filerInfo>
</headerData>
</edgarSubmission>
</XML>
</DOCUMENT>
<DOCUMENT>
<TYPE>INFORMATION TABLE
<SEQUENCE>2
<XML>
<?xml version="1.0" encoding="UTF-8"?>
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
<infoTable audit="S&amp;P holdings">
<nameOfIssuer>S&amp;P500 EQL WGT</nameOfIssuer>
<titleOfClass>COM</titleOfClass>
<cusip>123456789</cusip>
<value>1000</value>
<shrsOrPrnAmt>
<sshPrnamt>500</sshPrnamt>
<sshPrnamtType>SH</sshPrnamtType>
</shrsOrPrnAmt>
<investmentDiscretion>SOLE</investmentDiscretion>
<votingAuthority>
<Sole>500</Sole>
<Shared>0</Shared>
<None>0</None>
</votingAuthority>
</infoTable>
<infoTable>
<nameOfIssuer>BABCOCK &amp; WILCOX ENTERPRISES</nameOfIssuer>
<titleOfClass>COM</titleOfClass>
<cusip>987654321</cusip>
<value>2000</value>
<shrsOrPrnAmt>
<sshPrnamt>800</sshPrnamt>
<sshPrnamtType>SH</sshPrnamtType>
</shrsOrPrnAmt>
<investmentDiscretion>SOLE</investmentDiscretion>
<votingAuthority>
<Sole>800</Sole>
<Shared>0</Shared>
<None>0</None>
</votingAuthority>
</infoTable>
</informationTable>
</XML>
</DOCUMENT>
</SEC-DOCUMENT>
"""

# Well-formed XML with no SGML <XML> wrappers — prepare_13f_xml must leave this
# unchanged and parse_13f_hr must still succeed.
PLAIN_XML_FILING = """<?xml version="1.0" encoding="UTF-8"?>
<root>
<headerData>
<submissionType>13F-HR</submissionType>
<filerInfo>
<periodOfReport>03-31-2026</periodOfReport>
</filerInfo>
</headerData>
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
<infoTable>
<nameOfIssuer>S&amp;P500 EQL WGT</nameOfIssuer>
<titleOfClass>COM</titleOfClass>
<cusip>123456789</cusip>
<value>1000</value>
<shrsOrPrnAmt>
<sshPrnamt>500</sshPrnamt>
<sshPrnamtType>SH</sshPrnamtType>
</shrsOrPrnAmt>
<investmentDiscretion>SOLE</investmentDiscretion>
<votingAuthority>
<Sole>500</Sole>
<Shared>0</Shared>
<None>0</None>
</votingAuthority>
</infoTable>
</informationTable>
</root>
"""


@pytest.mark.asyncio
async def test_parse_13f_hr_preserves_ampersand_entities():
    """Issuer/title names containing '&' must not be corrupted or dropped."""
    result = await parse_13f_hr(SGML_FILING)
    names = {r["nameOfIssuer"] for r in result}

    assert "S&P500 EQL WGT" in names
    assert "BABCOCK & WILCOX ENTERPRISES" in names
    assert sum(r["weight"] for r in result) == pytest.approx(1.0)


def test_prepare_13f_xml_preserves_ampersand_in_attribute_value():
    """Attribute entities must survive block extraction (only decls are stripped)."""
    prepared = prepare_13f_xml(SGML_FILING)
    soup = BeautifulSoup(prepared, "xml")
    info = soup.find("infoTable")

    assert info is not None
    assert info.get("audit") == "S&P holdings"
    assert info.find("nameOfIssuer").get_text() == "S&P500 EQL WGT"


def test_prepare_13f_xml_no_block_fallback_returns_original_unchanged():
    """When there are no <XML> blocks, the original filing text is returned as-is."""
    assert prepare_13f_xml(PLAIN_XML_FILING) is PLAIN_XML_FILING
    assert prepare_13f_xml(PLAIN_XML_FILING) == PLAIN_XML_FILING


@pytest.mark.asyncio
async def test_parse_13f_hr_no_xml_blocks_still_parses():
    """Fallback path (no <XML> wrappers) must still parse a well-formed filing."""
    result = await parse_13f_hr(PLAIN_XML_FILING)
    names = {r["nameOfIssuer"] for r in result}

    assert "S&P500 EQL WGT" in names
    assert sum(r["weight"] for r in result) == pytest.approx(1.0)
