"""Render committee members as themed HTML cards for the OpenBB Workspace HTML widget."""

from datetime import date
from html import escape
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

_THEME = {
    "dark": {
        "bg": "transparent",
        "card": "#1b1f27",
        "text": "#e6e8eb",
        "muted": "#9aa4b2",
        "border": "#2c333f",
    },
    "light": {
        "bg": "transparent",
        "card": "#ffffff",
        "text": "#1b1f27",
        "muted": "#5a6473",
        "border": "#e2e6ea",
    },
}
_PARTY = {
    "Republican": ("#c0392b", "R"),
    "Democrat": ("#2563c9", "D"),
    "Independent": ("#6b7280", "I"),
}


def _age(birthday: str, today: date | None = None) -> int | None:
    """Return the member's age in whole years from a ``YYYY-MM-DD`` birthday."""
    if not birthday:
        return None
    try:
        born = date.fromisoformat(birthday)
    except ValueError:
        return None
    today = today or date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _anchor(label: str, href: str) -> str:
    """Build a safe external ``<a>`` tag, URL-encoding the href."""
    safe_href = escape(href, quote=True)
    return (
        f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer">'
        f"{escape(label)}</a>"
    )


def _profile_anchor(label: str, template: str, value: str) -> str:
    """Build an external profile anchor, encoding spaces in the id (e.g. Wikipedia)."""
    return _anchor(
        label, template.format(quote(str(value).replace(" ", "_"), safe="_"))
    )


def _term_location(term: dict) -> str:
    """Format a term's ``state[-district]`` location string."""
    loc = term.get("state", "")
    if term.get("district") is not None:
        loc = f"{loc}-{term.get('district')}"
    return loc


def _voting_section(voting: dict) -> str:
    """Render the career On-Passage Yea/Nay tally for the bio card."""
    total = voting.get("total", 0)
    if not total:
        return _section(
            "Voting Record",
            '<div class="vote-empty">No On-Passage roll-call votes on record.</div>',
        )
    yea, nay, pct = voting["yea"], voting["nay"], voting["yea_pct"]
    yea_w = round(100 * yea / total, 1)
    return _section(
        "Voting Record — On Passage (career)",
        f'<div class="vote-bar"><span style="width:{yea_w}%"></span></div>'
        f'<div class="vote-line"><span class="vote-yea-t">{yea} Yea</span>'
        f' · <span class="vote-nay-t">{nay} Nay</span> · <b>{pct}% Yea</b></div>',
    )


def render_member_bio(
    record: dict,
    committees: list,
    social: dict,
    voting: dict,
    theme: str | None,
    photo_url: str = "",
) -> str:
    """Build the themed HTML bio card for a single member."""
    colors = _THEME["light"] if theme == "light" else _THEME["dark"]
    ids = record.get("id", {})
    name = record.get("name", {})
    bio = record.get("bio", {})
    terms = record.get("terms", [])
    current = terms[-1] if terms else {}

    full_name = escape(
        name.get("official_full")
        or f"{name.get('first', '')} {name.get('last', '')}".strip()
        or "Unknown"
    )
    accent, letter = _PARTY.get(current.get("party", ""), ("#6b7280", "·"))
    role = _ROLE.get(current.get("type", ""), "Member")
    subtitle = escape(
        " · ".join(
            p for p in (role, _term_location(current), current.get("party", "")) if p
        )
    )

    if photo_url:
        avatar = (
            f'<img class="photo" src="{escape(photo_url, quote=True)}"'
            f' alt="{full_name}" />'
        )
    else:
        initials = escape("".join(p[0] for p in full_name.split()[:2]).upper())
        avatar = f'<div class="photo initials">{initials}</div>'

    facts = []
    birthday = bio.get("birthday")
    if birthday:
        age = _age(birthday)
        facts.append(
            f"Born {escape(birthday)}" + (f" (Age {age})" if age is not None else "")
        )
    if gender := _GENDER.get(bio.get("gender", "")):
        facts.append(gender)
    facts_html = f'<div class="facts">{" · ".join(facts)}</div>' if facts else ""

    contact = []
    if current.get("url"):
        contact.append(_anchor("Website", current["url"]))
    if current.get("contact_form"):
        contact.append(_anchor("Contact", current["contact_form"]))
    if current.get("phone"):
        contact.append(escape(current["phone"]))
    if current.get("office"):
        contact.append(escape(current["office"]))
    contact_html = (
        f'<div class="contact">{" · ".join(contact)}</div>' if contact else ""
    )

    sections = _voting_section(voting)

    links = [
        _profile_anchor(label, template, ids[key])
        for key, (label, template) in _PROFILE_LINKS.items()
        if ids.get(key)
    ]
    if links:
        sections += _section("Links", " · ".join(links))

    socials = [
        _profile_anchor(label, template, social[key])
        for key, (label, template) in _SOCIAL_LINKS.items()
        if social.get(key)
    ]
    if socials:
        sections += _section("Social", " · ".join(socials))

    if committees:
        items = "".join(
            f"<li>{escape(c.get('committee', ''))}"
            f'<span class="role"> {escape(c.get("title") or "Member")}</span></li>'
            for c in committees
        )
        sections += _section("Committee Assignments", f"<ul>{items}</ul>")

    if terms:
        rows = "".join(
            f"<li><span class='years'>{escape(t.get('start', ''))} – "
            f"{escape(t.get('end', ''))}</span> {_ROLE.get(t.get('type', ''), 'Member')},"
            f" {escape(_term_location(t))} ({escape(t.get('party', ''))})</li>"
            for t in reversed(terms)
        )
        sections += _section("Term History", f"<ul>{rows}</ul>")

    return f"""<style>
.member-bio {{ background:{colors["bg"]}; color:{colors["text"]}; padding:14px;
  font-family:-apple-system,Segoe UI,Roboto,sans-serif; font-size:13px; }}
.member-bio .head {{ display:flex; gap:14px; align-items:flex-start;
  border-bottom:1px solid {colors["border"]}; padding-bottom:12px; }}
.member-bio .photo {{ width:104px; height:127px; object-fit:cover; border-radius:8px;
  border-top:3px solid {accent}; background:{colors["border"]}; flex:none; }}
.member-bio .photo.initials {{ display:flex; align-items:center; justify-content:center;
  font-size:32px; font-weight:700; color:{colors["muted"]}; }}
.member-bio .name {{ font-size:17px; font-weight:700; }}
.member-bio .badge {{ display:inline-block; margin-left:8px; color:#fff;
  background:{accent}; font-size:12px; font-weight:700; border-radius:4px; padding:1px 6px;
  vertical-align:middle; }}
.member-bio .sub {{ color:{colors["muted"]}; margin-top:3px; }}
.member-bio .facts {{ margin-top:6px; }}
.member-bio .contact {{ margin-top:6px; font-size:12px; color:{colors["muted"]}; }}
.member-bio a {{ color:{accent}; text-decoration:none; }}
.member-bio a:hover {{ text-decoration:underline; }}
.member-bio h4 {{ margin:14px 0 6px; font-size:12px; text-transform:uppercase;
  letter-spacing:.04em; color:{colors["muted"]}; }}
.member-bio ul {{ margin:0; padding-left:18px; }}
.member-bio li {{ margin:2px 0; }}
.member-bio .role {{ color:{colors["muted"]}; }}
.member-bio .years {{ font-variant-numeric:tabular-nums; font-weight:600; }}
.member-bio .vote-bar {{ height:8px; border-radius:4px; overflow:hidden;
  background:#c0392b; margin:2px 0 5px; }}
.member-bio .vote-bar span {{ display:block; height:100%; background:#27ae60; }}
.member-bio .vote-yea-t {{ color:#27ae60; font-weight:600; }}
.member-bio .vote-nay-t {{ color:#c0392b; font-weight:600; }}
.member-bio .vote-empty {{ color:{colors["muted"]}; }}
</style>
<div class="member-bio">
  <div class="head">{avatar}
    <div><div class="name">{full_name}<span class="badge">{letter}</span></div>
      <div class="sub">{subtitle}</div>{facts_html}{contact_html}</div>
  </div>{sections}
</div>"""


def _section(title: str, body: str) -> str:
    """Wrap a titled section of the bio card."""
    return f"<h4>{escape(title)}</h4>{body}"


def _rank_key(member: dict) -> int:
    """Sort key: chairs first, then ranking members, then the rest."""
    title = (member.get("title") or "").lower()
    if title in ("chair", "chairman", "chairwoman", "chairperson"):
        return 0
    if "ranking" in title:
        return 1
    return 2


def render_member_cards(members: list, legislators: dict, theme: str | None) -> str:
    """Build the HTML for a committee's member cards."""
    colors = _THEME["light"] if theme == "light" else _THEME["dark"]

    cards = ""
    for member in sorted(members, key=_rank_key):
        profile = legislators.get(member.get("bioguide", ""), {})
        accent, letter = _PARTY.get(profile.get("party", ""), ("#6b7280", "·"))
        name = escape(member.get("name", "Unknown"))
        age = _age(profile.get("birthday", ""))
        meta = " · ".join(
            p
            for p in (
                escape(member.get("title") or "Member"),
                escape(profile.get("state", "")),
                f"Age {age}" if age is not None else "",
            )
            if p
        )
        photo = profile.get("photo_url", "")

        if photo:
            avatar = f'<img class="avatar" src="{escape(photo)}" alt="{name}" />'
        else:
            initials = escape("".join(p[0] for p in name.split()[:2]).upper())
            avatar = f'<div class="avatar initials">{initials}</div>'

        cards += (
            f'<div class="card" style="border-top:3px solid {accent}">'
            f"{avatar}"
            f'<div class="info"><div class="name">{name}'
            f'<span class="badge" style="background:{accent}">{letter}</span></div>'
            f'<div class="meta">{meta}</div></div></div>'
        )

    if not members:
        cards = '<div class="empty">No member data available for this committee.</div>'

    return f"""<style>
.committee-members {{ background:{colors["bg"]}; padding:12px;
  font-family:-apple-system,Segoe UI,Roboto,sans-serif; }}
.committee-members .grid {{ display:grid;
  grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:12px; }}
.committee-members .card {{ background:{colors["card"]}; color:{colors["text"]};
  border:1px solid {colors["border"]}; border-radius:10px; padding:12px;
  display:flex; flex-direction:column; align-items:center; text-align:center; }}
.committee-members .avatar {{ width:84px; height:103px; object-fit:cover;
  border-radius:8px; background:{colors["border"]}; }}
.committee-members .avatar.initials {{ display:flex; align-items:center;
  justify-content:center; font-size:24px; font-weight:700; color:{colors["muted"]}; }}
.committee-members .info {{ margin-top:8px; width:100%; }}
.committee-members .name {{ font-weight:600; font-size:13px; line-height:1.3; }}
.committee-members .badge {{ display:inline-block; margin-left:6px; color:#fff;
  font-size:11px; font-weight:700; border-radius:4px; padding:0 5px; }}
.committee-members .meta {{ color:{colors["muted"]}; font-size:12px; margin-top:4px; }}
.committee-members .empty {{ color:{colors["muted"]}; padding:24px; }}
</style>
<div class="committee-members"><div class="grid">{cards}</div></div>"""
