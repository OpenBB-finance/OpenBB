"""Markdown 'How To Use' notes served to the OpenBB Workspace app tabs."""

HOW_TO_USE: dict[str, str] = {
    "bills": (
        "## How To Use\n\n"
        "The Congress number is a sequential number representing the formed"
        " Congress for the elected period. As of 2026, the current Congress number"
        " is 119. Leaving it empty surfaces the 100 most recent bills.\n\n"
        "You can narrow the field by selecting a bill type, restricting dates, or"
        " adjusting the limit and offset parameters.\n\n"
        'The three widgets on this tab are grouped by the "Bill ID" column.\n\n'
        '**Click a cell in the pinned "Bill ID" column to change the loaded bill'
        " in the two widgets below.**\n\n"
        "**You can also manually enter a bill id —"
        " `{congress}-{bill_type}-{bill_number}`, e.g. `119-hr-29`.**\n\n"
        "Some bills, such as resolutions, may not have any formal text. If a bill"
        " has not been introduced in the House, it will likely not have any text"
        " to display in the viewer. Items from today may not be immediately"
        " available to the public."
    ),
    "amendments": (
        "## How To Use\n\n"
        "These widgets work the same way as the three on the **Bills** tab.\n\n"
        '**Click a cell in the pinned "Amendment ID" column to change the loaded'
        " amendment.**\n\n"
        "With no Congress number, amendments for the current Congress are"
        " surfaced. You can also filter by type.\n\n"
        "Amendment text is resolved to its Congressional Record document via the"
        " GovInfo link service. Some amendments were never printed in the Record"
        " and have no document.\n\n"
        "On a working day, there may be hundreds of amendments appended to the"
        " same bill. Each amendment number is a unique record."
    ),
    "committees": (
        "## How To Use\n\n"
        "Congressional committees produce different types of documents; this tab"
        " exposes them as a hierarchy:\n\n"
        "Congress → Chamber → Committee → Subcommittee → Document Type\n\n"
        "When no subcommittee is selected, the documents reflect the parent"
        " committee.\n\n"
        "Some committee meetings are only available as video; events producing no"
        " documents are omitted. GovInfo occasionally includes files that are not"
        ' properly encoded at the source, and those will result in "Failed to'
        ' load PDF file."'
    ),
    "laws": (
        "## How To Use\n\n"
        "Enacted public and private laws. Group the table by the pinned"
        ' "Law ID" column and click a cell to view the law text in the'
        " Congressional Law Viewer."
    ),
    "calendars": (
        "## How To Use\n\n"
        "Daily House and Senate calendar editions. Group the table by the pinned"
        ' "Calendar Date" column and click a cell to view the edition in the'
        " Congressional Calendar Viewer."
    ),
    "mandated_reports": (
        "## How To Use\n\n"
        "Reports submitted to Congress by federal agencies. Group the table by the"
        ' pinned "Package ID" column and click a cell to view the report in the'
        " Mandated Report Viewer."
    ),
    "members": (
        "## How To Use\n\n"
        "The current members of Congress. Filter the table by chamber, state, or"
        " party.\n\n"
        '**Click a cell in the pinned "Bioguide ID" column** (or pick a member from'
        " the dropdowns) to load that member into the **Member Info**, **Member"
        " Votes**, and **Member Legislation** widgets.\n\n"
        "- **Member Info**: bio, full term history, committee assignments, links, and"
        " their career On-Passage Yea/Nay voting record.\n"
        "- **Member Votes**: roll-call votes on legislation (House **and** Senate),"
        " across their full tenure, sourced from Voteview.\n"
        "- **Member Legislation**: bills the member sponsored or cosponsored."
    ),
}
