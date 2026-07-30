"""Compact plain-text record/replay cassette layer for the FFIEC report pipelines.

The FFIEC report fetchers reach the live site through four layers worth
recording: the ``ubpr_report._post`` router (``POST /Public/router/Search``,
which returns the report-builder grid as JSON), the
``guide.fetch_guide_concepts`` enrichment (which resolves UBPR concept codes to a
small ``{code: {description, narrative}}`` dict), the ``concepts.concept_index``
join (which resolves each concept code to its ``{name, narrative, monetary,
is_text}`` metadata from the CDR XBRL taxonomy and the MDRM dictionary), and the
browser-impersonating ``cdr._get_session`` (the ``UbprReport.aspx`` HTML the
peer-group/state-average reports render).

A cassette is fully self-contained: it stores the report-builder data, the parsed
guide concepts, and the (filtered) concept-index metadata - never the raw
Interactive User Guide HTML, never the binary CDR taxonomy/MDRM source, and never
a ZIP. The Interactive User Guide (``InteractiveUserGuide.aspx``) and the
taxonomy/MDRM downloads run hundreds of kilobytes to megabytes each; recording
them directly is what bloated the previous cassettes. Wrapping
:func:`guide.fetch_guide_concepts` and :func:`concepts.concept_index` as functions
and storing their small returned dicts captures the same enrichment in a few
kilobytes, and the recording session refuses to capture any
``InteractiveUserGuide.aspx`` request so the raw guide HTML can never leak back in.

The concept index returned for ``ubpr_ratio_single`` covers thousands of concept
codes; the recording filters it to only the codes the captured section grid
actually looks up, so the cassette stays small and the replay still serves every
join the parse performs.

Cassettes are pure text. The whole request -> response map is serialized with
``json.dumps(map, indent=2, sort_keys=True)`` under
``tests/cassettes/ffiec/<pipeline>.json`` - readable, diffable, no gzip and no
binary. Router responses are stored as their parsed JSON, ``fetch_guide_concepts``
and ``concept_index`` results as their dicts, and session ``GET``/``POST``
responses as ``.text``. :func:`replay` serves every recorded layer from the
cassette and raises on any unrecorded key, so a cassette integration test needs no
network and no pre-warmed cache.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any

CASSETTE_DIR = Path(__file__).parent / "cassettes" / "ffiec"

# Any guide URL is refused by the recording session: the parsed concepts are
# captured by wrapping ``fetch_guide_concepts`` instead, so the raw multi-hundred
# kilobyte guide HTML never enters a cassette.
_GUIDE_MARKER = "InteractiveUserGuide.aspx"

# The JSON router endpoint. ``ubpr_report._post`` already records every router
# call as its parsed JSON, so the recording session skips this URL to avoid
# storing each router response twice (once parsed, once as raw POST text).
_ROUTER_MARKER = "/Public/router/Search"


def _post_rebind_targets() -> list[tuple[Any, str]]:
    """Return every module that re-exports ``ubpr_report._post`` at module level.

    Most callers re-import ``_post`` inside the function body, so patching
    ``ubpr_report._post`` reaches them at call time. ``executive_summary_report``
    binds ``_post`` (and ``report_cycles``) at import, so its stale references must
    be patched directly for the recording/replay to intercept its router calls.
    """
    from openbb_federal_reserve.utils import executive_summary_report, ubpr_report

    return [(ubpr_report, "_post"), (executive_summary_report, "_post")]


# Sentinel store key marking a cassette captured for a single reporting cycle.
# The peer-group and state-average reports render the section grid as HTML keyed
# on the cycle id list, so capturing one cycle keeps that HTML small; replay must
# then cap ``report_cycles`` the same way so its rebuilt URL matches the recording.
_SINGLE_CYCLE_KEY = "__single_cycle__"


class UnrecordedRequest(KeyError):
    """Raised when a replayed request has no entry in the cassette."""


def _post_key(requestor_id: str, criteria: dict[str, Any]) -> str:
    """Build the request key for a ``ubpr_report._post`` call."""
    return f"post {requestor_id} {json.dumps(criteria, sort_keys=True)}"


def _guide_key(concepts: list[str], lines: dict[str, str] | None) -> str:
    """Build the request key for a ``fetch_guide_concepts`` call.

    The key is the sorted concept set plus whether a caller-supplied line map was
    passed, so the recorded enrichment is matched independently of concept order.
    """
    scope = "scoped" if lines else "global"
    return f"guide {scope} {json.dumps(sorted(set(concepts)))}"


def _index_key(product: str, form_type: str | None) -> str:
    """Build the request key for a ``concept_index`` call."""
    return f"index {product} {form_type or ''}"


def _body_str(data: Any) -> str:
    """Normalize a request body (str/bytes/mapping) to a stable string key part."""
    if data is None:
        return ""
    if isinstance(data, (bytes, bytearray)):
        return bytes(data).decode("utf-8", "ignore")
    if isinstance(data, str):
        return data
    return json.dumps(data, sort_keys=True)


def _session_key(method: str, url: str, body: str) -> str:
    """Build the request key for a session call: ``"METHOD url body"``."""
    return f"{method} {url} {body}"


def _as_text(value: Any) -> str:
    """Decode a recorded response body to text, never leaving binary behind."""
    if isinstance(value, str):
        return value
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("utf-8")
    return json.dumps(value)


class _AccessTrackingIndex(dict):
    """A concept-index ``dict`` that records every code looked up.

    The report pipelines read the index by ``__getitem__`` and ``.get`` with a
    concept code; the recorder filters the captured index to exactly those codes so
    the cassette holds only the metadata the parse joins against.
    """

    def __init__(self, data: dict[str, Any], seen: set[str]) -> None:
        """Wrap ``data`` and accumulate accessed keys into the shared ``seen`` set."""
        super().__init__(data)
        self._seen = seen

    def __getitem__(self, key: Any) -> Any:
        """Record the lookup, then return the underlying value."""
        if isinstance(key, str):
            self._seen.add(key)
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        """Record the lookup, then return the underlying value or ``default``."""
        if isinstance(key, str):
            self._seen.add(key)
        return super().get(key, default)


class _ReplayResponse:
    """A minimal response exposing ``.text``, ``.content`` and ``.json()``."""

    def __init__(self, body: Any, *, is_json: bool) -> None:
        """Hold the recorded body and whether it was a parsed-JSON router body."""
        self._body = body
        self._is_json = is_json
        self.status_code = 200

    @property
    def text(self) -> str:
        """Return the recorded body as text."""
        return _as_text(self._body)

    @property
    def content(self) -> bytes:
        """Return the recorded body as UTF-8 bytes."""
        return self.text.encode("utf-8")

    def json(self) -> Any:
        """Return the recorded body parsed as JSON."""
        if self._is_json:
            return self._body
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        """No-op; recorded responses are always successful (200)."""


class _ReplaySession:
    """A fake transport session serving recorded ``.get``/``.post`` responses."""

    def __init__(self, store: dict[str, str]) -> None:
        """Bind the session to the cassette store."""
        self._store = store

    def _serve(self, method: str, url: str, body: str) -> _ReplayResponse:
        """Look up and return the recorded response for a session request."""
        key = _session_key(method, url, body)
        if key not in self._store:
            raise UnrecordedRequest(
                f"No recorded session {method} for: {url}"
                + (f" (body: {body[:120]})" if body else "")
            )
        return _ReplayResponse(self._store[key], is_json=False)

    def get(self, url: str, **kwargs: Any) -> _ReplayResponse:
        """Serve a recorded GET response."""
        return self._serve("GET", url, "")

    def post(self, url: str, **kwargs: Any) -> _ReplayResponse:
        """Serve a recorded POST response, keyed by its request body."""
        return self._serve("POST", url, _body_str(kwargs.get("data")))


class Recorder:
    """Capture every FFIEC report-builder call into a request -> response text map.

    The router (:func:`ubpr_report._post`), the guide enrichment
    (:func:`guide.fetch_guide_concepts`), the concept-index join
    (:func:`concepts.concept_index`) and the report-page session
    (:func:`cdr._get_session`) are wrapped; the session refuses to record any
    ``InteractiveUserGuide.aspx`` request so the raw guide HTML never enters the
    cassette - that enrichment is captured as the parsed concept dict instead.
    """

    def __init__(self) -> None:
        """Initialize the empty recording store."""
        self.store: dict[str, str] = {}
        # While the guide enrichment runs, its own internal router/session traffic
        # is suppressed: only its small parsed result is kept, not the per-concept
        # line-resolution posts it makes to learn which report line each concept
        # appears on.
        self._in_guide = False
        # When a single-cycle capture trims the report-page sparkline history, the
        # recorded cycle's ``M/D/YYYY`` dates are the only points the replay reads.
        self._single_cycle = False
        self._keep_dates: frozenset[str] | None = None
        # The concept codes the pipeline actually looked up in the full index. The
        # captured index is filtered to these so the cassette stays small.
        self._index_seen: set[str] = set()
        # Each ``concept_index`` call's full result, keyed by its request key; the
        # filtered view is written on :meth:`save` once every lookup has run.
        self._index_full: dict[str, dict[str, Any]] = {}
        # The real ``cache.cached`` and ``cdr._get_session`` captured before the
        # recording patches them, so the concept-index producer's taxonomy/MDRM
        # downloads run through the on-disk cache and the real session - never the
        # recording proxy - and so are not stored in the cassette.
        self._real_cached: Callable[..., Any] | None = None
        self._real_get_session: Callable[[], Any] | None = None

    def _wrap_post(self) -> Callable[..., Any]:
        """Return a ``ubpr_report._post`` replacement that records its result."""
        from openbb_federal_reserve.utils import ubpr_report

        original = ubpr_report._post

        def recording_post(requestor_id: str, criteria: dict[str, Any]) -> Any:
            """Call the real router, recording the parsed JSON keyed by criteria."""
            result = original(requestor_id, criteria)
            if not self._in_guide:
                self.store[_post_key(requestor_id, criteria)] = json.dumps(result)
            return result

        return recording_post

    def _wrap_guide(self) -> Callable[..., Any]:
        """Return a ``fetch_guide_concepts`` replacement that records its result."""
        from openbb_federal_reserve.utils import guide

        original = guide.fetch_guide_concepts

        def recording_guide(
            concepts: list[str], lines: dict[str, str] | None = None
        ) -> dict[str, dict[str, str]]:
            """Call the real guide client and record only the parsed concept dict."""
            self._in_guide = True
            try:
                result = original(concepts, lines)
            finally:
                self._in_guide = False
            self.store[_guide_key(concepts, lines)] = json.dumps(result)
            return result

        return recording_guide

    def _wrap_index(self) -> Callable[..., Any]:
        """Return a ``concept_index`` replacement that records its filtered result.

        The real (large) index is returned to the pipeline through an
        access-tracking wrapper so the parse behaves identically; the captured full
        result is filtered on :meth:`save` to the codes the pipeline looked up.
        """
        from openbb_federal_reserve.utils import cache, cdr, concepts

        original = concepts.concept_index

        def recording_index(
            product: str = "ubpr_ratio_single", form_type: str | None = None
        ) -> dict[str, dict[str, Any]]:
            """Build the real index, then track every concept code looked up.

            The taxonomy/MDRM join runs against the on-disk cache and the real
            session (not the recording proxy), so its binary source downloads are
            cached rather than recorded; only the small parsed index is captured.
            """
            patched_cached = cache.cached
            patched_session = cdr._get_session
            cache.cached = self._real_cached  # ty: ignore[invalid-assignment]
            cdr._get_session = self._real_get_session  # ty: ignore[invalid-assignment]
            try:
                result = original(product, form_type)
            finally:
                cache.cached = patched_cached
                cdr._get_session = patched_session
            self._index_full[_index_key(product, form_type)] = result
            return _AccessTrackingIndex(result, self._index_seen)

        return recording_index

    def _wrap_session(self, get_session: Callable[[], Any]) -> Any:
        """Return a proxy session recording report-page bodies, never guide HTML."""
        real = get_session()
        recorder = self

        class _RecordingSession:
            """Pass calls to the real session, recording report-page bodies as text.

            A guide page (``InteractiveUserGuide.aspx``) is served but never
            recorded; the parsed concepts come from the wrapped
            ``fetch_guide_concepts`` so the raw guide HTML stays out of the cassette.
            """

            def _skip(self, url: str) -> bool:
                """Return whether a session call must not enter the cassette.

                Guide pages are captured as parsed concepts, router calls are
                captured by the wrapped ``_post``, and any traffic the guide
                enrichment makes while resolving its concepts is suppressed.
                """
                return (
                    recorder._in_guide or _GUIDE_MARKER in url or _ROUTER_MARKER in url
                )

            def get(self, url: str, **kwargs: Any) -> Any:
                """Record a report-page GET response (text)."""
                response = real.get(url, **kwargs)
                if not self._skip(url):
                    recorder.store[_session_key("GET", url, "")] = response.text
                return response

            def post(self, url: str, **kwargs: Any) -> Any:
                """Record a report-page POST response (text)."""
                response = real.post(url, **kwargs)
                if not self._skip(url):
                    key = _session_key("POST", url, _body_str(kwargs.get("data")))
                    recorder.store[key] = recorder._trim_history(
                        recorder._session_text(response)
                    )
                return response

        return _RecordingSession()

    def _trim_history(self, html: str) -> str:
        """Drop unread sparkline/descriptor payload from a single-cycle report grid.

        The ``UbprReport.aspx`` grid embeds, per cell, the full quarterly history
        in a ``data-graph_set`` JSON sparkline, a second full annual-trend history
        in a ``data-graph_subset`` blob no parser reads at all, and a verbose
        ``data-graph_descriptor`` chart-config blob - regardless of the requested
        cycle window. A single-cycle capture (and its single-cycle replay) reads
        only the captured cycle's ``data-graph_set`` value and the descriptor's
        ``conceptname``; the ``data-graph_subset`` blob and every other point and
        field is inert. Dropping the subset entirely and keeping only the read
        points shrinks the report HTML by an order of magnitude without changing a
        single replayed value. When the capture is not single-cycle the HTML is
        returned unchanged.
        """
        import html as _html
        import re

        if not self._single_cycle:
            return html
        if self._keep_dates is None:
            self._resolve_keep_dates()
        if not self._keep_dates:
            return html
        keep: frozenset[str] = self._keep_dates

        def _trim_set(match: re.Match[str]) -> str:
            try:
                points = json.loads(_html.unescape(match.group(1)))
            except (ValueError, TypeError):
                return match.group(0)
            kept = [p for p in points if str(p.get("category")) in keep]
            payload = json.dumps(kept, separators=(",", ":"))
            return 'data-graph_set="' + payload.replace('"', "&quot;") + '"'

        def _trim_descriptor(match: re.Match[str]) -> str:
            try:
                entries = json.loads(_html.unescape(match.group(1)))
            except (ValueError, TypeError):
                return match.group(0)
            concept = next(
                (
                    str(entry.get("conceptname"))
                    for entry in entries
                    if isinstance(entry, dict) and entry.get("conceptname")
                ),
                "",
            )
            payload = json.dumps([{"conceptname": concept}], separators=(",", ":"))
            return 'data-graph_descriptor="' + payload.replace('"', "&quot;") + '"'

        html = re.sub(r'\sdata-graph_subset="[^"]*"', "", html)
        html = re.sub(r'data-graph_set="([^"]*)"', _trim_set, html)
        return re.sub(r'data-graph_descriptor="([^"]*)"', _trim_descriptor, html)

    def _resolve_keep_dates(self) -> None:
        """Compute the captured single cycle's ``M/D/YYYY`` dates from the store."""
        from datetime import datetime

        rows: list[dict[str, str]] = []
        for key, value in self.store.items():
            if key.startswith("post PeriodsEndDateList"):
                rows = [r for r in json.loads(value) if r.get("reportingcycleid")]
                break
        rows.sort(
            key=lambda r: datetime.strptime(r["enddateformatted"], "%m/%d/%Y"),
            reverse=True,
        )
        dates: set[str] = set()
        for row in rows[:1]:
            month, day, year = row["enddateformatted"].split("/")
            dates.add(f"{int(month)}/{int(day)}/{year}")
        self._keep_dates = frozenset(dates)

    @staticmethod
    def _session_text(response: Any) -> str:
        """Return a session response body as text, decoding ``.content``.

        Raises a clear error on a non-text (binary) payload so a pipeline that
        downloads an XBRL/ZIP bulk file fails the capture loudly rather than
        writing a corrupt, lossy cassette.
        """
        content = response.content
        if content[:2] == b"PK":
            raise ValueError(
                "A binary (ZIP/XBRL) payload cannot be stored in a plain-text"
                " cassette; this pipeline is out of scope for the text layer."
            )
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return response.text

    @contextmanager
    def patch(self, *, single_cycle: bool = False):
        """Patch the router, guide, index and session transports for the context.

        Parameters
        ----------
        single_cycle : bool
            When True, ``report_cycles`` is capped to its single newest cycle for
            the capture so the ``UbprReport.aspx`` HTML the peer-group and
            state-average reports render stays small (one reporting period rather
            than five).
        """
        from openbb_federal_reserve.utils import (
            cache,
            cdr,
            concepts,
            guide,
            ubpr_report,
        )

        self._real_cached = cache.cached
        self._real_get_session = cdr._get_session
        cdr_session = self._wrap_session(cdr._get_session)
        recording_post = self._wrap_post()
        originals: dict[tuple[Any, str], Any] = {
            (guide, "fetch_guide_concepts"): guide.fetch_guide_concepts,
            (concepts, "concept_index"): concepts.concept_index,
            (cdr, "_get_session"): cdr._get_session,
            (cache, "cached"): cache.cached,
        }
        for target in _post_rebind_targets():
            originals[target] = getattr(*target)

        def bypass_cached(key: Any, ttl: Any, producer: Callable[[], Any]) -> Any:
            """Run every report-section producer so its transports are captured.

            The concept index, guide concepts and router calls are captured by their
            own wrappers; here every cached producer runs against the live
            transports so the recording sees the call even when a prior run left the
            result cached.
            """
            return producer()

        for module, attr in _post_rebind_targets():
            setattr(module, attr, recording_post)
        guide.fetch_guide_concepts = self._wrap_guide()  # ty: ignore[invalid-assignment]
        concepts.concept_index = self._wrap_index()  # ty: ignore[invalid-assignment]
        cdr._get_session = lambda: cdr_session  # ty: ignore[invalid-assignment]
        cache.cached = bypass_cached  # ty: ignore[invalid-assignment]
        if single_cycle:
            self._single_cycle = True
            self.store[_SINGLE_CYCLE_KEY] = "true"
            real_cycles = ubpr_report.report_cycles
            originals[(ubpr_report, "report_cycles")] = real_cycles
            ubpr_report.report_cycles = (  # ty: ignore[invalid-assignment]
                lambda: real_cycles()[:1]
            )
        try:
            yield self
        finally:
            for (module, name), value in originals.items():
                setattr(module, name, value)

    def _record_filtered_index(self) -> None:
        """Store each captured concept index filtered to the looked-up codes."""
        for key, full in self._index_full.items():
            filtered = {code: full[code] for code in self._index_seen if code in full}
            self.store[key] = json.dumps(filtered)

    def save(self, name: str) -> int:
        """Serialize the recording to ``cassettes/ffiec/<name>.json``.

        Returns
        -------
        int
            The plain-text cassette's size in bytes.
        """
        self._record_filtered_index()
        CASSETTE_DIR.mkdir(parents=True, exist_ok=True)
        path = CASSETTE_DIR / f"{name}.json"
        payload = json.dumps(self.store, indent=2, sort_keys=True)
        path.write_text(payload, encoding="utf-8")
        return len(payload.encode("utf-8"))


@contextmanager
def record(name: str, *, single_cycle: bool = False):
    """Record every FFIEC report-builder call, saving the cassette on clean exit.

    Yields the :class:`Recorder`; on exit the in-memory store is written to
    ``cassettes/ffiec/<name>.json`` as plain text. When ``single_cycle`` is True
    the capture is capped to the newest reporting cycle so report-page HTML stays
    small.
    """
    recorder = Recorder()
    with recorder.patch(single_cycle=single_cycle):
        yield recorder
    recorder.save(name)


def _load(name: str) -> dict[str, str]:
    """Load a cassette's request -> response map from its plain-text file."""
    path = CASSETTE_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def replay(name: str):
    """Serve a cassette's recorded responses, bypassing the on-disk cache.

    Patches the router, guide, concept-index and session transports to serve every
    layer from the recording and replaces ``utils.cache.cached`` with a shim that
    runs the report-section producers against the recording, so the parse/transform
    producers run against the recorded transports rather than a live network or a
    pre-warmed cache. An unrecorded request raises :class:`UnrecordedRequest`.
    """
    from openbb_federal_reserve.utils import cache, cdr, concepts, guide, ubpr_report

    store = _load(name)
    cdr_session = _ReplaySession(store)

    def replay_post(requestor_id: str, criteria: dict[str, Any]) -> Any:
        """Serve the recorded router JSON for a ``_post`` request."""
        key = _post_key(requestor_id, criteria)
        if key not in store:
            raise UnrecordedRequest(f"No recorded _post for: {requestor_id} {criteria}")
        return json.loads(store[key])

    def replay_guide(
        concepts_arg: list[str], lines: dict[str, str] | None = None
    ) -> dict[str, dict[str, str]]:
        """Serve the recorded parsed concept dict for a guide request."""
        key = _guide_key(concepts_arg, lines)
        if key not in store:
            raise UnrecordedRequest(
                f"No recorded guide concepts for: {sorted(concepts_arg)}"
            )
        return json.loads(store[key])

    def replay_index(
        product: str = "ubpr_ratio_single", form_type: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """Serve the recorded filtered concept index for an ``concept_index`` call."""
        key = _index_key(product, form_type)
        if key not in store:
            raise UnrecordedRequest(
                f"No recorded concept_index for: {product} {form_type or ''}"
            )
        return json.loads(store[key])

    def bypass_cached(key: Any, ttl: Any, producer: Callable[[], Any]) -> Any:
        """Run every producer against the recording so it exercises the cassette."""
        return producer()

    originals: dict[tuple[Any, str], Any] = {
        (guide, "fetch_guide_concepts"): guide.fetch_guide_concepts,
        (concepts, "concept_index"): concepts.concept_index,
        (cdr, "_get_session"): cdr._get_session,
        (cache, "cached"): cache.cached,
    }
    for target in _post_rebind_targets():
        originals[target] = getattr(*target)
        setattr(*target, replay_post)
    guide.fetch_guide_concepts = replay_guide  # ty: ignore[invalid-assignment]
    concepts.concept_index = replay_index  # ty: ignore[invalid-assignment]
    cdr._get_session = lambda: cdr_session  # ty: ignore[invalid-assignment]
    cache.cached = bypass_cached  # ty: ignore[invalid-assignment]
    if store.get(_SINGLE_CYCLE_KEY):
        # The cassette captured one cycle, so the report-page URL was built from a
        # single cycle id; cap ``report_cycles`` to match and serve that recording.
        real_cycles = ubpr_report.report_cycles
        originals[(ubpr_report, "report_cycles")] = real_cycles
        ubpr_report.report_cycles = (  # ty: ignore[invalid-assignment]
            lambda: real_cycles()[:1]
        )
    try:
        yield store
    finally:
        for (module, name_), value in originals.items():
            setattr(module, name_, value)
