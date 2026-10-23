"""Project Congressional member records to the payloads the widget pages render."""

from datetime import date
from urllib.parse import quote

_PROFILE_LINKS = {
    "wikipedia": ("Wikipedia", "https://en.wikipedia.org/wiki/{}"),
    "ballotpedia": ("Ballotpedia", "https://ballotpedia.org/{}"),
    "govtrack": ("GovTrack", "https://www.govtrack.us/congress/members/{}"),
    "opensecrets": (
        "OpenSecrets",
        "https://www.opensecrets.org/members-of-congress/summary?cid={}",
    ),
    "votesmart": ("VoteSmart", "https://justfacts.votesmart.org/candidate/{}"),
    "cspan": ("C-SPAN", "https://www.c-span.org/person/?{}"),
}
_SOCIAL_LINKS = {
    "twitter": ("Twitter/X", "https://twitter.com/{}"),
    "facebook": ("Facebook", "https://facebook.com/{}"),
    "instagram": ("Instagram", "https://instagram.com/{}"),
    "youtube": ("YouTube", "https://youtube.com/user/{}"),
}
_ROLE = {"rep": "Representative", "sen": "Senator"}
_GENDER = {"M": "Male", "F": "Female"}
_PARTY_LETTER = {"Republican": "R", "Democrat": "D", "Independent": "I"}


def _age(birthday: str, today: date | None = None) -> int | None:
    """Return the member's age in whole years from a ``YYYY-MM-DD`` birthday.

    Parameters
    ----------
    birthday : str
        Birthday in ISO format. Empty or unparsable values return None.
    today : date | None
        Reference date. Defaults to the current date.

    Returns
    -------
    int | None
        Age in whole years, or None when the birthday is unusable.
    """
    if not birthday:
        return None
    try:
        born = date.fromisoformat(birthday)
    except ValueError:
        return None
    today = today or date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _profile_url(template: str, value) -> str:
    """Build an external profile URL, encoding spaces in the id."""
    return template.format(quote(str(value).replace(" ", "_"), safe="_"))


def _term_location(term: dict) -> str:
    """Format a term's ``state[-district]`` location string."""
    location = term.get("state", "")
    if term.get("district") is not None:
        location = f"{location}-{term.get('district')}"
    return location


def _rank_key(member: dict) -> int:
    """Sort key: chairs first, then ranking members, then the rest."""
    title = (member.get("title") or "").lower()
    if title in ("chair", "chairman", "chairwoman", "chairperson"):
        return 0
    if "ranking" in title:
        return 1
    return 2


def committee_members_payload(
    members: list,
    profiles: dict,
    detail: dict | None = None,
) -> dict:
    """Build the payload for the committee members page.

    Parameters
    ----------
    members : list
        Committee membership records, each with name, title, and bioguide.
    profiles : dict
        Legislator profiles indexed by bioguide id.
    detail : dict | None
        Committee overview - name, jurisdiction, website, and parent name.

    Returns
    -------
    dict
        Committee detail and one record per member, chairs first.
    """
    detail = detail or {}
    cards: list[dict] = []

    for member in sorted(members, key=_rank_key):
        bioguide = member.get("bioguide", "")
        profile = profiles.get(bioguide, {})
        party = profile.get("party", "")
        cards.append(
            {
                "bioguide_id": bioguide,
                "name": member.get("name", "Unknown"),
                "title": member.get("title") or "Member",
                "party": party,
                "party_letter": _PARTY_LETTER.get(party, "·"),
                "state": profile.get("state", ""),
                "age": _age(profile.get("birthday", "")),
                "photo_url": profile.get("photo_url"),
            }
        )

    return {
        "committee": {
            "name": detail.get("name", ""),
            "chamber": detail.get("chamber", ""),
            "jurisdiction": detail.get("jurisdiction", ""),
            "website": detail.get("website", ""),
            "parent_name": detail.get("parent_name", ""),
            "is_subcommittee": bool(detail.get("is_subcommittee")),
        },
        "members": cards,
    }


def member_bio_payload(
    record: dict,
    committees: list,
    social: dict,
    voting: dict,
    photo_url: str | None = None,
) -> dict:
    """Build the payload for a member's bio page.

    Parameters
    ----------
    record : dict
        The member's unitedstates legislator record.
    committees : list
        Committee assignments from ``member_committees``.
    social : dict
        Social-media handles indexed by network.
    voting : dict
        Career On-Passage tally - yea, nay, total, and yea_pct.
    photo_url : str | None
        Portrait URL, when one exists.

    Returns
    -------
    dict
        Identity, contact, links, committees, terms, and the voting tally.
    """
    ids = record.get("id", {})
    name = record.get("name", {})
    bio = record.get("bio", {})
    terms = record.get("terms", [])
    current = terms[-1] if terms else {}
    party = current.get("party", "")

    return {
        "bioguide_id": ids.get("bioguide", ""),
        "name": name.get("official_full")
        or f"{name.get('first', '')} {name.get('last', '')}".strip()
        or "Unknown",
        "role": _ROLE.get(current.get("type", ""), "Member"),
        "party": party,
        "party_letter": _PARTY_LETTER.get(party, "·"),
        "location": _term_location(current),
        "photo_url": photo_url,
        "birthday": bio.get("birthday", ""),
        "age": _age(bio.get("birthday", "")),
        "gender": _GENDER.get(bio.get("gender", ""), ""),
        "contact": {
            "website": current.get("url", ""),
            "contact_form": current.get("contact_form", ""),
            "phone": current.get("phone", ""),
            "office": current.get("office", ""),
        },
        "links": [
            {"label": label, "url": _profile_url(template, ids[key])}
            for key, (label, template) in _PROFILE_LINKS.items()
            if ids.get(key)
        ],
        "social": [
            {"label": label, "url": _profile_url(template, social[key])}
            for key, (label, template) in _SOCIAL_LINKS.items()
            if social.get(key)
        ],
        "committees": [
            {
                "committee": committee.get("committee", ""),
                "title": committee.get("title") or "Member",
                "is_subcommittee": bool(committee.get("is_subcommittee")),
            }
            for committee in committees
        ],
        "terms": [
            {
                "start": term.get("start", ""),
                "end": term.get("end", ""),
                "role": _ROLE.get(term.get("type", ""), "Member"),
                "location": _term_location(term),
                "party": term.get("party", ""),
            }
            for term in reversed(terms)
        ],
        "voting": {
            "yea": voting.get("yea", 0),
            "nay": voting.get("nay", 0),
            "total": voting.get("total", 0),
            "yea_pct": voting.get("yea_pct"),
        },
    }
