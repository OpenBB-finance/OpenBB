"""Tests for SEC Form 13F-HR parsing."""

import asyncio

from openbb_sec.utils.parse_13f import parse_13f_hr

EMPTY_13F_FILING = """<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission>
  <headerData>
    <filerInfo><periodOfReport>2025-12-31</periodOfReport></filerInfo>
  </headerData>
  <informationTable>
    <infoTable>
      <nameOfIssuer>NA</nameOfIssuer>
      <titleOfClass>NA</titleOfClass>
      <cusip>000000000</cusip>
      <value>0</value>
      <shrsOrPrnAmt><sshPrnamt>0</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt>
      <investmentDiscretion>SOLE</investmentDiscretion>
      <votingAuthority><Sole>0</Sole><Shared>0</Shared><None>0</None></votingAuthority>
    </infoTable>
  </informationTable>
</edgarSubmission>"""


def test_parse_13f_hr_uses_zero_weight_for_empty_filings():
    """Placeholder rows in zero-holding filings must remain model-valid."""
    result = asyncio.run(parse_13f_hr(EMPTY_13F_FILING))

    assert len(result) == 1
    assert result[0]["nameOfIssuer"] == "NA"
    assert result[0]["value"] == 0
    assert result[0]["weight"] == 0.0
