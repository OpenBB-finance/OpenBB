# Congress.gov Provider

A **fully keyless** OpenBB Platform provider for U.S. legislative data. It sources
everything from public, no-credential endpoints:

- **GovInfo bulk data** — bills (`BILLSTATUS`), CRS summaries (`BILLSUM`), bill text
  (`BILLS`), enacted laws (`PLAW`), congressional calendars (`CCAL`), and mandated
  reports (`CMR`).
- **GovInfo link service & `wssearch`** — full-text search and the Congressional
  Record documents that amendment text resolves to.
- **The unitedstates `congress-legislators` dataset** — members, committees,
  committee membership, social handles, and member photos.
- **Voteview** — every roll-call vote for **both chambers**, across full history,
  mapped to bioguide ids.

> No `api.congress.gov` API key is used anywhere — the provider requires **no
> credentials**.

## Features

- **Bills** — list/filter bills by congress, type, and date; per-bill metadata and
  CRS summaries (Markdown + raw JSON); text versions (PDF) in a document viewer.
- **Amendments** — list/filter amendments; per-amendment metadata; amendment text
  resolved to its Congressional Record document via the GovInfo link service.
- **Enacted laws** — public and private laws with a text viewer.
- **Congressional calendars** — daily House and Senate calendar editions.
- **Mandated reports** — agency reports submitted to Congress.
- **Committees** — committee/subcommittee info, documents (reports, hearings with
  witnesses, prints), and a theme-aware HTML **member-card** widget (photos, party
  colors, ages).
- **Full-text search** — across the congressional GovInfo collections.
- **Members** — roster plus, per member: an HTML **bio card** (photo, full term
  history, committee assignments, links, and a career *On-Passage* Yea/Nay tally),
  roll-call **votes** on legislation (House **and** Senate, full tenure), and the
  bills they sponsored or cosponsored.

### OpenBB Workspace Application

With this extension and `openbb-platform-api` installed, a multi-tab OpenBB
Workspace app is served from the backend: **Bills**, **Amendments**,
**Committees**, **Members**, **Laws**, **Calendars**, **Mandated Reports**, and
**Search** — each with grouped tables, document viewers, Markdown/HTML widgets, and
"How To Use" notes.

## Installation

```bash
pip install openbb-congress-gov
```

Then build the Python static assets so the `uscongress` router is registered:

```sh
openbb-build
```

The Workspace app can run standalone with only `openbb-congress-gov` and
`openbb-platform-api` installed:

```sh
openbb-api
```

## Configuration

**None required.** All data is public and keyless, so there are no credentials to
set up.

## Coverage

All endpoints are under the `obb.uscongress` path. The data commands:

```python
In [1]: from openbb import obb
In [2]: obb.uscongress
Out[2]:
/uscongress
    amendment_info
    amendment_text
    amendments
    bill_info
    bill_text
    bills
    calendars
    committee_documents
    committee_info
    laws
    mandated_reports
    member_legislation
    member_votes
    members
    search
```

The provider also exposes Workspace-only support endpoints (not data commands):
`*_urls` document-viewer resolvers (`bill_text_urls`, `amendment_text_urls`,
`law_text_urls`, `calendar_urls`, `mandated_report_urls`, `committee_document_urls`,
`search_document_urls`), the `*_choices` dropdown endpoints (`committee_choices`,
`member_choices`), the HTML widgets (`committee_members`, `member_info`), and the
`how_to_use` notes.

### Bill / Amendment text downloads

`bill_text` and `amendment_text` are POST endpoints that download documents from
GovInfo. They expect a list of GovInfo URLs in the request body:

```json
{
    "urls": ["https://www.govinfo.gov/content/pkg/BILLS-119hr29ih/pdf/BILLS-119hr29ih.pdf"]
}
```

## Usage Examples

```python
from openbb import obb

# Recent bills (defaults to the current Congress)
obb.uscongress.bills(limit=10)

# A specific bill's metadata + CRS summary, by bill id (congress-type-number)
obb.uscongress.bill_info(bill_id="119-hr-1")

# Amendments for the current Congress, filtered to Senate amendments
obb.uscongress.amendments(amendment_type="samdt")

# A member's full voting history on legislation (House and Senate), by bioguide id
obb.uscongress.member_votes(bioguide_id="C000127")

# Bills a member sponsored or cosponsored across every Congress they served
obb.uscongress.member_legislation(bioguide_id="A000055")

# Full-text search across the congressional GovInfo collections
obb.uscongress.search(query="artificial intelligence", congress=119)
```

Identifiers use the canonical dash form — `bill_id` like `119-hr-29`, `amendment_id`
like `119-hamdt-2`, and `bioguide_id` like `A000055`. See the function signatures and
docstrings for all parameters.
