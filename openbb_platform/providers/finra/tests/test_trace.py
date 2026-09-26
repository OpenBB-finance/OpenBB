"""Tests for the TRACE query building."""

import asyncio

import pytest

from openbb_finra.utils.trace import is_cusip, match_filters, resolve_bonds


class TestIsCusip:
    """CUSIPs are recognised by their check digit."""

    @pytest.mark.parametrize(
        "value", ["037833100", "037833EH9", "912810UG1", "38141gxz2", "084670702"]
    )
    def test_valid(self, value):
        """Real CUSIPs validate."""
        assert is_cusip(value)

    @pytest.mark.parametrize(
        "value", ["037833101", "AAPL5231623", "03783310", "03783310X", "0378-3310"]
    )
    def test_invalid(self, value):
        """Wrong check digits, lengths, and characters do not."""
        assert not is_cusip(value)


class TestMatchFilters:
    """Every word becomes one substring filter."""

    def test_words(self):
        """Words are split and wildcards removed."""
        assert match_filters("goldman  sachs%_", "issuerName") == [
            {
                "searchValue": "goldman",
                "fuzzy": False,
                "synonym": False,
                "fields": [{"name": "issuerName", "boost": 1}],
            },
            {
                "searchValue": "sachs",
                "fuzzy": False,
                "synonym": False,
                "fields": [{"name": "issuerName", "boost": 1}],
            },
        ]

    def test_only_wildcards(self):
        """Wildcards alone give no filter."""
        assert match_filters("%_", "issuerName") == []


class TestResolveBonds:
    """Identifiers resolve to their bond type in one search per kind."""

    def test_cusips_and_symbols(self, fake_session, response, trace_answer):
        """CUSIPs and symbols are searched separately and merged by CUSIP."""
        from openbb_finra.utils.client import trace_session

        apple = {
            "cusip": "037833EH9",
            "issueSymbolIdentifier": "AAPL5231623",
            "issuerName": "APPLE INC",
            "bondType": "CA",
        }

        def responder(call):
            if call["method"] == "GET":
                return response(400, "{}")

            field = call["json"]["domainFilters"][0]["fieldName"]

            if field == "cusip":
                return trace_answer([apple, {"cusip": None, "bondType": "CA"}])

            return trace_answer([apple])

        session = fake_session(responder=responder)

        async def run():
            async with trace_session() as trace:
                return await resolve_bonds(trace, ["037833EH9", "AAPL5231623"])

        assert asyncio.run(run()) == [apple]
        assert len(session.calls) == 3

    def test_only_symbols(self, fake_session, response, trace_answer):
        """A symbol-only request makes a single search."""
        from openbb_finra.utils.client import trace_session

        def responder(call):
            if call["method"] == "GET":
                return response(400, "{}")

            assert call["json"]["domainFilters"][0]["fieldName"] == (
                "issueSymbolIdentifier"
            )

            return trace_answer([])

        fake_session(responder=responder)

        async def run():
            async with trace_session() as trace:
                return await resolve_bonds(trace, ["AAPL5231623"])

        assert asyncio.run(run()) == []
