"""Live SDMX 2.1 structure fallbacks."""

from __future__ import annotations

from openbb_ecb.utils.metadata._constants import AGENCY, BASE_URL, NS, STRUCTURE_HEADERS
from openbb_ecb.utils.metadata._helpers import en_text
from openbb_ecb.utils.metadata._typing import MetadataBase


class LoaderMixin(MetadataBase):
    """Fetch structure artefacts not present in the shipped cache."""

    def _fetch_codelist_live(
        self, codelist_id: str, agency: str = AGENCY, version: str = "latest"
    ) -> dict[str, str]:
        """Fetch a single codelist ``{code_id: label}`` from the live API."""
        from defusedxml import ElementTree as DET
        from openbb_core.provider.utils.helpers import make_request

        url = f"{BASE_URL}/codelist/{agency}/{codelist_id}/{version}?detail=full"
        try:
            response = make_request(url, headers=STRUCTURE_HEADERS)
            if response.status_code != 200:
                return {}
            root = DET.fromstring(response.content)
        except Exception:  # noqa: BLE001
            return {}

        out: dict[str, str] = {}
        for cl in root.findall(".//str:Codelist", NS):
            for code in cl.findall("str:Code", NS):
                code_id = code.get("id")
                if code_id:
                    out[code_id] = en_text(code, "Name") or code_id
        if out:
            self.codelists[codelist_id] = out
        return out

    def _fetch_available_constraint(
        self, flow_ref: str, key: str
    ) -> dict[str, list[str]]:
        """Return ``{dimension_id: [available_value, ...]}`` for a partial key."""
        from defusedxml import ElementTree as DET
        from openbb_core.provider.utils.helpers import make_request

        url = (
            f"{BASE_URL}/availableconstraint/{flow_ref}/{key or 'all'}"
            "?mode=available&references=none"
        )
        try:
            response = make_request(url, headers=STRUCTURE_HEADERS)
            if response.status_code != 200:
                return {}
            root = DET.fromstring(response.content)
        except Exception:  # noqa: BLE001
            return {}

        out: dict[str, list[str]] = {}
        for kv in root.iter():
            if kv.tag.rsplit("}", 1)[-1] != "KeyValue":
                continue
            dim_id = kv.get("id")
            if not dim_id:
                continue
            values = [
                (v.text or "").strip()
                for v in kv
                if v.tag.rsplit("}", 1)[-1] == "Value" and (v.text or "").strip()
            ]
            if values:
                out[dim_id] = values
        return out
