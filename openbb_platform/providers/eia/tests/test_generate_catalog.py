"""Tests for the EIA catalog generator."""

import json

import pytest

from openbb_us_eia.utils import generate_catalog


def _leaf_node(name, facets=("coalRankId",), freq="annual"):
    return {
        "name": name,
        "description": "A  test\r\n dataset.",
        "frequency": [
            {"id": freq, "format": "YYYY", "description": "Yearly."},
        ],
        "defaultFrequency": freq,
        "startPeriod": "2000",
        "endPeriod": "2024",
        "data": {"heat-content": {"units": "Btu"}, "value": []},
        "facets": [{"id": facet, "description": facet} for facet in facets],
    }


def _mini_tree():
    nodes = {
        "coal": {
            "name": "Coal",
            "routes": [
                {"id": "receipts", "name": "Receipts"},
                {"id": "price-by-rank", "name": "Price by Rank"},
            ],
        },
        "coal/receipts": _leaf_node("Receipts", facets=("coalRankId", "plantId")),
        "coal/price-by-rank": _leaf_node("Price by Rank"),
    }
    facet_values = {
        "coal/receipts": {
            "coalRankId": {
                "total": 2,
                "values": [
                    {"id": "BIT", "name": "Bituminous"},
                    {"id": "SUB", "name": "Subbituminous"},
                    {"id": "(NA)", "name": "Not Applicable"},
                ],
            },
            "plantId": {
                "total": 1,
                "values": [{"id": "1", "name": "Plant One"}],
            },
        },
        "coal/price-by-rank": {
            "coalRankId": {
                "total": 1,
                "values": [{"id": "LIG", "name": "Lignite"}],
            },
        },
    }
    root = {"routes": [{"id": "coal", "name": "Coal", "description": "Coal data."}]}
    return {"root": root, "nodes": nodes, "facet_values": facet_values}


class TestSlugHelpers:
    """Slug and snake-case helpers."""

    def test_slugify_cleans_names(self):
        assert generate_catalog.slugify("F.O.B. Costs (per unit)") == "fob_costs"
        assert generate_catalog.slugify("No. 2 Distillate - discontinued") == (
            "no2_distillate"
        )
        assert (
            generate_catalog.slugify("Total CO2 - deprecated: see SEDS") == "total_co2"
        )

    def test_snake_case(self):
        assert generate_catalog.snake_case("plantCode") == "plant_code"
        assert generate_catalog.snake_case("heat-content") == "heat_content"


class TestNamedGroup:
    """Group assembly from a crawled tree."""

    def test_builds_datasets_and_choices(self):
        tree = _mini_tree()
        child_meta = generate_catalog._child_meta(tree)
        group = generate_catalog._named_group(
            "coal", tree, child_meta, ["coal/receipts", "coal/price-by-rank"]
        )
        assert sorted(group["datasets"]) == ["price_by_rank", "receipts"]
        spec = group["datasets"]["receipts"]
        assert spec["path"] == "coal/receipts"
        assert spec["description"] == "A test dataset."
        assert spec["category"] == "Coal"
        assert spec["data_columns"]["heat_content"]["id"] == "heat-content"
        assert spec["data_columns"]["value"]["units"] is None
        assert spec["facets"]["coal_rank"]["id"] == "coalRankId"
        assert {"BIT", "SUB"} == {
            choice["value"] for choice in spec["facets"]["coal_rank"]["choices"]
        }
        assert {"BIT", "LIG", "SUB"} == {
            value for value in group["choices"]["coal_rank"]
        }

    def test_duplicate_slug_raises(self):
        tree = _mini_tree()
        tree["nodes"]["coal"]["routes"][1]["name"] = "Receipts"
        tree["nodes"]["coal/price-by-rank"]["name"] = "Receipts"
        child_meta = generate_catalog._child_meta(tree)
        with pytest.raises(ValueError, match="Duplicate dataset slug"):
            generate_catalog._named_group(
                "coal", tree, child_meta, ["coal/receipts", "coal/price-by-rank"]
            )

    def test_long_slug_without_override_raises(self):
        tree = _mini_tree()
        tree["nodes"]["coal/price-by-rank"]["name"] = "word " * 20
        child_meta = generate_catalog._child_meta(tree)
        with pytest.raises(ValueError, match="add a SLUG_OVERRIDES entry"):
            generate_catalog._named_group(
                "coal", tree, child_meta, ["coal/price-by-rank"]
            )

    def test_unmapped_facet_raises(self):
        tree = _mini_tree()
        tree["nodes"]["coal/receipts"]["facets"].append({"id": "newFacetId"})
        child_meta = generate_catalog._child_meta(tree)
        with pytest.raises(KeyError, match="Unmapped facet id"):
            generate_catalog._named_group("coal", tree, child_meta, ["coal/receipts"])


def _receipt_spec():
    return {
        "path": "coal/shipments/receipts",
        "name": "Receipts",
        "description": "Coal shipment receipts.",
        "category": "Coal Shipments",
        "category_slug": "coal_shipments",
        "frequencies": {
            "quarterly": {"format": 'YYYY-"Q"Q', "path": "coal/shipments/receipts"},
            "annual": {"format": "YYYY", "path": "coal/shipments/receipts"},
        },
        "default_frequency": "annual",
        "start_period": "2008-Q1",
        "end_period": "2025-Q1",
        "data_columns": {
            "quantity": {"id": "quantity", "alias": None, "units": "tons"},
            "price": {"id": "price", "alias": None, "units": "dollars per ton"},
        },
        "facets": {
            "coal_rank": {
                "id": "coalRankId",
                "description": "Coal Rank",
                "n_values": 2,
                "choices": [
                    {"value": "BIT", "label": "Bituminous", "param": "bituminous"},
                    {
                        "value": "SUB",
                        "label": "Subbituminous",
                        "param": "subbituminous",
                    },
                ],
            },
            "mine_type": {
                "id": "mineTypeId",
                "description": "Mine Type",
                "n_values": 2,
                "choices": [
                    {"value": "S", "label": "Surface", "param": "surface"},
                    {"value": "U", "label": "Underground", "param": "underground"},
                ],
            },
            "mine": {
                "id": "mineMSHAId",
                "description": "Mine",
                "n_values": 1267,
            },
        },
    }


class TestFacetQueryField:
    """A facet field documents the choices and any frequency restriction."""

    def test_frequency_restricted_facet_says_so(self):
        source = generate_catalog._facet_query_field(
            "electricity",
            "timezone",
            {
                "id": "timezone",
                "description": "Timezone",
                "choices": [
                    {"value": "Eastern", "param": "eastern"},
                    {"value": "Central", "param": "central"},
                ],
                "frequencies": ["hourly", "local-hourly"],
            },
        )
        assert "Only applies to frequency: hourly, local-hourly." in source

    def test_unrestricted_facet_omits_the_note(self):
        source = generate_catalog._facet_query_field(
            "coal",
            "coal_rank",
            {
                "id": "coalRankId",
                "description": "Coal rank",
                "choices": [{"value": "MET"}, {"value": "BIT"}],
            },
        )
        assert "Only applies to frequency" not in source


class TestRenderDatasetModule:
    """Complete model module rendering."""

    def test_module_compiles_and_declares_everything(self):
        source = generate_catalog.render_dataset_module(
            "coal", "receipts", _receipt_spec()
        )
        compile(source, "receipts.py", "exec")
        assert "class EiaCoalReceiptsQueryParams(EiaApiQueryParams):" in source
        assert "class EiaCoalReceiptsData(EiaApiData):" in source
        assert "class EiaCoalReceiptsFetcher" in source
        assert "@staticmethod" in source
        assert "def transform_query" in source
        assert "async def aextract_data" in source
        assert "def transform_data" in source
        assert '__group__ = "coal"' in source
        assert '__dataset__ = "receipts"' in source
        assert 'mine_type: Literal["surface", "underground"] | None = Field(' in source
        assert "coal_rank: str | None = Field(" in source
        assert "facet_options" in source
        assert "coal_rank_name: str | None = Field(" in source
        assert "quantity: float | None = Field(" in source
        assert (
            "Quantity (tons). Withheld or unavailable values return as null." in source
        )

    def test_release_module_declares_release_field(self):
        spec = _receipt_spec()
        spec["category"] = "Annual Energy Outlook"
        source = generate_catalog.render_dataset_module(
            "aeo", "2025", spec, release_datasets=["2024", "2025"]
        )
        compile(source, "aeo.py", "exec")
        assert 'release: Literal["2024", "2025"] = Field(' in source
        assert 'default="2025"' in source
        assert "__dataset__" not in source

    def test_large_vocabulary_points_to_facet_options(self):
        spec = _receipt_spec()
        spec["facets"]["coal_rank"]["choices"] = [
            {"value": f"V{i}", "label": f"Label {i}", "param": f"label_{i}"}
            for i in range(150)
        ]
        spec["facets"]["coal_rank"]["n_values"] = 150
        source = generate_catalog.render_dataset_module("coal", "receipts", spec)
        assert "There are 150 valid values" in source

    def test_catalog_helpers_loader_guard(self, monkeypatch):
        import importlib.util

        monkeypatch.setitem(generate_catalog.__dict__, "_CATALOG_HELPERS", None)
        monkeypatch.setattr(
            importlib.util, "spec_from_file_location", lambda *args, **kwargs: None
        )
        with pytest.raises(ImportError, match="Unable to load"):
            generate_catalog._catalog_helpers()

    def test_data_column_facet_collision_raises(self):
        spec = _receipt_spec()
        spec["data_columns"]["coal_rank"] = {
            "id": "coal-rank",
            "alias": None,
            "units": None,
        }
        with pytest.raises(ValueError, match="collides"):
            generate_catalog.render_dataset_module("coal", "receipts", spec)


class TestReleaseTemplate:
    """Release-group template assembly."""

    def test_uses_union_choices_and_drops_uncatalogued(self):
        spec = _receipt_spec()
        group_doc = {
            "datasets": {"2024": dict(spec), "2025": dict(spec)},
            "choices": {
                "coal_rank": [
                    {"value": "BIT", "label": "Bituminous", "param": "bituminous"},
                    {"value": "LIG", "label": "Lignite", "param": "lignite"},
                ]
            },
        }
        template = generate_catalog._release_template("aeo", group_doc)
        assert template["name"] == "Coal Shipments"
        assert template["path"] == "aeo"
        assert "release" in template["description"]
        assert [c["param"] for c in template["facets"]["coal_rank"]["choices"]] == [
            "bituminous",
            "lignite",
        ]
        assert "choices" not in template["facets"]["mine_type"]


class TestRenderRegistry:
    """Registry module rendering."""

    def test_registry_lists_every_model(self):
        catalog_doc = generate_catalog.build_catalog(_full_tree())
        source = generate_catalog.render_registry(catalog_doc)
        compile(source, "registry.py", "exec")
        assert (
            "from openbb_us_eia.models.coal.receipts import EiaCoalReceiptsFetcher"
            in source
        )
        assert '"EiaCoalReceipts": EiaCoalReceiptsFetcher,' in source
        assert '"EiaAeo": EiaAeoFetcher,' in source
        assert '"EiaCrudeOilImports": EiaCrudeOilImportsFetcher,' in source


class TestWriteModels:
    """Model module writing."""

    def test_writes_modules_and_registry(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_catalog, "MODELS_ROOT", tmp_path)
        catalog_doc = generate_catalog.build_catalog(_full_tree())
        written = generate_catalog.write_models(catalog_doc)
        assert written == sum(
            1
            if group in generate_catalog.FLAT_GROUPS + generate_catalog.RELEASE_GROUPS
            else len(catalog_doc["groups"][group]["datasets"])
            for group in generate_catalog.DATASET_GROUPS_EMIT
        )
        assert (tmp_path / "coal" / "receipts.py").exists()
        assert (tmp_path / "coal" / "__init__.py").exists()
        assert (tmp_path / "aeo.py").exists()
        assert (tmp_path / "seds.py").exists()
        assert (tmp_path / "registry.py").exists()


def _full_tree():
    """Build a synthetic crawl covering every catalog group."""

    def leaf(name, facets, freqs=(("annual", "YYYY"),)):
        return {
            "name": name,
            "description": f"{name} description.",
            "frequency": [
                {"id": fid, "format": fmt, "description": fid} for fid, fmt in freqs
            ],
            "defaultFrequency": freqs[0][0],
            "startPeriod": "2000",
            "endPeriod": "2024",
            "data": {"value": {"units": "units"}},
            "facets": [{"id": facet, "description": facet} for facet in facets],
        }

    def category(name, children):
        return {
            "name": name,
            "routes": [{"id": child, "name": f"{name} {child}"} for child in children],
        }

    hourly = (("hourly", 'YYYY-MM-DD"T"HH24'), ("local-hourly", 'YYYY-MM-DD"T"HH24TZH'))
    daily = (("daily", "YYYY-MM-DD"),)

    nodes = {
        "coal": category("Coal", ["receipts"]),
        "coal/receipts": leaf("Receipts", ["coalRankId", "plantId"]),
        "petroleum": category("Petroleum", ["pri", "move"]),
        "petroleum/pri": category("Prices", ["spt", "imc1"]),
        "petroleum/pri/spt": leaf(
            "Spot Prices", ["duoarea", "product", "process", "series"]
        ),
        "petroleum/pri/imc1": leaf(
            "F.O.B. Costs of Imported Crude Oil by Area", ["duoarea"]
        ),
        "petroleum/move": category("Movements", ["imc1"]),
        "petroleum/move/imc1": leaf(
            "F.O.B. Costs of Imported Crude Oil by Area", ["duoarea"]
        ),
        "natural-gas": category("Natural Gas", ["pri"]),
        "natural-gas/pri": category("Prices", ["sum"]),
        "natural-gas/pri/sum": leaf(
            "Natural Gas Prices", ["duoarea", "product", "process", "series"]
        ),
        "electricity": category(
            "Electricity",
            [
                "electric-power-operational-data",
                "facility-fuel",
                "operating-generator-capacity",
                "retail-sales",
                "rto",
                "state-electricity-profiles",
            ],
        ),
        "electricity/electric-power-operational-data": leaf(
            "Electric Power Operations", ["location", "sectorid", "fueltypeid"]
        ),
        "electricity/facility-fuel": leaf(
            "Facility Fuel",
            ["plantCode", "fuel2002", "fuelType", "state", "primeMover"],
        ),
        "electricity/operating-generator-capacity": leaf(
            "Inventory of Operable Generators",
            [
                "stateid",
                "sector",
                "entityid",
                "plantid",
                "generatorid",
                "unit",
                "technology",
                "energy_source_code",
                "prime_mover_code",
                "balancing_authority_code",
                "status",
            ],
        ),
        "electricity/retail-sales": leaf("Retail Sales", ["stateid", "sectorid"]),
        "electricity/rto": category(
            "Grid Monitor",
            [
                "region-data",
                "daily-region-data",
                "fuel-type-data",
                "daily-fuel-type-data",
                "interchange-data",
                "daily-interchange-data",
                "region-sub-ba-data",
                "daily-region-sub-ba-data",
            ],
        ),
        "electricity/rto/region-data": leaf(
            "Hourly Demand", ["respondent", "type"], freqs=hourly
        ),
        "electricity/rto/daily-region-data": leaf(
            "Daily Demand", ["respondent", "type", "timezone"], freqs=daily
        ),
        "electricity/rto/fuel-type-data": leaf(
            "Hourly Generation", ["respondent", "fueltype"], freqs=hourly
        ),
        "electricity/rto/daily-fuel-type-data": leaf(
            "Daily Generation", ["respondent", "fueltype", "timezone"], freqs=daily
        ),
        "electricity/rto/interchange-data": leaf(
            "Hourly Interchange", ["fromba", "toba"], freqs=hourly
        ),
        "electricity/rto/daily-interchange-data": leaf(
            "Daily Interchange", ["fromba", "toba", "timezone"], freqs=daily
        ),
        "electricity/rto/region-sub-ba-data": leaf(
            "Hourly Subregion Demand", ["subba", "parent"], freqs=hourly
        ),
        "electricity/rto/daily-region-sub-ba-data": leaf(
            "Daily Subregion Demand", ["subba", "parent", "timezone"], freqs=daily
        ),
        "electricity/state-electricity-profiles": category(
            "State Profiles", ["summary"]
        ),
        "electricity/state-electricity-profiles/summary": leaf(
            "State Rankings", ["stateID"]
        ),
        "crude-oil-imports": leaf(
            "Crude Oil Imports",
            ["originId", "originType", "destinationId", "destinationType", "gradeId"],
        ),
        "international": leaf(
            "International",
            [
                "productId",
                "activityId",
                "countryRegionId",
                "countryRegionTypeId",
                "dataFlagId",
                "unit",
            ],
        ),
        "seds": leaf("SEDS", ["seriesId", "stateId"]),
        "total-energy": leaf("Total Energy", ["msn"]),
        "densified-biomass": category("Biomass", ["production-by-region"]),
        "densified-biomass/production-by-region": leaf(
            "Production by Region", ["fuelTypeId", "region"]
        ),
        "nuclear-outages": category("Nuclear", ["us-nuclear-outages"]),
        "nuclear-outages/us-nuclear-outages": leaf(
            "U.S. Nuclear Outages", ["facility"]
        ),
        "aeo": category("AEO", ["2025"]),
        "aeo/2025": leaf(
            "AEO 2025", ["history", "scenario", "tableId", "seriesId", "regionId"]
        ),
        "ieo": category("IEO", ["2023"]),
        "ieo/2023": leaf(
            "IEO 2023", ["history", "scenario", "tableId", "seriesId", "regionId"]
        ),
    }
    literal_targets = {
        "coal": "coal/receipts",
        "electricity": "electricity/operating-generator-capacity",
        "electricity_grid": "electricity/rto/daily-region-data",
        "state_electricity_profiles": "electricity/state-electricity-profiles/summary",
        "crude_oil_imports": "crude-oil-imports",
        "international": "international",
        "densified_biomass": "densified-biomass/production-by-region",
        "nuclear_outages": "nuclear-outages/us-nuclear-outages",
        "aeo": "aeo/2025",
        "ieo": "ieo/2023",
    }
    for group, path in literal_targets.items():
        canonical_map = generate_catalog.FACET_CANONICAL[group]
        declared = {canonical_map[f["id"]] for f in nodes[path]["facets"]}
        for canonical in generate_catalog.LITERAL_FACETS.get(group, set()) - declared:
            facet_id = next(
                key for key, value in canonical_map.items() if value == canonical
            )
            nodes[path]["facets"].append({"id": facet_id, "description": facet_id})

    facet_values: dict = {}
    for path, node in nodes.items():
        if node.get("routes"):
            continue
        for facet in node["facets"]:
            facet_values.setdefault(path, {})[facet["id"]] = {
                "total": 1,
                "values": [{"id": "X", "name": "Value X"}],
            }
    facet_values["seds"]["seriesId"] = {
        "total": 3,
        "values": [{"id": f"S{i}", "name": f"Series {i}"} for i in range(3)],
    }
    root = {
        "routes": [
            {"id": top, "name": top, "description": f"{top} route."}
            for top in (
                "coal",
                "petroleum",
                "natural-gas",
                "electricity",
                "crude-oil-imports",
                "international",
                "seds",
                "total-energy",
                "densified-biomass",
                "nuclear-outages",
                "aeo",
                "ieo",
            )
        ]
    }
    return {"root": root, "nodes": nodes, "facet_values": facet_values}


class TestBuildCatalog:
    """Full catalog assembly over a synthetic all-groups tree."""

    def test_builds_every_group(self, monkeypatch):
        monkeypatch.setattr(generate_catalog, "CHOICES_LIMIT", 2)
        catalog = generate_catalog.build_catalog(_full_tree())
        groups = catalog["groups"]
        assert sorted(groups) == [
            "aeo",
            "coal",
            "crude_oil_imports",
            "densified_biomass",
            "electricity",
            "electricity_grid",
            "ieo",
            "international",
            "natural_gas",
            "nuclear_outages",
            "petroleum",
            "seds",
            "state_electricity_profiles",
            "total_energy",
        ]
        petroleum_paths = {
            spec["path"] for spec in groups["petroleum"]["datasets"].values()
        }
        assert "petroleum/move/imc1" not in petroleum_paths
        assert "petroleum/pri/imc1" in petroleum_paths
        demand = groups["electricity_grid"]["datasets"]["demand"]
        assert set(demand["frequencies"]) == {"hourly", "local-hourly", "daily"}
        assert demand["facets"]["timezone"]["frequencies"] == ["daily"]
        assert list(groups["aeo"]["datasets"]) == ["2025"]
        assert list(groups["ieo"]["datasets"]) == ["2023"]
        assert "series" not in groups["seds"]["choices"]
        assert groups["seds"]["choices"]["state"][0]["value"] == "X"


class TestFetchTree:
    """The live crawl against a stubbed HTTP session."""

    def test_crawls_routes_and_facets(self, monkeypatch):
        tree = _mini_tree()

        class FakeResponse:
            def __init__(self, payload, status=200):
                self.status_code = status
                self._payload = payload

            def json(self):
                return {"response": self._payload}

        class FakeSession:
            def __init__(self):
                self.flaky_hits = 0

            def get(self, url, params=None, timeout=None):
                assert params["api_key"] == "KEY"
                path = url.removeprefix(generate_catalog.API_BASE).strip("/")
                if not path:
                    return FakeResponse(tree["root"])
                if "/facet/" in path:
                    node_path, facet_id = path.split("/facet/")
                    if facet_id == "plantId":
                        return FakeResponse({}, status=500)
                    entry = tree["facet_values"][node_path][facet_id]
                    return FakeResponse(
                        {"totalFacets": entry["total"], "facets": entry["values"]}
                    )
                if path == "coal/receipts":
                    self.flaky_hits += 1
                    if self.flaky_hits == 1:
                        import requests

                        raise requests.RequestException("reset by peer")
                    if self.flaky_hits == 2:
                        return FakeResponse({}, status=429)
                return FakeResponse(tree["nodes"][path])

        import time

        import requests

        monkeypatch.setattr(time, "sleep", lambda seconds: None)
        monkeypatch.setattr(requests, "Session", FakeSession)
        crawled = generate_catalog.fetch_tree("KEY")
        assert set(crawled["nodes"]) == set(tree["nodes"])
        assert crawled["facet_values"]["coal/receipts"]["coalRankId"]["total"] == 2
        assert "plantId" not in crawled["facet_values"]["coal/receipts"]

    def test_non_retryable_status_raises(self, monkeypatch):
        class FakeResponse:
            status_code = 404

            def json(self):
                return {}

        class FakeSession:
            def get(self, url, params=None, timeout=None):
                return FakeResponse()

        import requests

        monkeypatch.setattr(requests, "Session", FakeSession)
        with pytest.raises(RuntimeError, match="HTTP 404"):
            generate_catalog.fetch_tree("KEY")

    def test_retries_exhausted_raises(self, monkeypatch):
        class FakeResponse:
            status_code = 503

            def json(self):
                return {}

        class FakeSession:
            def get(self, url, params=None, timeout=None):
                return FakeResponse()

        import time

        import requests

        monkeypatch.setattr(time, "sleep", lambda seconds: None)
        monkeypatch.setattr(requests, "Session", FakeSession)
        with pytest.raises(RuntimeError, match="Retries exhausted"):
            generate_catalog.fetch_tree("KEY")


class TestLintGenerated:
    """The ruff gate on generated modules."""

    def test_raises_when_ruff_fails(self, tmp_path, monkeypatch):
        class FakeCompleted:
            returncode = 1

        monkeypatch.setattr(
            generate_catalog.subprocess, "run", lambda argv, **kwargs: FakeCompleted()
        )
        with pytest.raises(RuntimeError, match="failed for the generated modules"):
            generate_catalog.lint_generated(tmp_path)


class TestMain:
    """The command-line entry point."""

    def test_main_writes_outputs_from_tree_file(self, tmp_path, monkeypatch):
        tree_file = tmp_path / "tree.json"
        tree_file.write_text(json.dumps(_full_tree()))
        asset = tmp_path / "eia_catalog.json.xz"
        models_root = tmp_path / "models"
        monkeypatch.setattr(generate_catalog, "ASSET_PATH", asset)
        monkeypatch.setattr(generate_catalog, "MODELS_ROOT", models_root)
        monkeypatch.setattr(
            "sys.argv", ["generate-eia-catalog", "--tree", str(tree_file)]
        )
        assert generate_catalog.main() == 0
        assert asset.exists()
        assert (models_root / "coal" / "receipts.py").exists()
        assert (models_root / "registry.py").exists()

    def test_main_returns_ty_exit_code(self, tmp_path, monkeypatch, capsys):
        tree_file = tmp_path / "tree.json"
        tree_file.write_text(json.dumps(_full_tree()))
        asset = tmp_path / "eia_catalog.json.xz"
        models_root = tmp_path / "models"
        monkeypatch.setattr(generate_catalog, "ASSET_PATH", asset)
        monkeypatch.setattr(generate_catalog, "MODELS_ROOT", models_root)
        monkeypatch.setattr(
            "sys.argv", ["generate-eia-catalog", "--tree", str(tree_file)]
        )

        class FakeCompleted:
            def __init__(self, returncode):
                self.returncode = returncode

        def fake_run(argv, **kwargs):
            return FakeCompleted(2 if "ty" in argv else 0)

        monkeypatch.setattr(generate_catalog.subprocess, "run", fake_run)
        assert generate_catalog.main() == 2
        assert "ty check failed" in capsys.readouterr().err

    def test_main_asset_only_leaves_models_untouched(self, tmp_path, monkeypatch):
        tree_file = tmp_path / "tree.json"
        tree_file.write_text(json.dumps(_full_tree()))
        asset = tmp_path / "eia_catalog.json.xz"
        models_root = tmp_path / "models"
        monkeypatch.setattr(generate_catalog, "ASSET_PATH", asset)
        monkeypatch.setattr(generate_catalog, "MODELS_ROOT", models_root)
        monkeypatch.setattr(
            "sys.argv",
            ["generate-eia-catalog", "--tree", str(tree_file), "--asset-only"],
        )
        assert generate_catalog.main() == 0
        assert asset.exists()
        assert not models_root.exists()

    def test_main_requires_api_key_for_live_crawl(self, tmp_path, monkeypatch, capsys):
        from openbb_core.app.service.user_service import UserService

        monkeypatch.setattr("sys.argv", ["generate-eia-catalog"])

        class FakeCredentials:
            def model_dump(self):
                return {"eia_api_key": None}

        class FakeSettings:
            credentials = FakeCredentials()

        monkeypatch.setattr(
            UserService, "default_user_settings", FakeSettings(), raising=False
        )
        assert generate_catalog.main() == 1
        assert "API key is required" in capsys.readouterr().err

    def test_main_live_crawl_uses_credential(self, tmp_path, monkeypatch):
        from openbb_core.app.service.user_service import UserService
        from pydantic import SecretStr

        monkeypatch.setattr("sys.argv", ["generate-eia-catalog"])
        monkeypatch.setattr(
            generate_catalog, "ASSET_PATH", tmp_path / "eia_catalog.json.xz"
        )
        monkeypatch.setattr(generate_catalog, "MODELS_ROOT", tmp_path / "models")

        class FakeCredentials:
            def model_dump(self):
                return {"eia_api_key": SecretStr("KEY")}

        class FakeSettings:
            credentials = FakeCredentials()

        monkeypatch.setattr(
            UserService, "default_user_settings", FakeSettings(), raising=False
        )
        crawled: dict = {}

        def fake_fetch_tree(api_key):
            crawled["api_key"] = api_key
            return _full_tree()

        monkeypatch.setattr(generate_catalog, "fetch_tree", fake_fetch_tree)
        assert generate_catalog.main() == 0
        assert crawled["api_key"] == "KEY"
        assert (tmp_path / "eia_catalog.json.xz").exists()
        assert (tmp_path / "models" / "registry.py").exists()
