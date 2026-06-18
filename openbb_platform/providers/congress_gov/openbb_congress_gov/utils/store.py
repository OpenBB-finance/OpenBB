"""SQLite-backed store for BILLSTATUS, amendments, and derived member data."""

_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS bills ("
    "bill_id TEXT PRIMARY KEY, congress INTEGER, bill_type TEXT, number INTEGER, "
    "type_display TEXT, title TEXT, origin_chamber TEXT, origin_chamber_code TEXT, "
    "update_date TEXT, update_date_text TEXT, latest_action_date TEXT, "
    "latest_action_text TEXT, record BLOB);"
    "CREATE INDEX IF NOT EXISTS ix_bills_unit ON bills (congress, bill_type);"
    "CREATE TABLE IF NOT EXISTS bill_meta ("
    "bill_id TEXT PRIMARY KEY, congress INTEGER, bill_type TEXT, title TEXT, "
    "introduced_date TEXT, latest_action_date TEXT, latest_action TEXT);"
    "CREATE TABLE IF NOT EXISTS amendments ("
    "amendment_id TEXT PRIMARY KEY, congress INTEGER, amendment_type TEXT, "
    "number TEXT, record BLOB);"
    "CREATE INDEX IF NOT EXISTS ix_amendments_unit ON amendments (congress);"
    "CREATE TABLE IF NOT EXISTS legislation ("
    "bioguide TEXT, congress INTEGER, bill_type TEXT, bill_id TEXT, role TEXT);"
    "CREATE INDEX IF NOT EXISTS ix_legislation_bioguide ON legislation (bioguide);"
    "CREATE TABLE IF NOT EXISTS passage ("
    "bioguide TEXT NOT NULL, congress INTEGER NOT NULL, chamber TEXT NOT NULL, "
    "yea INTEGER NOT NULL DEFAULT 0, nay INTEGER NOT NULL DEFAULT 0, "
    "PRIMARY KEY (bioguide, congress, chamber));"
    "CREATE INDEX IF NOT EXISTS ix_passage_bioguide ON passage (bioguide);"
    "CREATE TABLE IF NOT EXISTS parsed (name TEXT PRIMARY KEY, data BLOB);"
    "CREATE TABLE IF NOT EXISTS loaded ("
    "kind TEXT NOT NULL, key TEXT NOT NULL, PRIMARY KEY (kind, key));"
)


_CREATED: set = set()


def _connect():
    """Open the cache database, creating and committing the schema once per file."""
    import os
    import sqlite3

    from openbb_congress_gov.utils.bulk import _cache_dir

    cache_dir = _cache_dir()
    if not cache_dir:
        return None
    path = os.path.join(cache_dir, "congress_gov.db")
    try:
        conn = sqlite3.connect(path, timeout=30)
        conn.execute("PRAGMA busy_timeout=30000")
        if path not in _CREATED:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(_SCHEMA)
            conn.commit()
            _CREATED.add(path)
        return conn
    except sqlite3.Error:
        return None


def _pack(value) -> bytes:
    """Serialize a structure to compressed JSON bytes."""
    import json
    import zlib

    return zlib.compress(json.dumps(value).encode("utf-8"))


def _unpack(blob: bytes):
    """Deserialize compressed JSON bytes."""
    import json
    import zlib

    return json.loads(zlib.decompress(blob))


def bills_loaded(congress: int, bill_type: str) -> bool:
    """Return True if a Congress/type's bills have been ingested."""
    conn = _connect()
    if conn is None:
        return False
    try:
        row = conn.execute(
            "SELECT 1 FROM loaded WHERE kind = 'bills' AND key = ?",
            (f"{congress}-{bill_type}",),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def _meta_rows(records: list, congress: int, bill_type: str) -> list:
    """Build one metadata row per bill (title/dates), shared by the legislation join."""
    rows = []
    for record in records:
        latest = record.get("latestAction") or {}
        rows.append(
            (
                record.get("bill_id"),
                congress,
                bill_type,
                record.get("title"),
                record.get("introducedDate"),
                latest.get("actionDate"),
                latest.get("text"),
            )
        )
    return rows


def _write_meta_and_legislation(conn, congress, bill_type, meta_rows, leg_rows) -> None:
    """Replace a Congress/type's bill metadata and sponsor rows (shared write path)."""
    conn.execute(
        "DELETE FROM bill_meta WHERE congress = ? AND bill_type = ?",
        (congress, bill_type),
    )
    conn.executemany(
        "INSERT OR REPLACE INTO bill_meta (bill_id, congress, bill_type, title, "
        "introduced_date, latest_action_date, latest_action) VALUES (?, ?, ?, ?, ?, ?, ?)",
        meta_rows,
    )
    conn.execute(
        "DELETE FROM legislation WHERE congress = ? AND bill_type = ?",
        (congress, bill_type),
    )
    conn.executemany(
        "INSERT INTO legislation (bioguide, congress, bill_type, bill_id, role) "
        "VALUES (?, ?, ?, ?, ?)",
        leg_rows,
    )


def ingest_bills(congress: int, bill_type: str, records: list, leg_rows: list) -> None:
    """Store a Congress/type's full bills (compressed), amendments, meta, and sponsors."""
    bill_rows = []
    amendment_rows = []
    for record in records:
        latest = record.get("latestAction") or {}
        bill_rows.append(
            (
                record.get("bill_id"),
                congress,
                bill_type,
                record.get("number"),
                record.get("type"),
                record.get("title"),
                record.get("originChamber"),
                record.get("originChamberCode"),
                (record.get("updateDate") or "")[:10],
                record.get("updateDateIncludingText"),
                latest.get("actionDate"),
                latest.get("text"),
                _pack(record),
            )
        )
        for amendment in record.get("amendments") or []:
            amendment_rows.append(
                (
                    amendment.get("amendment_id"),
                    congress,
                    (amendment.get("type") or "").lower(),
                    amendment.get("number"),
                    _pack(amendment),
                )
            )
    meta_rows = _meta_rows(records, congress, bill_type)

    conn = _connect()
    if conn is None:
        return
    try:
        conn.execute(
            "DELETE FROM bills WHERE congress = ? AND bill_type = ?",
            (congress, bill_type),
        )
        conn.executemany(
            "INSERT INTO bills (bill_id, congress, bill_type, number, type_display, "
            "title, origin_chamber, origin_chamber_code, update_date, "
            "update_date_text, latest_action_date, latest_action_text, record) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            bill_rows,
        )
        conn.executemany(
            "INSERT OR REPLACE INTO amendments "
            "(amendment_id, congress, amendment_type, number, record) "
            "VALUES (?, ?, ?, ?, ?)",
            amendment_rows,
        )
        _write_meta_and_legislation(conn, congress, bill_type, meta_rows, leg_rows)
        conn.execute(
            "INSERT OR IGNORE INTO loaded (kind, key) VALUES ('bills', ?)",
            (f"{congress}-{bill_type}",),
        )
        conn.commit()
    finally:
        conn.close()


def _bill_list_item(row) -> dict:
    """Build the slim bills-list shape from a bills row."""
    return {
        "updateDate": row[7],
        "bill_id": row[0],
        "congress": row[1],
        "number": row[2],
        "originChamber": row[3],
        "originChamberCode": row[4],
        "type": row[5],
        "title": row[6],
        "latestAction": {"actionDate": row[8], "text": row[9]},
        "updateDateIncludingText": row[10],
    }


def list_bills(
    congress: int,
    bill_types: list,
    start_date,
    end_date,
    limit,
    offset,
    sort_by: str,
) -> list:
    """Query the bills list for a Congress, filtered by type and update date."""
    if not bill_types:
        return []
    conn = _connect()
    if conn is None:
        return []
    try:
        placeholders = ",".join("?" * len(bill_types))
        clauses = [f"congress = ? AND bill_type IN ({placeholders})"]
        params: list = [congress, *bill_types]
        if start_date is not None:
            clauses.append("update_date != '' AND update_date >= ?")
            params.append(str(start_date))
        if end_date is not None:
            clauses.append("update_date != '' AND update_date <= ?")
            params.append(str(end_date))
        order = "DESC" if sort_by == "desc" else "ASC"
        sql = (
            "SELECT bill_id, congress, number, origin_chamber, origin_chamber_code, "  # noqa: S608
            "type_display, title, update_date, latest_action_date, "
            "latest_action_text, update_date_text FROM bills WHERE "
            + " AND ".join(clauses)
            + f" ORDER BY COALESCE(NULLIF(latest_action_date, ''), update_date) {order}"
            + f" LIMIT {-1 if limit == 0 else (limit or 100)} OFFSET {offset or 0}"
        )
        return [_bill_list_item(row) for row in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def get_bill(bill_id: str) -> dict | None:
    """Return a single bill's full record, or None if absent."""
    conn = _connect()
    if conn is None:
        return None
    try:
        row = conn.execute(
            "SELECT record FROM bills WHERE bill_id = ?", (bill_id,)
        ).fetchone()
        return _unpack(row[0]) if row else None
    finally:
        conn.close()


def list_amendments(congress: int, amendment_type: str | None) -> list:
    """Return a Congress's amendment records, optionally filtered by type."""
    conn = _connect()
    if conn is None:
        return []
    try:
        if amendment_type is None:
            rows = conn.execute(
                "SELECT record FROM amendments WHERE congress = ?", (congress,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT record FROM amendments WHERE congress = ? AND amendment_type = ?",
                (congress, amendment_type.lower()),
            ).fetchall()
        return [_unpack(row[0]) for row in rows]
    finally:
        conn.close()


def get_amendment(amendment_id: str) -> dict | None:
    """Return a single amendment's full record, or None if absent."""
    conn = _connect()
    if conn is None:
        return None
    try:
        row = conn.execute(
            "SELECT record FROM amendments WHERE amendment_id = ?", (amendment_id,)
        ).fetchone()
        return _unpack(row[0]) if row else None
    finally:
        conn.close()


def ingest_legislation(
    congress: int, bill_type: str, records: list, leg_rows: list
) -> None:
    """Store a Congress/type's bill metadata and sponsor rows (no full records)."""
    meta_rows = _meta_rows(records, congress, bill_type)
    conn = _connect()
    if conn is None:
        return
    try:
        _write_meta_and_legislation(conn, congress, bill_type, meta_rows, leg_rows)
        conn.execute(
            "INSERT OR IGNORE INTO loaded (kind, key) VALUES ('legislation', ?)",
            (f"{congress}-{bill_type}",),
        )
        conn.commit()
    finally:
        conn.close()


def compact() -> None:
    """Rebuild the database file to reclaim free space (VACUUM)."""
    conn = _connect()
    if conn is None:
        return
    try:
        conn.execute("VACUUM")
    finally:
        conn.close()


def get_legislation(bioguide: str, congresses: list) -> list:
    """Return a member's sponsored/cosponsored bills for the given Congresses."""
    if not congresses:
        return []
    conn = _connect()
    if conn is None:
        return []
    try:
        placeholders = ",".join("?" * len(congresses))
        rows = conn.execute(
            "SELECT l.bill_id, l.congress, l.role, m.title, m.introduced_date, "  # noqa: S608
            "m.latest_action_date, m.latest_action "
            "FROM legislation l LEFT JOIN bill_meta m ON l.bill_id = m.bill_id "
            f"WHERE l.bioguide = ? AND l.congress IN ({placeholders}) "
            "ORDER BY m.introduced_date DESC",
            (bioguide, *congresses),
        ).fetchall()
        return [
            {
                "bill_id": row[0],
                "congress": row[1],
                "role": row[2],
                "title": row[3],
                "introduced_date": row[4],
                "latest_action_date": row[5],
                "latest_action": row[6],
            }
            for row in rows
        ]
    finally:
        conn.close()


def loaded_keys(kind: str) -> set:
    """Return the set of already-ingested keys for a data kind."""
    conn = _connect()
    if conn is None:
        return set()
    try:
        rows = conn.execute("SELECT key FROM loaded WHERE kind = ?", (kind,))
        return {row[0] for row in rows}
    finally:
        conn.close()


def get_passage(bioguide: str) -> tuple[int, int] | None:
    """Return a member's career ``(yea, nay)`` passage tally, or None if absent."""
    conn = _connect()
    if conn is None:
        return None
    try:
        row = conn.execute(
            "SELECT SUM(yea), SUM(nay) FROM passage WHERE bioguide = ?", (bioguide,)
        ).fetchone()
        return (row[0], row[1]) if row and row[0] is not None else None
    finally:
        conn.close()


def add_passage(congress: int, chamber: str, tallies: dict) -> None:
    """Replace one Congress/chamber's passage tallies, marking the unit ingested.

    Storing per Congress/chamber (rather than a single accumulated row) makes
    re-ingestion idempotent: a refreshed Voteview file simply overwrites that
    unit's rows instead of double-counting into a running total.
    """
    conn = _connect()
    if conn is None:
        return
    try:
        conn.execute(
            "DELETE FROM passage WHERE congress = ? AND chamber = ?",
            (congress, chamber),
        )
        conn.executemany(
            "INSERT INTO passage (bioguide, congress, chamber, yea, nay) "
            "VALUES (?, ?, ?, ?, ?)",
            [(b, congress, chamber, y, n) for b, (y, n) in tallies.items()],
        )
        conn.execute(
            "INSERT OR IGNORE INTO loaded (kind, key) VALUES ('passage', ?)",
            (f"{congress}-{chamber}",),
        )
        conn.commit()
    finally:
        conn.close()


def get_parsed(name: str):
    """Return a cached parsed structure by name, or None if absent."""
    conn = _connect()
    if conn is None:
        return None
    try:
        row = conn.execute("SELECT data FROM parsed WHERE name = ?", (name,)).fetchone()
        return _unpack(row[0]) if row else None
    finally:
        conn.close()


def delete_parsed(name: str) -> None:
    """Remove a cached parsed structure by name, if present."""
    conn = _connect()
    if conn is None:
        return
    try:
        conn.execute("DELETE FROM parsed WHERE name = ?", (name,))
        conn.commit()
    finally:
        conn.close()


def put_parsed(name: str, value) -> None:
    """Store a parsed structure under a name."""
    payload = _pack(value)
    conn = _connect()
    if conn is None:
        return
    try:
        conn.execute(
            "INSERT OR REPLACE INTO parsed (name, data) VALUES (?, ?)",
            (name, payload),
        )
        conn.commit()
    finally:
        conn.close()


def reset() -> None:
    """Clear all cached data (used by tests and forced rebuilds)."""
    conn = _connect()
    if conn is None:
        return
    try:
        conn.executescript(
            "DELETE FROM bills; DELETE FROM bill_meta; DELETE FROM amendments; "
            "DELETE FROM legislation; DELETE FROM passage; "
            "DELETE FROM parsed; DELETE FROM loaded;"
        )
        conn.commit()
    finally:
        conn.close()
