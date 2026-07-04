"""Generate per-district ``widgets.json`` and ``apps.json`` specifications."""

from __future__ import annotations

import copy
import json
from typing import Any

_SEAL = (
    "https://upload.wikimedia.org/wikipedia/commons/1/1a"
    "/Seal_of_the_United_States_Federal_Reserve_System.svg"
)


_COMMONS = "https://upload.wikimedia.org/wikipedia/commons/thumb"

_DISTRICT_IMAGES = {
    "atlanta": f"{_COMMONS}/8/8b/Federal_Reserve_Bank_of_Atlanta_Headquarters.jpg/960px-Federal_Reserve_Bank_of_Atlanta_Headquarters.jpg",
    "boston": f"{_COMMONS}/f/f4/Federal_Reserve_from_South_Boston.jpg/960px-Federal_Reserve_from_South_Boston.jpg",
    "chicago": f"{_COMMONS}/3/35/Federal_Reserve_Bank_of_Chicago_%2851574643886%29.jpg/960px-Federal_Reserve_Bank_of_Chicago_%2851574643886%29.jpg",
    "cleveland": f"{_COMMONS}/b/b1/Federal_Reserve_Bank%2C_Cleveland%2C_Ohio_LCCN2010630382.jpg/960px-Federal_Reserve_Bank%2C_Cleveland%2C_Ohio_LCCN2010630382.jpg",
    "dallas": f"{_COMMONS}/6/63/Federal_Reserve_Bank_of_Dallas_01.jpg/960px-Federal_Reserve_Bank_of_Dallas_01.jpg",
    "kc": f"{_COMMONS}/4/49/Federal_Reserve_KC.jpg/960px-Federal_Reserve_KC.jpg",
    "minneapolis": f"{_COMMONS}/b/b9/Federal_Reserve_Bank_of_Minneapolis_building_3.jpg/960px-Federal_Reserve_Bank_of_Minneapolis_building_3.jpg",
    "ny": f"{_COMMONS}/c/cf/2013_Federal_Reserve_Bank_of_New_York_from_west.jpg/960px-2013_Federal_Reserve_Bank_of_New_York_from_west.jpg",
    "philadelphia": f"{_COMMONS}/5/5a/Federal_Reserve_Bank_Building_Philadelphia.jpg/960px-Federal_Reserve_Bank_Building_Philadelphia.jpg",
    "richmond": f"{_COMMONS}/c/c5/Federal_Reserve_Bank_building_-01-_%289741337905%29.jpg/960px-Federal_Reserve_Bank_building_-01-_%289741337905%29.jpg",
    "sf": f"{_COMMONS}/9/9e/Fed_Reserve_Bank_of_SF%2C_101_Market_St.JPG/960px-Fed_Reserve_Bank_of_SF%2C_101_Market_St.JPG",
    "stl": f"{_COMMONS}/d/de/St_Louis_night_expblend.jpg/960px-St_Louis_night_expblend.jpg",
}

_DISTRICT_DESCRIPTIONS = {
    "atlanta": (
        "The Atlanta Fed's real-time growth and inflation toolkit: the GDPNow"
        " nowcast, Sticky-Price CPI, Business Inflation Expectations, the Wage"
        " Growth Tracker, the Survey of Business Uncertainty, the Market"
        " Probability Tracker, and Taylor Rule utilities."
    ),
    "boston": (
        "New England regional economics from the Boston Fed's New England Public"
        " Policy Center - employment, output, and prices across the six New"
        " England states, benchmarked against the nation."
    ),
    "chicago": (
        "The Chicago Fed's national and Seventh District barometers: the CFNAI"
        " national activity index, the NFCI financial conditions index, the"
        " Brave-Butters-Kelley and Midwest Economy indexes, advance retail trade"
        " (CARTS), labor-market conditions, and the AgLetter farmland-value and"
        " farm-credit survey."
    ),
    "cleveland": (
        "Inflation measurement from the Cleveland Fed - model-based Inflation"
        " Expectations, the Inflation Nowcast, and Median and trimmed-mean CPI"
        " with component detail, plus a systemic-risk indicator."
    ),
    "dallas": (
        "Texas and global activity from the Dallas Fed - the Texas Manufacturing,"
        " Service Sector, Retail, and Banking Outlook surveys, Trimmed Mean PCE,"
        " the Texas Leading and Weekly Economic indexes, the Energy Survey, and"
        " global growth and trade indicators."
    ),
    "kc": (
        "The Kansas City Fed's financial-stress and labor gauges plus"
        " agricultural finance - the KCFSI Financial Stress Index, the"
        " Risk-On/Risk-Off and Policy Rate Uncertainty indexes, model-based"
        " natural rates, the Labor Market Conditions Indicators, and the"
        " Agricultural Credit Survey and Finance Databook."
    ),
    "minneapolis": (
        "Ninth District labor-market and output data from the Minneapolis Fed -"
        " regional employment, unemployment, labor-force participation, quits, job"
        " openings, weekly claims, regional GDP and CPI, and the business"
        " conditions survey."
    ),
    "ny": (
        "The New York Fed's reference rates and market plumbing - SOFR, the"
        " effective fed funds and overnight bank funding rates, SOMA holdings, and"
        " primary-dealer statistics - plus the Global Supply Chain Pressure Index,"
        " Multivariate Core Trend inflation, the Survey of Consumer Expectations,"
        " the Empire State manufacturing survey, and the Household Debt and Credit"
        " report."
    ),
    "philadelphia": (
        "Forecasting and business-cycle data from the Philadelphia Fed - the ADS"
        " Business Conditions Index, the Survey of Professional Forecasters, the"
        " Livingston Survey, the Anxious Index, GDPplus, the State Coincident"
        " Indexes, and the Manufacturing and Nonmanufacturing Business Outlook"
        " surveys."
    ),
    "richmond": (
        "Fifth District business surveys from the Richmond Fed - the"
        " Manufacturing, Service Sector, and combined State surveys and the CFO"
        " Survey - alongside the Non-Employment Index and a recession-probability"
        " indicator."
    ),
    "sf": (
        "Inflation decomposition and rate analytics from the San Francisco Fed -"
        " Cyclical/Acyclical and Supply/Demand-driven PCE inflation, the Proxy"
        " Funds Rate, the Treasury term premium and expected short-rate path, the"
        " Daily News Sentiment Index, and Fernald's Total Factor Productivity."
    ),
    "stl": (
        "Macroeconomic data from the St. Louis Fed - the FRED-MD and FRED-QD large"
        " macro datasets, a national economic index, and the Economic Synopses"
        " research series."
    ),
}


def _full_widgets() -> dict[str, Any]:
    """Build every federal_reserve widget with the official ``build_json`` tool."""
    from fastapi import FastAPI
    from openbb_platform_api.utils.widgets import build_json

    from openbb_federal_reserve import federal_reserve_router

    app = FastAPI()
    app.include_router(federal_reserve_router.router.api_router)
    return build_json(app.openapi(), [])


def district_widgets(slug: str, full: dict | None = None) -> dict[str, Any]:
    """Filter the full widget set to one district with bare, relative endpoints."""
    full = _full_widgets() if full is None else full
    prefix = f"/{slug}/"
    widgets: dict[str, Any] = {}
    for widget_id, source in full.items():
        # The publication-series discovery commands stay in the Python/API
        # interface but are not surfaced as dashboard widgets.
        if "publication_series" in widget_id:
            continue
        endpoint = source.get("endpoint", "")
        owned = endpoint.startswith(prefix)
        if not owned and widget_id.startswith(f"{slug}_"):
            owned = True
        if not owned and source.get("type") == "multi_file_viewer":
            owned = any(
                (param.get("optionsParams") or {}).get("district") == slug
                for param in source.get("params", [])
            )
        if not owned:
            continue
        widget = copy.deepcopy(source)
        widget["endpoint"] = _district_relative(endpoint, prefix)
        for param in widget.get("params", []):
            options = param.get("optionsEndpoint")
            if isinstance(options, str):
                param["optionsEndpoint"] = _district_relative(options, prefix)
        widgets[widget_id] = widget
    return widgets


_SHARED_ENDPOINTS = (
    "regional_publications_download",
    "regional_publications_choices",
    "market_probability_meetings",
    "bhcpr_report_download",
    "bhcpr_report_choices",
)


def _district_relative(value: str, prefix: str) -> str:
    """Rebase a widget endpoint to a bare path relative to the district."""
    if value.startswith(prefix):
        return value[len(prefix) :]
    last = value.rsplit("/", 1)[-1]
    if last in _SHARED_ENDPOINTS:
        return last
    return value


def _tab_slug(name: str, used: set[str]) -> str:
    """Build a unique, url-safe tab id from a theme name."""
    base = "-".join(
        part
        for part in "".join(c if c.isalnum() else " " for c in name.lower()).split()
    )
    base = base or "tab"
    slug, counter = base, 2
    while slug in used:
        slug = f"{base}-{counter}"
        counter += 1
    used.add(slug)
    return slug


def build_apps(
    widgets: dict[str, Any], district: str, district_slug: str = ""
) -> list[dict]:
    """Build a district apps.json with one themed tab per widget ``subCategory``."""
    image = _DISTRICT_IMAGES.get(district_slug, _SEAL)
    themes: dict[str, list[str]] = {}
    for widget_id, widget in widgets.items():
        theme = widget.get("subCategory") or "Overview"
        themes.setdefault(theme, []).append(widget_id)

    tabs: dict[str, Any] = {}
    used: set[str] = set()
    for theme, widget_ids in themes.items():
        slug = _tab_slug(theme, used)
        layout = [
            {
                "i": widget_id,
                "x": 0,
                "y": index * 18,
                "w": 40,
                "h": 18,
                "state": {"params": {}},
            }
            for index, widget_id in enumerate(widget_ids)
        ]
        tabs[slug] = {"id": slug, "name": theme, "layout": layout}

    return [
        {
            "name": f"{district} Fed",
            "img": image,
            "img_dark": image,
            "img_light": image,
            "description": _DISTRICT_DESCRIPTIONS.get(
                district_slug,
                "Indicators and surveys published by the Federal Reserve Bank of"
                f" {district}.",
            ),
            "allowCustomization": True,
            "tabs": tabs,
            "groups": [],
        }
    ]


def _assets_dir() -> Any:
    """Return the path to the committed regional spec assets directory."""
    from pathlib import Path

    return Path(__file__).resolve().parent.parent / "assets" / "regional"


def _curated_apps_path(slug: str) -> Any:
    """Return the path to a subrouter's hand-curated ``apps.json``."""
    from pathlib import Path

    return Path(__file__).resolve().parent.parent / "assets" / slug / "apps.json"


_CURATED_SLUGS = ("ffiec",)


def _widgets_path(slug: str) -> Any:
    """Return the read/write path for a slug's ``widgets.json``."""
    from pathlib import Path

    if slug in _CURATED_SLUGS:
        return Path(__file__).resolve().parent.parent / "assets" / slug / "widgets.json"
    return _assets_dir() / f"{slug}_widgets.json"


def register_spec_routes(
    district_router: Any, slug: str, district: str, curated_apps: bool = False
) -> None:
    """Attach ``/widgets.json`` and ``/apps.json`` GET routes to a district router."""
    api_router = district_router.api_router

    def _read(path: Any, builder: Any) -> Any:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return builder()

    async def widgets_json() -> Any:
        """Serve the district's widgets.json specification."""
        return _read(
            _widgets_path(slug),
            lambda: _relabel_metadata(district_widgets(slug), district),
        )

    async def apps_json() -> Any:
        """Serve the district's apps.json specification."""
        return _read(
            _assets_dir() / f"{slug}_apps.json",
            lambda: build_apps(district_widgets(slug), district, slug),
        )

    async def curated_apps_json() -> Any:
        """Serve the subrouter's hand-curated apps.json verbatim."""
        path = _curated_apps_path(slug)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []

    api_router.add_api_route(
        "/widgets.json", widgets_json, methods=["GET"], include_in_schema=False
    )
    api_router.add_api_route(
        "/apps.json",
        curated_apps_json if curated_apps else apps_json,
        methods=["GET"],
        include_in_schema=False,
    )


def _relabel_metadata(widgets: dict[str, Any], branch: str) -> dict[str, Any]:
    """Give every widget a consistent browser category and sub-category."""
    for widget in widgets.values():
        widget["category"] = "Federal Reserve"
        widget["subCategory"] = branch
    return widgets


def write_specs(districts: list[tuple]) -> list[str]:
    """Generate and write the widgets/apps spec files for every district."""
    full = _full_widgets()
    out = _assets_dir()
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for _district_router, slug, district in districts:
        widgets = district_widgets(slug, full)
        apps = build_apps(widgets, district, slug)
        _relabel_metadata(widgets, district)
        for path, payload in (
            (_widgets_path(slug), widgets),
            (out / f"{slug}_apps.json", apps),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            written.append(path.name)
    return written
