"""Live API loader mixin."""

from __future__ import annotations

import json
import warnings

from openbb_core.app.model.abstract.warning import OpenBBWarning

from openbb_imf.utils.metadata._constants import BASE_URL
from openbb_imf.utils.metadata._typing import _MixinBase


def _extract_codelist_payload(codelist_obj: dict) -> tuple[dict, dict]:
    """Return ``({code_id: label}, {code_id: description})`` for a codelist."""
    labels: dict = {}
    descs: dict = {}
    for code in codelist_obj.get("codes", []):
        code_id = code.get("id")
        if not code_id:
            continue
        label = code.get("names", {}).get("en") or code.get("name") or code_id
        description = (
            code.get("descriptions", {}).get("en", "")
            or code.get("description", "")
            or ""
        )
        if not description and label:
            description = label
        labels[code_id] = label
        descs[code_id] = description
    return labels, descs


class LoaderMixin(_MixinBase):
    """Codelist fetchers for cache backfill."""

    def _fetch_single_codelist(
        self: _MixinBase, agency_id: str, codelist_id: str
    ) -> bool:
        """Fetch one codelist by id and merge it into the cache."""
        from openbb_core.provider.utils.helpers import make_request
        from requests.exceptions import RequestException

        if codelist_id in self._codelist_cache and self._codelist_cache.get(
            codelist_id
        ):
            return True

        url = (
            f"{BASE_URL}/structure/codelist/{agency_id}/{codelist_id}"
            "?detail=full&references=none"
        )
        headers = {"Accept": "application/json"}

        try:
            response = make_request(url, headers=headers, timeout=5)
            if response.status_code != 200:
                return False
            json_response: dict = response.json()
        except (json.JSONDecodeError, RequestException):
            return False

        codelists_in_response = json_response.get("data", {}).get("codelists", [])
        if not codelists_in_response:
            return False

        with self._codelist_lock:
            for codelist_obj in codelists_in_response:
                cl_id = codelist_obj.get("id")
                if not cl_id:
                    continue
                labels, descs = _extract_codelist_payload(codelist_obj)
                self._codelist_cache[cl_id] = labels
                self._codelist_descriptions[cl_id] = descs

        return codelist_id in self._codelist_cache

    def _bulk_fetch_and_cache_codelists(
        self: _MixinBase, agency_id: str, dataflow_id: str
    ) -> None:
        """Fetch every codelist referenced by ``dataflow_id``."""
        from openbb_core.provider.utils.helpers import make_request
        from requests.exceptions import RequestException

        url = (
            f"{BASE_URL}/structure/codelist/{agency_id},{dataflow_id}/all"
            "?detail=full&references=none"
        )
        headers = {"Accept": "application/json"}

        try:
            response = make_request(url, headers=headers)
            json_response: dict = response.json()
        except (json.JSONDecodeError, RequestException) as e:
            warnings.warn(
                f"Could not bulk fetch codelists for {agency_id}/{dataflow_id}: "
                f"{e} -> {url}",
                OpenBBWarning,
            )
            return

        codelists_in_response = json_response.get("data", {}).get("codelists", [])
        with self._codelist_lock:
            for codelist_obj in codelists_in_response:
                cl_id = codelist_obj.get("id")
                if not cl_id:
                    continue
                labels, descs = _extract_codelist_payload(codelist_obj)
                self._codelist_cache[cl_id] = labels
                self._codelist_descriptions[cl_id] = descs

    def _get_codelist_map(
        self: _MixinBase,
        codelist_id: str,
        agency_id: str,
        dataflow_id: str,
        include_descriptions: bool = False,
    ) -> dict:
        """Return ``{code_id: label}`` or ``{code_id: {name, description}}``."""
        with self._codelist_lock:
            if codelist_id in self._codelist_cache:
                return _shape_codelist(
                    self._codelist_cache[codelist_id],
                    self._codelist_descriptions.get(codelist_id, {}),
                    include_descriptions=include_descriptions,
                )

        self._bulk_fetch_and_cache_codelists(agency_id, dataflow_id)

        with self._codelist_lock:
            if codelist_id in self._codelist_cache:
                return _shape_codelist(
                    self._codelist_cache[codelist_id],
                    self._codelist_descriptions.get(codelist_id, {}),
                    include_descriptions=include_descriptions,
                )

        warnings.warn(f"Codelist '{codelist_id}' not found.", OpenBBWarning)
        return {}


def _shape_codelist(
    labels: dict, descriptions: dict, *, include_descriptions: bool
) -> dict:
    """Format the cached codelist into the requested shape."""
    if include_descriptions and descriptions:
        return {
            code_id: {
                "name": label,
                "description": descriptions.get(code_id, ""),
            }
            for code_id, label in labels.items()
        }
    return labels.copy()
