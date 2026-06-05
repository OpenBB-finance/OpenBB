"""Congressional Committees Utilities (keyless: unitedstates + GovInfo wssearch/MODS)."""

_CONGRESS_GOV_TO_THOMAS_ID: dict[str, str] = {
    "JJEC": "JSEC",
    "JHJE": "JSEC",
}

_GOVTRACK_DATA_CACHE: dict[str, dict] = {}


def _system_code_to_thomas_id(system_code: str) -> str:
    """Convert a Congress.gov committee systemCode to a unitedstates thomas_id."""
    code = system_code.upper()

    if code.endswith("00"):
        base = code[:-2]
        return _CONGRESS_GOV_TO_THOMAS_ID.get(base, base)

    return code


async def get_committee_members(system_code: str) -> list:
    """Fetch current committee members from unitedstates/congress-legislators."""
    from openbb_core.provider.utils.helpers import amake_request

    thomas_id = _system_code_to_thomas_id(system_code)

    if "committee_membership" not in _GOVTRACK_DATA_CACHE:
        url = (
            "https://unitedstates.github.io/congress-legislators/"
            "committee-membership-current.json"
        )
        try:
            data = await amake_request(url, timeout=30)
        except Exception:  # noqa: BLE001
            return []

        if not isinstance(data, dict):
            return []

        _GOVTRACK_DATA_CACHE["committee_membership"] = data

    membership: dict = _GOVTRACK_DATA_CACHE["committee_membership"]

    return membership.get(thomas_id, [])


async def get_committee_overview(system_code: str, chamber: str) -> dict:
    """Build a committee overview (structure + members) from keyless sources."""
    from openbb_congress_gov.utils.bulk import load_committee_structure

    structure = await load_committee_structure()
    thomas_id = _system_code_to_thomas_id(system_code)
    parent_thomas = thomas_id[:4]
    sub_thomas = thomas_id[4:]

    parent = next((c for c in structure if c.get("thomas_id") == parent_thomas), {})
    prefix = system_code.lower()[:4]

    detail: dict = {
        "name": parent.get("name", ""),
        "chamber": chamber,
        "type": parent.get("type", chamber),
        "website": parent.get("url", ""),
        "jurisdiction": parent.get("jurisdiction", ""),
        "is_subcommittee": bool(sub_thomas),
        "parent_name": "",
        "subcommittees": [],
    }

    if sub_thomas:
        sub = next(
            (
                s
                for s in parent.get("subcommittees", [])
                if s.get("thomas_id") == sub_thomas
            ),
            {},
        )
        detail["parent_name"] = parent.get("name", "")
        detail["name"] = (
            f"{parent.get('name', '')} — {sub.get('name', '')}"
            if sub.get("name")
            else parent.get("name", "")
        )
        detail["jurisdiction"] = sub.get("jurisdiction", detail["jurisdiction"])
    else:
        detail["subcommittees"] = [
            {
                "name": s.get("name", ""),
                "systemCode": f"{prefix}{s.get('thomas_id', '')}",
            }
            for s in parent.get("subcommittees", [])
            if s.get("name")
        ]

    if not detail["name"]:
        detail["name"] = system_code.upper()

    members = await get_committee_members(system_code)

    return {
        "chamber": chamber,
        "system_code": system_code,
        "detail": detail,
        "members": members,
    }


async def fetch_committee_documents(
    system_code: str,
    congress: int,
    doc_type: str = "all",
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Fetch a committee's documents from GovInfo (keyless, committee-indexed)."""
    import asyncio

    from openbb_congress_gov.utils.bulk import (
        DOC_TYPE_COLLECTION,
        search_committee_docs,
    )

    doc_types = list(DOC_TYPE_COLLECTION) if doc_type == "all" else [doc_type]

    groups = await asyncio.gather(
        *[
            search_committee_docs(system_code, dt, congress, limit=limit, offset=offset)
            for dt in doc_types
        ]
    )

    results: list[dict] = []
    seen: set[str] = set()
    for group in groups:
        for record in group:
            if record["package_id"] in seen:
                continue
            seen.add(record["package_id"])
            results.append(record)

    results.sort(key=lambda r: r.get("date") or "", reverse=True)
    return results


async def get_committee_doc_choices(
    system_code: str,
    congress: int,
    doc_type: str = "all",
    limit: int = 20,
    is_workspace: bool = False,
) -> list:
    """Document choices for a committee's viewer widget."""
    from openbb_congress_gov.utils.bulk import fetch_package_mods, parse_mods

    docs = await fetch_committee_documents(system_code, congress, doc_type, limit=limit)

    if not docs:
        if is_workspace is True:
            return [{"label": "No documents found for this committee.", "value": ""}]
        return []

    if is_workspace is False:
        return docs

    choices: list[dict] = []
    seen: set[str] = set()
    for doc in docs:
        package_id = doc["package_id"]
        label = " - ".join(p for p in (doc.get("citation"), doc.get("date")) if p)
        label = f"{label} - {doc.get('title', '')}" if label else doc.get("title", "")

        if doc["doc_url"] not in seen:
            seen.add(doc["doc_url"])
            choices.append({"label": label, "value": doc["doc_url"]})

        if doc["doc_type"] == "meeting":
            detail = parse_mods(await fetch_package_mods(package_id), package_id)
            for accompanying in detail["documents"]:
                if accompanying["pdf"] in seen:
                    continue
                seen.add(accompanying["pdf"])
                choices.append(
                    {
                        "label": f"{label} — {accompanying['title']}",
                        "value": accompanying["pdf"],
                    }
                )

    return choices
