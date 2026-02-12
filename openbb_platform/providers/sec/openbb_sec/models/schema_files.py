"""SEC XBRL Taxonomy Explorer Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, model_validator

TAXONOMY_CHOICES = Literal[
    "us-gaap",
    "srt",
    "dei",
    "ecd",
    "cyd",
    "ffd",
    "ifrs",
    "hmrc-dpl",
    "rxp",
    "spac",
    "cef",
    "oef",
    "vip",
    "fnd",
    "sro",
    "sbs",
    "rocr",
    "country",
    "currency",
    "exch",
    "naics",
    "sic",
    "stpr",
    "snj",
]

CATEGORY_CHOICES = Literal[
    "operating_company",
    "investment_company",
    "self_regulatory_org",
    "sbs_repository",
    "nrsro",
    "common_reference",
]


class SecSchemaFilesQueryParams(QueryParams):
    """SEC XBRL Taxonomy Explorer Query.

    Source: https://sec.gov/

    Progressively explore SEC/FASB XBRL taxonomies:

    - No parameters: list all available taxonomy families.
    - taxonomy only: get all parsed structures for the most recent year.
    - taxonomy + year: get all parsed structures for a specific year.
    - taxonomy + component: get one component's structure using the most recent year.
    - taxonomy + year + component: get one component's parsed structure.
    """

    taxonomy: TAXONOMY_CHOICES | None = Field(
        default=None,
        description=(
            "Taxonomy family to explore. "
            + "Omit to list all available taxonomies and their descriptions."
        ),
    )
    year: int | None = Field(
        default=None,
        description=(
            "Taxonomy year (e.g. 2011+ for us-gaap, varies by taxonomy). "
            + "Defaults to the most recent year when omitted."
        ),
    )
    component: str | None = Field(
        default=None,
        description=(
            "Presentation component to retrieve. Values are taxonomy-specific. "
            + "Omit to return all components for the taxonomy."
        ),
    )
    category: CATEGORY_CHOICES | None = Field(
        default=None,
        description=("Filter taxonomies by SEC filer category."),
    )

    @model_validator(mode="after")
    def _validate_progressive_params(self):
        """Enforce progressive drill-down: year requires taxonomy, component requires year."""
        if self.year is not None and self.taxonomy is None:
            raise ValueError(
                "Parameter 'year' requires 'taxonomy' to be set. "
                "Provide a taxonomy first, or omit both to list all taxonomies."
            )
        if self.component is not None and self.taxonomy is None:
            raise ValueError("Parameter 'component' requires 'taxonomy' to be set.")
        if self.category is not None and self.taxonomy is not None:
            raise ValueError(
                "Parameter 'category' is only used when listing all taxonomies "
                "(i.e., when 'taxonomy' is not set)."
            )
        return self


class SecSchemaFilesData(Data):
    """SEC XBRL Taxonomy Explorer Data."""

    name: str = Field(
        description=(
            "Identifier: taxonomy key, year, component name, or XBRL element ID "
            "depending on the query mode."
        )
    )
    label: str | None = Field(
        default=None,
        description="Human-readable label.",
    )
    description: str | None = Field(
        default=None,
        description="Description or long name.",
    )
    category: str | None = Field(
        default=None,
        description="Taxonomy category (e.g., operating_company).",
    )
    style: str | None = Field(
        default=None,
        description="Taxonomy style (e.g., FASB_STANDARD, SEC_EMBEDDED).",
    )
    has_label_linkbase: bool | None = Field(
        default=None,
        description="Whether the taxonomy has a parseable label linkbase.",
    )
    url: str | None = Field(
        default=None,
        description="URL to the taxonomy resource or SEC reference page.",
    )
    level: int | None = Field(
        default=None,
        description="Hierarchy depth in presentation structure (0 = root).",
    )
    order: float | None = Field(
        default=None,
        description="Sort order within parent in presentation structure.",
    )
    parent_id: str | None = Field(
        default=None,
        description="Parent XBRL element ID in presentation structure.",
    )
    preferred_label: str | None = Field(
        default=None,
        description="Preferred label role URI for presentation rendering.",
    )
    xbrl_type: str | None = Field(
        default=None,
        description=(
            "XBRL data type (e.g., monetaryItemType, textBlockItemType, "
            "stringItemType, sharesItemType, perShareItemType, domainItemType)."
        ),
    )
    period_type: str | None = Field(
        default=None,
        description="Period type: 'instant' (point-in-time) or 'duration' (over a period).",
    )
    balance_type: str | None = Field(
        default=None,
        description="Balance type for monetary items: 'credit' or 'debit'.",
    )
    abstract: bool | None = Field(
        default=None,
        description="Whether the element is abstract (grouping/heading only, not taggable).",
    )
    substitution_group: str | None = Field(
        default=None,
        description=(
            "XBRL substitution group: 'item' (line item), 'dimensionItem' (axis), "
            "'hypercubeItem' (table)."
        ),
    )
    nillable: bool | None = Field(
        default=None,
        description="Whether the element value can be nil.",
    )


def _flatten_nodes(nodes) -> list[dict[str, Any]]:
    """Recursively flatten XBRLNode trees into a list of dicts."""
    results: list[dict[str, Any]] = []
    for node in nodes:
        results.append(
            {
                "name": node.element_id,
                "label": node.label,
                "description": node.documentation,
                "level": node.level,
                "order": node.order,
                "parent_id": node.parent_id,
                "preferred_label": node.preferred_label,
                "xbrl_type": node.xbrl_type,
                "period_type": node.period_type,
                "balance_type": node.balance_type,
                "abstract": node.abstract,
                "substitution_group": node.substitution_group,
                "nillable": node.nillable,
            }
        )
        if node.children:
            results.extend(_flatten_nodes(node.children))
    return results


class SecSchemaFilesFetcher(
    Fetcher[SecSchemaFilesQueryParams, list[SecSchemaFilesData]]
):
    """SEC XBRL Taxonomy Explorer Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecSchemaFilesQueryParams:
        """Transform the query."""
        return SecSchemaFilesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecSchemaFilesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Extract taxonomy data based on the query parameters.

        Operates in progressive modes:
        1. No params → list all taxonomy families
        2. taxonomy (+ optional year, no component) → auto-resolve year if needed, return all components
        3. taxonomy + component (+ optional year) → return one component's structure
        """
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.xbrl_taxonomy_helper import XBRLManager

        manager = XBRLManager()

        # Mode 1: List all taxonomy families
        if query.taxonomy is None:
            taxonomies = manager.list_available_taxonomies(query.category)
            return [
                {
                    "name": key,
                    "label": meta["label"],
                    "description": meta["description"],
                    "category": meta["category"],
                    "style": meta["style"],
                    "has_label_linkbase": meta["has_label_linkbase"] == "True",
                    "url": meta["sec_reference_url"],
                }
                for key, meta in taxonomies.items()
            ]

        # Mode 2: Auto-resolve year to the most recent if not supplied
        year = query.year
        available_years = manager.get_available_years(query.taxonomy)
        if year is None:
            if not available_years:
                raise OpenBBError(
                    f"No years found for taxonomy '{query.taxonomy}'. "
                    "Omit all parameters to list available taxonomies."
                )
            year = max(available_years)
        elif available_years and year not in available_years:
            raise OpenBBError(
                f"Year {year} is not available for taxonomy '{query.taxonomy}'. "
                f"Available years: {sorted(available_years, reverse=True)}"
            )

        # Resolve components to fetch
        if query.component is not None:
            target_components = [query.component]
        else:
            target_components = manager.list_available_components(query.taxonomy, year)
            if not target_components:
                raise OpenBBError(f"No components found for {query.taxonomy} {year}.")

            # Smart default: if multiple components, return component listing
            # with metadata instead of parsing everything (which is too heavy
            # for taxonomies like us-gaap with 26 components or IFRS with 47).
            # Single-component taxonomies auto-parse fully.
            if len(target_components) > 1:
                return manager.get_components_metadata(query.taxonomy, year)

        # Fetch and flatten all target components
        results: list[dict[str, Any]] = []
        for comp in target_components:
            nodes = manager.get_structure(query.taxonomy, year, comp)
            results.extend(_flatten_nodes(nodes))
        return results

    @staticmethod
    def transform_data(
        query: SecSchemaFilesQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[SecSchemaFilesData]:
        """Transform the data to the standard format."""
        return [SecSchemaFilesData.model_validate(d) for d in data]
