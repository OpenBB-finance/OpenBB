"""Federal Reserve NIC Institution Structure Model."""

from datetime import date
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.models.institutions import _parse_nic_date

_RELN_LVL_MAP = {
    "1": "Direct",
    "2": "Indirect",
    "3": "2(g)(3)",
    "4": "Debt Previously Contracted",
}

_CTRL_IND_MAP = {
    "0": "Not applicable",
    "1": "Controlled",
    "2": "Non-controlled",
}

_EQUITY_IND_MAP = {
    "0": "Other basis of control",
    "1": "Ownership/control in a BHC, SLHC, bank or FBO (exact percent)",
    "2": "Ownership/control in a non-banking company (bracketed percent)",
}

_REG_IND_MAP = {
    "1": "Regulated",
    "2": "Unregulated",
}

_REASON_TERM_RELN_MAP = {
    "0": "Not applicable (ongoing relationship)",
    "1": "Relationship terminated, no remaining basis",
    "2": "Parent sold or transferred control of Offspring",
    "3": "Offspring liquidated or merged",
    "4": "Control fell below regulatory reportable level",
    "5": "Parent ceased to be controlled or reportable",
    "6": "Change to regulatory reporting criteria",
}

_TRNSFM_CD_MAP = {
    "1": "Charter Discontinued (Merger or Purchase & Assumption)",
    "5": "Split",
    "7": "Sale of Assets",
    "9": "Charter Retained (Merger or Purchase & Assumption)",
    "50": "Failure, Government Assistance Provided",
}

_ACCT_METHOD_MAP = {
    "0": "Not applicable",
    "1": "Pooling of interests",
    "2": "Purchase/Acquisition",
}


class FederalReserveInstitutionStructureQueryParams(QueryParams):
    """Federal Reserve NIC Institution Structure Query Parameters."""

    __json_schema_extra__ = {
        "kind": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Ownership relationships (hierarchy)",
                        "value": "relationships",
                    },
                    {
                        "label": "Transformations (mergers and acquisitions)",
                        "value": "transformations",
                    },
                ]
            }
        }
    }

    kind: Literal["relationships", "transformations"] = Field(
        default="relationships",
        description="Hierarchy ownership 'relationships' or merger/acquisition"
        " 'transformations'.",
    )
    rssd_id: str | None = Field(
        default=None,
        description="Filter to records referencing this RSSD identifier.",
    )


class FederalReserveInstitutionStructureData(Data):
    """Federal Reserve NIC Institution Structure Data."""

    offspring_name: str | None = Field(
        default=None,
        description="The name of the offspring (owned/controlled subsidiary).",
    )
    parent_name: str | None = Field(
        default=None, description="The name of the parent (owner/controller)."
    )
    successor_name: str | None = Field(
        default=None, description="The name of the successor (survivor)."
    )
    predecessor_name: str | None = Field(
        default=None, description="The name of the predecessor (non-survivor)."
    )
    relationship_level: str | None = Field(
        default=None, description="Whether the relationship is direct or indirect."
    )
    control_indicator: str | None = Field(
        default=None, description="Whether the parent controls the offspring."
    )
    equity_indicator: str | None = Field(
        default=None, description="The form of ownership or control."
    )
    percent_equity: float | None = Field(
        default=None, description="The parent's percent of equity voting control."
    )
    percent_other: float | None = Field(
        default=None, description="The parent's percent of other voting control."
    )
    percent_equity_bracket: str | None = Field(
        default=None, description="The bracketed range of the equity percent."
    )
    regulated_indicator: str | None = Field(
        default=None, description="Whether the relationship is regulated."
    )
    reason_relationship_terminated: str | None = Field(
        default=None, description="The reason the relationship was terminated."
    )
    transformation_type: str | None = Field(
        default=None, description="The type of merger/acquisition transformation."
    )
    accounting_method: str | None = Field(
        default=None, description="The accounting method used in the transformation."
    )
    relationship_established_date: date | None = Field(
        default=None, description="The date the relationship was established."
    )
    start_date: date | None = Field(
        default=None, description="The date the record became effective."
    )
    end_date: date | None = Field(
        default=None, description="The date the record ceased to be valid."
    )
    transformation_date: date | None = Field(
        default=None, description="The date the transformation became effective."
    )
    offspring_rssd_id: str | None = Field(
        default=None,
        description="The RSSD identifier of the offspring (owned/controlled).",
    )
    parent_rssd_id: str | None = Field(
        default=None,
        description="The RSSD identifier of the parent (owner/controller).",
    )
    successor_rssd_id: str | None = Field(
        default=None,
        description="The RSSD identifier of the successor (survivor).",
    )
    predecessor_rssd_id: str | None = Field(
        default=None,
        description="The RSSD identifier of the predecessor (non-survivor).",
    )


class FederalReserveInstitutionStructureFetcher(
    Fetcher[
        FederalReserveInstitutionStructureQueryParams,
        list[FederalReserveInstitutionStructureData],
    ]
):
    """Federal Reserve NIC Institution Structure Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveInstitutionStructureQueryParams:
        """Transform the query params."""
        return FederalReserveInstitutionStructureQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveInstitutionStructureQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the requested NIC structure file and filter by RSSD."""
        from openbb_federal_reserve.utils.ffiec import (
            fetch_relationships,
            fetch_transformations,
        )

        records = (
            fetch_relationships()
            if query.kind == "relationships"
            else fetch_transformations()
        )

        # Filter the raw records first (a cheap check of the two RSSD columns), so
        # only the handful of matching rows are lowercased into dicts — the bulk
        # file holds hundreds of thousands of relationships.
        if query.rssd_id:
            target = query.rssd_id.strip()
            records = [
                r
                for r in records
                if any(
                    target == str(v).strip()
                    for k, v in r.items()
                    if "RSSD" in k.upper()
                )
            ]

        rows = [
            {
                k.lstrip("#").lower(): (v.strip() if isinstance(v, str) else v)
                for k, v in r.items()
            }
            for r in records
        ]

        if not rows:
            raise EmptyDataError("No structure records matched the query.")

        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveInstitutionStructureQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveInstitutionStructureData]:
        """Curate the records, translate coded fields, and resolve RSSD names."""
        from openbb_federal_reserve.utils.ffiec import rssd_names

        names = rssd_names()
        results: list[FederalReserveInstitutionStructureData] = []
        for row in data:
            if query.kind == "relationships":
                mapped = FederalReserveInstitutionStructureFetcher._map_relationship(
                    row
                )
                mapped["parent_name"] = names.get(str(mapped.get("parent_rssd_id")))
                mapped["offspring_name"] = names.get(
                    str(mapped.get("offspring_rssd_id"))
                )
            else:
                mapped = FederalReserveInstitutionStructureFetcher._map_transformation(
                    row
                )
                mapped["predecessor_name"] = names.get(
                    str(mapped.get("predecessor_rssd_id"))
                )
                mapped["successor_name"] = names.get(
                    str(mapped.get("successor_rssd_id"))
                )
            results.append(
                FederalReserveInstitutionStructureData.model_validate(mapped)
            )
        return results

    @staticmethod
    def _map_relationship(row: dict) -> dict[str, Any]:
        """Curate and decode a single relationship record."""
        mapped: dict[str, Any] = {
            "parent_rssd_id": row.get("id_rssd_parent"),
            "offspring_rssd_id": row.get("id_rssd_offspring"),
        }
        reln_lvl = row.get("reln_lvl")
        if reln_lvl:
            mapped["relationship_level"] = _RELN_LVL_MAP.get(reln_lvl, reln_lvl)
        ctrl = row.get("ctrl_ind")
        if ctrl:
            mapped["control_indicator"] = _CTRL_IND_MAP.get(ctrl, ctrl)
        equity = row.get("equity_ind")
        if equity:
            mapped["equity_indicator"] = _EQUITY_IND_MAP.get(equity, equity)
        reg = row.get("reg_ind")
        if reg:
            mapped["regulated_indicator"] = _REG_IND_MAP.get(reg, reg)
        term = row.get("reason_term_reln")
        if term:
            mapped["reason_relationship_terminated"] = _REASON_TERM_RELN_MAP.get(
                term, term
            )
        bracket = row.get("pct_equity_bracket")
        if bracket:
            mapped["percent_equity_bracket"] = bracket
        for source, target in (
            ("pct_equity", "percent_equity"),
            ("pct_other", "percent_other"),
        ):
            value = row.get(source)
            if value not in (None, ""):
                mapped[target] = float(value)
        mapped["relationship_established_date"] = _parse_nic_date(
            row.get("dt_reln_est")
        )
        mapped["start_date"] = _parse_nic_date(row.get("dt_start"))
        mapped["end_date"] = _parse_nic_date(row.get("dt_end"))
        return mapped

    @staticmethod
    def _map_transformation(row: dict) -> dict[str, Any]:
        """Curate and decode a single transformation record."""
        mapped: dict[str, Any] = {
            "predecessor_rssd_id": row.get("id_rssd_predecessor"),
            "successor_rssd_id": row.get("id_rssd_successor"),
        }
        trnsfm = row.get("trnsfm_cd")
        if trnsfm:
            mapped["transformation_type"] = _TRNSFM_CD_MAP.get(trnsfm, trnsfm)
        acct = row.get("acct_method")
        if acct:
            mapped["accounting_method"] = _ACCT_METHOD_MAP.get(acct, acct)
        mapped["transformation_date"] = _parse_nic_date(row.get("dt_trans"))
        return mapped
