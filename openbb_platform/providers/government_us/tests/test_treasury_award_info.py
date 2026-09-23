"""Tests for the federal award info HTML widget."""

import asyncio
import json
import re

from openbb_government_us.treasury import treasury_router
from openbb_government_us.treasury.models import usaspending_award
from openbb_government_us.treasury.treasury_router import award_info, router
from openbb_government_us.treasury.utils import usaspending
from openbb_government_us.treasury.utils.award_render import render_award_info


def _record(**overrides) -> dict:
    """Build a detail record with overridable defaults."""
    record = {
        "award_id": "CONT_AWD_HT940216C0001_9700",
        "section": "detail",
        "category": "contract",
        "award_type_description": "DEFINITIVE CONTRACT",
        "description": "MANAGED CARE SUPPORT",
        "piid": "HT940216C0001",
        "total_obligation": 51269205263.03,
        "base_and_all_options": 56620536577.19,
        "subaward_count": 146,
        "date_signed": "2016-07-29",
        "period_start": "2016-08-01",
        "recipient_name": "HUMANA GOVERNMENT BUSINESS INC",
        "recipient_uei": "ZE6ZM6NKSV43",
        "recipient_state": "KY",
        "place_of_performance_state": "KY",
        "awarding_agency": "Department of Defense",
        "funding_agency": "Department of Defense",
        "naics": "524114",
        "psc": "Q201",
    }
    record.update(overrides)
    return record


def _raw_detail(**overrides) -> dict:
    """Build a source-shaped award detail payload."""
    record = {
        "generated_unique_award_id": "CONT_AWD_HT940216C0001_9700",
        "id": 307885715,
        "category": "contract",
        "type_description": "DEFINITIVE CONTRACT",
        "description": "MANAGED CARE SUPPORT",
        "piid": "HT940216C0001",
        "total_obligation": 51269205263.03,
        "recipient": {"recipient_name": "HUMANA GOVERNMENT BUSINESS INC"},
        "period_of_performance": {"start_date": "2016-08-01"},
    }
    record.update(overrides)
    return record


def _raw_subaward(number: int) -> dict:
    """Build a source-shaped subaward payload."""
    return {
        "id": 9850548 + number,
        "subaward_number": f"WS-16-C-0001, MOD M{number}",
        "description": "REIMBURSEMENT METHODOLOGY CHANGES",
        "action_date": "2025-03-07",
        "amount": 258312.0,
        "recipient_name": "WISCONSIN PHYSICIANS SERVICE INSURANCE CORP.",
    }


class TestAwardRender:
    """Tests for the award detail HTML renderer."""

    def test_renders_each_populated_section(self):
        """Every section holding a populated field gets a heading."""
        html = render_award_info(_record())
        assert re.findall(r"<h2>([^<]+)</h2>", html) == [
            "Award",
            "Amounts",
            "Period of Performance",
            "Recipient",
            "Place of Performance",
            "Agencies",
            "Classification",
        ]

    def test_leaves_no_unreplaced_tokens(self):
        """Every template token is substituted."""
        html = render_award_info(_record())
        assert "__" not in html

    def test_omits_absent_fields(self):
        """A field the award does not report renders no row at all."""
        html = render_award_info(_record())
        assert "Total Loan Value" not in html
        assert "FAIN" not in html
        assert "Total Obligation" in html

    def test_absent_section_is_dropped_entirely(self):
        """A section with no populated field renders no heading."""
        record = _record()
        del record["place_of_performance_state"]
        assert "Place of Performance" not in render_award_info(record)

    def test_numbers_keep_full_precision(self):
        """Monetary values are emitted raw, unrounded and unabbreviated."""
        html = render_award_info(_record())
        assert 'data-value="51269205263.03"' in html
        assert 'data-value="56620536577.19"' in html
        assert "51.27" not in html
        assert "51,269,205,263.03" not in html

    def test_escapes_hostile_values(self):
        """Source text is escaped rather than injected as markup."""
        html = render_award_info(
            _record(description="<script>alert('x')</script>", recipient_name="A&B <b>")
        )
        assert "<script>alert" not in html
        assert "&lt;script&gt;alert" in html
        assert "A&amp;B &lt;b&gt;" in html

    def test_template_token_in_data_is_inert(self):
        """A literal template token in source text is not treated as a token."""
        html = render_award_info(_record(description="__BODY__ __KPIS__"))
        assert "__BODY__ __KPIS__" in html
        assert re.search(r"<h2>Award</h2>", html)

    def test_empty_record_renders_placeholder(self):
        """A record with no fields renders the empty-state message."""
        html = render_award_info({})
        assert "No award detail was returned." in html
        assert "__" not in html


def _subaward(**overrides) -> dict:
    """Build a subaward record with overridable defaults."""
    record = {
        "award_id": "CONT_AWD_HT940216C0001_9700",
        "section": "subawards",
        "subaward_id": 9850548,
        "subaward_number": "WS-16-C-0001, MOD M164",
        "description": "REIMBURSEMENT METHODOLOGY CHANGES",
        "action_date": "2025-03-07",
        "amount": 258312.0,
        "recipient_name": "WISCONSIN PHYSICIANS SERVICE INSURANCE CORP.",
    }
    record.update(overrides)
    return record


class TestSubawardCards:
    """Tests for the collapsible subaward cards."""

    def test_renders_one_collapsible_card_per_subaward(self):
        """Each subaward becomes its own details element."""
        html = render_award_info(_record(), [_subaward(), _subaward(subaward_id=2)], 2)
        assert html.count('<details class="sub">') == 2
        assert "<summary>Subawards (2)</summary>" in html

    def test_section_is_itself_collapsible_and_starts_closed(self):
        """The whole subawards block is one collapsible container, closed by default."""
        html = render_award_info(_record(), [_subaward()], 1)
        assert '<details class="subawards"><summary>Subawards (1)</summary>' in html
        assert '<details class="subawards" open' not in html

    def test_summary_carries_recipient_date_and_amount(self):
        """The collapsed summary shows who, when, and how much."""
        html = render_award_info(_record(), [_subaward()], 1)
        assert (
            '<span class="sub-name">WISCONSIN PHYSICIANS SERVICE INSURANCE CORP.</span>'
            in html
        )
        assert '<span class="sub-date">2025-03-07</span>' in html
        assert '<span class="sub-amount" data-value="258312.0"' in html

    def test_card_body_lists_the_individual_details(self):
        """The expanded card lists each populated subaward field."""
        html = render_award_info(_record(), [_subaward()], 1)
        body = re.search(r'<div class="sub-body"><dl>(.*?)</dl>', html, re.S).group(1)
        assert re.findall(r"<dt>([^<]+)</dt>", body) == [
            "Subaward Number",
            "Action Date",
            "Amount",
            "Description",
            "Subaward ID",
        ]

    def test_card_omits_absent_subaward_fields(self):
        """A subaward field the source omits renders no row."""
        subaward = _subaward()
        del subaward["description"]
        html = render_award_info(_record(), [subaward], 1)
        body = re.search(r'<div class="sub-body"><dl>(.*?)</dl>', html, re.S).group(1)
        assert "Description" not in body

    def test_amount_keeps_full_precision(self):
        """Subaward amounts are emitted raw, not rounded or abbreviated."""
        html = render_award_info(_record(), [_subaward(amount=1913834852.94)], 1)
        assert 'data-value="1913834852.94"' in html
        assert "1.91 B" not in html

    def test_discloses_a_truncated_render(self):
        """Rendering fewer cards than the award reports says so explicitly."""
        html = render_award_info(_record(), [_subaward()], 1234)
        assert "<summary>Subawards (1234)</summary>" in html
        assert "Showing the first 1 of 1234." in html

    def test_no_note_when_every_subaward_is_shown(self):
        """A complete render carries no truncation note."""
        html = render_award_info(_record(), [_subaward()], 1)
        assert 'class="note"' not in html

    def test_no_subawards_renders_no_section(self):
        """An award without subawards renders no subawards block."""
        html = render_award_info(_record(), [], None)
        assert '<details class="subawards">' not in html
        assert '<details class="sub">' not in html
        assert "__" not in html

    def test_escapes_hostile_subaward_values(self):
        """Subaward text is escaped rather than injected as markup."""
        html = render_award_info(
            _record(),
            [_subaward(recipient_name="<img src=x onerror=alert(1)>")],
            1,
        )
        assert "<img src=x" not in html
        assert "&lt;img src=x" in html

    def test_unnamed_subrecipient_falls_back(self):
        """A subaward with no recipient name still gets a card label."""
        subaward = _subaward()
        del subaward["recipient_name"]
        html = render_award_info(_record(), [subaward], 1)
        assert "Unnamed subrecipient" in html


class TestAwardInfoEndpoint:
    """Tests for the award_info endpoint's two response branches."""

    @staticmethod
    def _patch(monkeypatch, detail, pages):
        """Patch the detail fetch and the paged subawards POST."""
        calls: dict = {"pages": []}

        async def _fake_extract(query, credentials, **kwargs):
            return [detail]

        async def _fake_post(path, payload, **kwargs):
            calls["pages"].append(payload["page"])
            page = pages[payload["page"] - 1]
            return {
                "results": page,
                "page_metadata": {"hasNext": payload["page"] < len(pages)},
            }

        monkeypatch.setattr(
            usaspending_award.UsSpendingAwardFetcher, "aextract_data", _fake_extract
        )
        monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)
        return calls

    def test_html_branch_returns_a_document(self, monkeypatch):
        """Without raw, the endpoint returns the rendered HTML page."""
        self._patch(monkeypatch, _raw_detail(), [[]])
        response = asyncio.run(award_info("CONT_AWD_HT940216C0001_9700"))
        body = response.body.decode()
        assert response.media_type == "text/html"
        assert "HUMANA GOVERNMENT BUSINESS INC" in body
        assert 'data-value="51269205263.03"' in body

    def test_raw_branch_returns_detail_and_subawards(self, monkeypatch):
        """With raw=True, the JSON carries the detail row and every subaward row."""
        self._patch(
            monkeypatch,
            _raw_detail(subaward_count=2),
            [[_raw_subaward(1), _raw_subaward(2)]],
        )
        response = asyncio.run(award_info("CONT_AWD_HT940216C0001_9700", raw=True))
        records = json.loads(response.body.decode())
        assert response.media_type == "application/json"
        assert [r["section"] for r in records] == ["detail", "subawards", "subawards"]
        assert records[0]["total_obligation"] == 51269205263.03
        assert records[1]["amount"] == 258312.0
        assert "<html" not in response.body.decode()

    def test_raw_subaward_rows_share_one_key_set(self, monkeypatch):
        """A subaward missing a field still carries it, so the rows stay square."""
        bare = _raw_subaward(2)
        bare["description"] = None
        self._patch(
            monkeypatch, _raw_detail(subaward_count=2), [[_raw_subaward(1), bare]]
        )
        response = asyncio.run(award_info("CONT_AWD_HT940216C0001_9700", raw=True))
        records = json.loads(response.body.decode())
        rows = [r for r in records if r["section"] == "subawards"]
        assert len(rows) == 2
        assert len({tuple(row) for row in rows}) == 1
        assert rows[1]["description"] is None

    def test_paginates_until_the_source_runs_out(self, monkeypatch):
        """Subawards spanning multiple pages are all collected."""
        calls = self._patch(
            monkeypatch,
            _raw_detail(subaward_count=3),
            [[_raw_subaward(1), _raw_subaward(2)], [_raw_subaward(3)]],
        )
        response = asyncio.run(award_info("CONT_AWD_HT940216C0001_9700"))
        assert calls["pages"] == [1, 2]
        assert response.body.decode().count('<details class="sub">') == 3

    def test_skips_the_subaward_fetch_when_the_count_is_zero(self, monkeypatch):
        """An award reporting no subawards makes no subaward request."""
        calls = self._patch(monkeypatch, _raw_detail(subaward_count=0), [[]])
        response = asyncio.run(award_info("CONT_AWD_HT940216C0001_9700"))
        assert calls["pages"] == []
        assert '<details class="sub">' not in response.body.decode()

    def test_stops_at_the_render_cap_and_discloses_it(self, monkeypatch):
        """Paging stops at the cap and the shortfall is stated, never silent."""
        monkeypatch.setattr(treasury_router, "SUBAWARD_RENDER_CAP", 3)
        calls = self._patch(
            monkeypatch,
            _raw_detail(subaward_count=99),
            [[_raw_subaward(1), _raw_subaward(2)]] * 5,
        )
        body = asyncio.run(award_info("CONT_AWD_HT940216C0001_9700")).body.decode()
        assert calls["pages"] == [1, 2]
        assert body.count('<details class="sub">') == 3
        assert "Showing the first 3 of 99." in body

    def test_widget_declares_html_with_the_raw_toggle(self):
        """The registered route advertises an HTML widget with the raw toggle."""
        route = next(r for r in router.api_router.routes if r.path == "/award_info")
        config = route.openapi_extra["widget_config"]
        assert config["type"] == "html"
        assert config["raw"] is True
        assert config["widgetId"] == "ustreasury_award_info_us_treasury_obb"
        assert [p["paramName"] for p in config["params"]] == ["award_id", "raw"]
        assert config["params"][1]["show"] is False
