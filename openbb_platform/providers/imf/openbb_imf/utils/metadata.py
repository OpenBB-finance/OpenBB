""" "IMF Metadata utilities."""

# pylint: disable=C0301,C0302,R0902,R0911,R0912,R0913,R0914,R0915,R0917,R1702,W0718
# flake8: noqa: PLR0911,PLR0912,PLR0913,PLR0917

import threading
import warnings

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_imf.utils.helpers import (
    build_codelist_to_hierarchies_map,
    build_hierarchy_to_codelist_map,
    build_time_period_params,
    extract_all_codelists_from_hierarchy,
    parse_agency_from_urn,
    parse_codelist_id_from_urn,
    parse_codelist_urn,
    parse_indicator_code_from_urn,
    parse_search_query,
)


class ImfMetadata:
    """Singleton class to manage IMF metadata and caching."""

    _instance = None
    _lock = threading.Lock()
    _codelist_lock = threading.Lock()
    _constraints_lock = threading.Lock()
    _initialized = None

    def __new__(cls):
        """Initialize the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the IMF metadata singleton."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            self._codelist_cache: dict = {}
            self._codelist_descriptions: dict = {}
            self._metadata_cache: dict = {}
            self._constraints_cache: dict = {}
            self.hierarchies = {}
            self._hierarchy_to_codelist_map = {}
            self._codelist_to_hierarchies_map = {}
            _ = self._load_from_cache()
            self._initialized = True

    def _load_from_cache(self) -> bool:
        """Load metadata from the local cache file."""
        # pylint: disable=import-outside-toplevel
        import gzip
        import pickle
        from pathlib import Path

        cache_path = Path(__file__).parent.parent / "assets" / "imf_cache.pkl.gz"
        cache: dict = {}

        if not cache_path.exists():
            return False

        try:
            with gzip.open(cache_path, "rb") as f:
                cache = pickle.load(f)  # noqa: S301

            self.dataflows = cache.get("dataflows", {})
            self.datastructures = cache.get("datastructures", {})
            self.conceptschemes = cache.get("conceptschemes", {})
            self.dataflow_groups = cache.get("dataflow_groups", {})
            self._metadata_cache = cache.get("metadata_cache", {})
            self._constraints_cache = cache.get("constraints_cache", {})
            self._codelist_cache = cache.get("codelist_cache", {})
            self._codelist_descriptions = cache.get("codelist_descriptions", {})
            self._dataflow_parameters_cache = cache.get("dataflow_parameters", {})
            self._dataflow_indicators_cache = cache.get("dataflow_indicators", {})
            self.hierarchies = cache.get("hierarchies", {})
            # Build quick lookup maps
            self._hierarchy_to_codelist_map = self._build_hierarchy_to_codelist_map()
            self._codelist_to_hierarchies_map = (
                self._build_codelist_to_hierarchies_map()
            )

            return True

        except Exception as e:
            warnings.warn(f"Error loading cache: {e}", OpenBBWarning)
            return False

    def list_dataflows(self) -> list[dict]:
        """List available dataflows."""
        dfs: list = []
        keys = sorted(list(self.dataflows.keys()))

        for key in keys:
            label = self.dataflows[key].get("name", key)
            value = self.dataflows[key].get("id", key)
            dfs.append({"label": label.strip(), "value": value.strip()})

        return dfs

    def search_dataflows(self, query: str) -> list[dict]:
        """Search dataflows based on a query string.

        Parameters
        ----------
        query : str
            The search query string, which can include AND (+) and OR (|) operators,
            as well as quoted phrases for exact matches.
        Returns
        -------
        list[dict]
            A list of matching dataflows, grouped by their structureRef ID.
        """
        grouped_results: dict = {}
        parsed_query = self._parse_query(query)

        if not parsed_query:
            raise OpenBBError(
                ValueError(f"Query string is empty or invalid -> '{query}'")
            )

        for dataflow_obj in self.dataflows.values():
            dataflow_id = dataflow_obj.get("id", "").lower()
            dataflow_name = dataflow_obj.get("name", "").lower()
            dataflow_description = dataflow_obj.get("description", "").lower()
            dataflow_matches = False

            for or_group in parsed_query:
                or_group_matches_all_and_terms = True

                for and_term in or_group:
                    if not (
                        and_term in dataflow_id
                        or and_term in dataflow_name
                        or and_term in dataflow_description
                    ):
                        or_group_matches_all_and_terms = False
                        break

                if or_group_matches_all_and_terms:
                    dataflow_matches = True
                    break

            if dataflow_matches:
                structure_ref_id = dataflow_obj.get("structureRef", {}).get("id")
                if structure_ref_id:
                    if structure_ref_id not in grouped_results:
                        grouped_results[structure_ref_id] = []

                    grouped_results[structure_ref_id].append(
                        {
                            "id": dataflow_obj.get("id"),
                            "name": dataflow_obj.get("name"),
                            "description": dataflow_obj.get("description", ""),
                        }
                    )

        final_results = [
            {"group_id": group_id, "dataflows": dataflows}
            for group_id, dataflows in grouped_results.items()
        ]

        return final_results

    def search_indicators(
        self,
        query: str,
        dataflows: list[str] | str | None = None,
        keywords: list[str] | None = None,
    ) -> list[dict]:
        """Search indicators based on a query string and optional keyword filters.

        Parameters
        ----------
        query : str
            The search query string. Multiple search phrases can be separated by semicolons (;).
            Each phrase can use AND (+) and OR (|) operators, as well as quoted phrases.
            Semicolon separation allows commas to be used within search phrases.
            Examples:
                "inflation rate;+consumer price" - searches for "inflation rate" OR "consumer price"
                "gdp+growth;|employment" - searches for "gdp AND growth" OR "employment"
        dataflows : list[str] | str | None, optional
            A dataflow ID or list of dataflow IDs to search within. If None, all
            dataflows will be searched, which can be slow.
        keywords : list[str] | None, optional
            List of keywords to filter results. Each keyword is a single word that must
            appear in the indicator's label or description. Keywords prefixed with "not "
            will exclude indicators containing that word (e.g., "not USD" excludes indicators
            with "USD" in them).
        Returns
        -------
        list[dict]
            A list of matching indicators with table/hierarchy information included.
        """
        target_dataflow_ids: list = []
        if dataflows:
            target_dataflow_ids = (
                [dataflows] if isinstance(dataflows, str) else dataflows
            )
        else:
            if not query and not keywords:
                raise OpenBBError(
                    "A query must be provided when no dataflows and keywords are specified."
                )
            target_dataflow_ids = list(self.dataflows.keys())

        if not target_dataflow_ids:
            raise OpenBBError(
                "No valid dataflows found to search indicators in."
                "This might be due to incorrect dataflow IDs."
            )

        # Build a map of indicators to their tables for enrichment
        indicator_to_tables: dict[str, list[dict]] = {}
        # Also build searchable text for each indicator from their tables
        indicator_table_text: dict[str, str] = {}

        for df_id in set(target_dataflow_ids):
            try:
                hierarchies = self.get_dataflow_hierarchies(df_id)
                for hierarchy in hierarchies:
                    try:
                        structure = self.get_dataflow_table_structure(
                            df_id, hierarchy["id"]
                        )
                        # Build searchable table text
                        table_search_text = (
                            hierarchy.get("name", "").lower()
                            + " "
                            + hierarchy.get("description", "").lower()
                        )

                        for ind in structure.get("indicators", []):
                            if ind.get("is_group"):
                                continue
                            indicator_code = ind.get("indicator_code") or ind.get(
                                "code"
                            )
                            if indicator_code:
                                key = f"{df_id}_{indicator_code}"
                                if key not in indicator_to_tables:
                                    indicator_to_tables[key] = []
                                    indicator_table_text[key] = ""

                                table_entry = {
                                    "table_id": hierarchy["id"],
                                    "table_name": hierarchy["name"],
                                }
                                if table_entry not in indicator_to_tables[key]:
                                    indicator_to_tables[key].append(table_entry)
                                    indicator_table_text[key] += " " + table_search_text
                    except Exception:  # noqa: S110
                        pass
            except Exception:  # noqa: S110
                pass

        # Get indicators for target dataflows
        all_indicators: list = []
        for df_id in set(target_dataflow_ids):
            try:
                indicators = self.get_indicators_in(df_id)
                # Enrich each indicator with table information
                for ind in indicators:
                    key = f"{df_id}_{ind['indicator']}"
                    ind["tables"] = indicator_to_tables.get(key, [])
                    # Build member_of as list of dataflow_id::table_id strings
                    ind["member_of"] = [
                        f"{df_id}::{t['table_id']}" for t in ind["tables"]
                    ]
                    # Add table text for searching (will be removed before return)
                    ind["_table_search_text"] = indicator_table_text.get(key, "")
                all_indicators.extend(indicators)
            except (KeyError, ValueError, OpenBBError) as e:
                warnings.warn(
                    f"Could not retrieve indicators for dataflow '{df_id}': {e}",
                    OpenBBWarning,
                )
                continue

        # Filter indicators by query
        # Split query on semicolon to allow commas within search phrases
        if not query:
            search_results = all_indicators
        else:
            # Split on semicolon to get separate phrases
            phrases = [phrase.strip() for phrase in query.split(";") if phrase.strip()]

            if not phrases:
                search_results = all_indicators
            else:
                filtered_by_query: list = []
                for indicator in all_indicators:
                    text_to_search = (
                        indicator.get("label", "").lower()
                        + " "
                        + indicator.get("description", "").lower()
                        + " "
                        + indicator.get("dataflow_name", "").lower()
                        + " "
                        + indicator.get("dataflow_id", "").lower()
                        + " "
                        + indicator.get("indicator", "").lower()
                        + " "
                        + indicator.get("_table_search_text", "")
                    )

                    match = False
                    for phrase in phrases:
                        # This handles AND (+) and OR (|) operators within the phrase
                        parsed_phrase = self._parse_query(phrase)

                        if not parsed_phrase:
                            # If parsing fails, treat as simple substring search
                            if phrase.lower() in text_to_search:
                                match = True
                                break
                        else:
                            phrase_match = False

                            for or_group in parsed_phrase:
                                if all(term in text_to_search for term in or_group):
                                    phrase_match = True
                                    break

                            if phrase_match:
                                match = True
                                break

                    if match:
                        filtered_by_query.append(indicator)
                search_results = filtered_by_query

        # Apply keyword filters
        if not keywords:
            # Clean up internal search field before returning
            for indicator in search_results:
                indicator.pop("_table_search_text", None)
            return search_results

        filtered_results: list = []
        for indicator in search_results:
            indicator_text = (
                indicator.get("indicator", "")
                + " "
                + indicator.get("label", "")
                + " "
                + indicator.get("description", "")
                + " "
                + indicator.get("_table_search_text", "")
            ).lower()

            # Check each keyword
            include = True
            for keyword in keywords:
                kw = keyword.strip()
                if kw.lower().startswith("not "):
                    # Exclusion keyword - if the word is present, exclude this indicator
                    exclude_word = kw[4:].lower()  # Remove "not " prefix
                    if exclude_word and exclude_word in indicator_text:
                        include = False
                        break
                elif kw.lower() not in indicator_text:
                    include = False
                    break

            if include:
                filtered_results.append(indicator)

        # Clean up internal search field before returning
        for indicator in filtered_results:
            indicator.pop("_table_search_text", None)

        return filtered_results

    def _parse_query(self, query: str) -> list[list[str]]:
        """Parse a search query string into OR-groups of AND-terms."""
        return parse_search_query(query)

    def get_dataflow_parameters(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Get available parameters for a given dataflow."""
        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        if (
            hasattr(self, "_dataflow_parameters_cache")
            and dataflow_id in self._dataflow_parameters_cache
        ):
            return self._dataflow_parameters_cache[dataflow_id]

        df_obj = self.dataflows[dataflow_id]
        agency_id = df_obj.get("agencyID")
        dsd_id = df_obj.get("structureRef", {}).get("id")
        dsd = self.datastructures.get(dsd_id, {})
        if not dsd:
            return {}

        dimensions_metadata = {
            dim["id"]: dim for dim in dsd.get("dimensions", []) if dim.get("id")
        }

        constraints_response = self.get_available_constraints(
            dataflow_id=dataflow_id,
            key="all",
            component_id="all",
            mode="available",
            references="all",
        )
        key_values = constraints_response.get("key_values", [])
        constrained_values_map = {kv["id"]: kv.get("values", []) for kv in key_values}

        parameters: dict[str, list[dict]] = {}
        dimension_codes_cache: dict[str, dict] = {}

        def _get_codes(dim_id: str) -> dict:
            if dim_id in dimension_codes_cache:
                return dimension_codes_cache[dim_id]

            dim_meta = dimensions_metadata.get(dim_id, {})
            codelist_id = self._resolve_codelist_id(
                dataflow_id, dsd_id, dim_id, dim_meta
            )
            if codelist_id:
                codes = (
                    self._get_codelist_map(
                        codelist_id, agency_id, dataflow_id, include_descriptions=False
                    )
                    or {}
                )
                dimension_codes_cache[dim_id] = codes
                return codes
            return {}

        for dim_id in dimensions_metadata:
            if dim_id == "TIME_PERIOD":
                continue

            # Get the codelist ID for this dimension upfront
            dim_meta = dimensions_metadata.get(dim_id, {})
            codelist_id = self._resolve_codelist_id(
                dataflow_id, dsd_id, dim_id, dim_meta
            )

            if not codelist_id:
                continue

            # Get the full codelist from cache
            full_codes = self._codelist_cache.get(codelist_id, {})
            if not full_codes:
                # Try to fetch it if not in cache
                codes_map = _get_codes(dim_id)
                if not codes_map:
                    continue
                full_codes = codes_map

            value_ids_to_use = (
                constrained_values_map[dim_id]
                if dim_id in constrained_values_map
                else list(full_codes.keys())
            )

            options: list = []
            for val_id in value_ids_to_use:
                # Look up the label from the full codes
                label = full_codes.get(val_id, val_id)

                # If it's a dict (from _get_codes with descriptions), extract the name
                if isinstance(label, dict):
                    label = label.get("name", val_id)

                # Ensure we have a string label
                if not label or label == val_id:
                    # If still no proper label, use the code itself
                    label = val_id

                options.append({"label": label, "value": val_id.strip()})

            if options:
                parameters[dim_id] = options

        time_period_options, _ = self._build_time_period_parameters(
            constraints_response
        )
        if time_period_options:
            parameters["TIME_PERIOD"] = time_period_options

        if hasattr(self, "_dataflow_parameters_cache"):
            self._dataflow_parameters_cache[dataflow_id] = parameters

        return parameters

    def _parse_agency_from_urn(self, code_urn: str) -> str | None:
        """Parse agency ID from hierarchicalCode's code URN."""
        return parse_agency_from_urn(code_urn)

    def _fetch_single_codelist(self, agency_id: str, codelist_id: str) -> bool:
        """
        Fetch a single codelist from the API and cache it.

        Parameters
        ----------
        agency_id : str
            The agency ID (e.g., "ISORA", "IMF.STA")
        codelist_id : str
            The codelist ID (e.g., "CL_RAFIT_LABELS")

        Returns
        -------
        bool
            True if successfully fetched and cached, False otherwise.
        """
        # pylint: disable=import-outside-toplevel
        import json

        from openbb_core.provider.utils.helpers import make_request
        from requests.exceptions import RequestException

        if codelist_id in self._codelist_cache and self._codelist_cache.get(
            codelist_id
        ):
            return True

        url = f"https://api.imf.org/external/sdmx/3.0/structure/codelist/{agency_id}/{codelist_id}?detail=full&references=none"
        headers = {"Accept": "application/json"}

        try:
            response = make_request(url, headers=headers, timeout=5)
            if response.status_code != 200:
                # Mark as failed to avoid repeated attempts
                # self._codelist_cache[codelist_id] = {}
                return False
            json_response: dict = response.json()
        except (json.JSONDecodeError, RequestException):
            # Mark as failed to avoid repeated attempts
            # self._codelist_cache[codelist_id] = {}
            return False

        codelists_in_response = json_response.get("data", {}).get("codelists", [])

        if not codelists_in_response:
            return False

        with self._codelist_lock:
            for codelist_obj in codelists_in_response:
                cl_id = codelist_obj.get("id")
                if not cl_id:
                    continue

                current_codelist_map = {}
                current_descriptions_map = {}
                for code in codelist_obj.get("codes", []):
                    code_id = code.get("id")
                    code_name_obj = (
                        code.get("names", {}).get("en") or code.get("name") or code_id
                    )
                    code_description = (
                        code.get("descriptions", {}).get("en", "")
                        or code.get("description", "")
                        or ""
                    )
                    if not code_description and code_name_obj:
                        code_description = code_name_obj

                    if code_id:
                        current_codelist_map[code_id] = code_name_obj
                        current_descriptions_map[code_id] = code_description

                self._codelist_cache[cl_id] = current_codelist_map
                self._codelist_descriptions[cl_id] = current_descriptions_map

        return codelist_id in self._codelist_cache

    def _bulk_fetch_and_cache_codelists(self, agency_id: str, dataflow_id: str):
        """Fetch all codelists for a given agency and dataflow and caches them."""
        # pylint: disable=import-outside-toplevel
        import json

        from openbb_core.provider.utils.helpers import make_request
        from requests.exceptions import RequestException

        url = f"https://api.imf.org/external/sdmx/3.0/structure/codelist/{agency_id},{dataflow_id}/all?detail=full&references=none"
        headers = {"Accept": "application/json"}

        try:
            response = make_request(url, headers=headers)
            json_response: dict = response.json()
        except (json.JSONDecodeError, RequestException) as e:
            warnings.warn(
                f"Could not bulk fetch codelists for {agency_id}/{dataflow_id}: {e} -> {url}",
                OpenBBWarning,
            )
            return

        codelists_in_response = json_response.get("data", {}).get("codelists", [])

        with self._codelist_lock:
            for codelist_obj in codelists_in_response:
                codelist_id = codelist_obj.get("id")
                if not codelist_id:
                    continue

                current_codelist_map = {}
                current_descriptions_map = {}
                for code in codelist_obj.get("codes", []):
                    code_id = code.get("id")
                    code_name_obj = (
                        code.get("names", {}).get("en") or code.get("name") or code_id
                    )
                    code_description = (
                        code.get("descriptions", {}).get("en", "")
                        or code.get("description", "")
                        or ""
                    )
                    if not code_description and code_name_obj:
                        code_description = code_name_obj

                    if code_id:
                        current_codelist_map[code_id] = code_name_obj
                        current_descriptions_map[code_id] = code_description

                self._codelist_cache[codelist_id] = current_codelist_map
                self._codelist_descriptions[codelist_id] = current_descriptions_map

    def _get_codelist_map(
        self,
        codelist_id: str,
        agency_id: str,
        dataflow_id: str,
        include_descriptions: bool = False,
    ) -> dict:
        """Download and cache the codelist map for a given codelist ID."""
        with self._codelist_lock:
            if codelist_id in self._codelist_cache:
                if include_descriptions and codelist_id in self._codelist_descriptions:
                    result = {}
                    for code_id, code_name in self._codelist_cache[codelist_id].items():
                        result[code_id] = {
                            "name": code_name,
                            "description": self._codelist_descriptions[codelist_id].get(
                                code_id, ""
                            ),
                        }
                    return result
                return self._codelist_cache[codelist_id].copy()

        # If not in cache, try to bulk fetch and cache
        self._bulk_fetch_and_cache_codelists(agency_id, dataflow_id)

        # Try again from cache
        with self._codelist_lock:
            if codelist_id in self._codelist_cache:
                if include_descriptions and codelist_id in self._codelist_descriptions:
                    result = {}
                    for code_id, code_name in self._codelist_cache[codelist_id].items():
                        result[code_id] = {
                            "name": code_name,
                            "description": self._codelist_descriptions[codelist_id].get(
                                code_id, ""
                            ),
                        }
                    return result
                return self._codelist_cache[codelist_id].copy()

        warnings.warn(f"Codelist '{codelist_id}' not found.", OpenBBWarning)
        return {}

    def get_available_constraints(
        self,
        dataflow_id: str,
        key: str,
        component_id: str | None = None,
        mode: str | None = None,
        references: str | None = None,
        **kwargs,
    ) -> dict:
        """Fetch available constraints for a given dataflow and parameters."""
        # pylint: disable=import-outside-toplevel
        import json

        from openbb_core.provider.utils.helpers import make_request
        from requests.exceptions import RequestException

        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        kwargs_sorted = sorted(kwargs.items())
        kwargs_tuple = tuple(kwargs_sorted)

        cache_key = (
            f"{dataflow_id}:{key}:{component_id}:{mode}:{references}:{kwargs_tuple}"
        )

        with self._constraints_lock:
            if cached_constraints := self._constraints_cache.get(cache_key):
                return cached_constraints

        df = self.dataflows[dataflow_id]
        agency_id = df.get("agencyID")

        if not agency_id:
            raise ValueError(f"Agency ID not found for dataflow '{dataflow_id}'.")

        # Note: URL length is now primarily managed by table_builder.py which limits
        # constraint keys to depth 0-1 codes when there are many indicators.
        # This fallback is kept as a safety net for edge cases.
        processed_key = key

        base_url = (
            f"https://api.imf.org/external/sdmx/3.0/availability/dataflow/"
            f"{agency_id}/{dataflow_id}/%2B/{processed_key}/{component_id or 'all'}"
        )
        query_params = {
            "mode": mode,
            "references": references,
        }
        c_params = {f"c[{k}]": v for k, v in kwargs.items() if v}
        query_params.update(c_params)

        query_params = {k: v for k, v in query_params.items() if v is not None}
        url = (
            base_url + "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
            if query_params
            else base_url
        )
        json_response: dict = {}
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": "Open Data Platform - IMF Metadata Utility",
            }
            response = make_request(url, headers=headers)
            response.raise_for_status()
            json_response = response.json()
        except json.JSONDecodeError as e:
            raise OpenBBError(
                f"Unexpected response format when fetching constraints {dataflow_id}: {e}"
                + f" -> {url}"
            ) from None
        except RequestException as e:
            raise OpenBBError(
                f"An error occurred while fetching constraints {dataflow_id}: {e} -> {url}"
            ) from None

        extracted_values: dict = {}
        json_data = json_response.get("data", {})
        data_constraints = json_data.get("dataConstraints", [])

        for constraint in data_constraints:
            for region in constraint.get("cubeRegions", []):
                for kv in region.get("keyValues", []):
                    dim_id = kv.get("id")
                    if dim_id:
                        if dim_id not in extracted_values:
                            extracted_values[dim_id] = []
                        for val in kv.get("values", []):
                            if isinstance(val, dict):
                                extracted_values[dim_id].append(val.get("value"))
                            else:
                                extracted_values[dim_id].append(val)
                for comp in region.get("components", []):
                    dim_id = comp.get("id")
                    if dim_id:
                        if dim_id not in extracted_values:
                            extracted_values[dim_id] = []
                        for val in comp.get("values", []):
                            if isinstance(val, dict):
                                extracted_values[dim_id].append(val.get("value"))
                            else:
                                extracted_values[dim_id].append(val)

        for dim_id, values in list(extracted_values.items()):
            # Remove falsy values, deduplicate.
            unique_values = {v for v in values if v}
            extracted_values[dim_id] = list(unique_values)

        key_values = [{"id": k, "values": v} for k, v in extracted_values.items()]

        result = {"key_values": key_values, "full_response": json_response}

        with self._constraints_lock:
            self._constraints_cache[cache_key] = result

        return result

    def get_indicators_in(self, dataflow_id: str) -> list:
        """Get indicators available in a given dataflow."""
        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        dataflow_obj = self.dataflows[dataflow_id]
        dataflow_name = dataflow_obj.get("name", "").replace("\\xa0", "").strip()
        structure_ref = dataflow_obj.get("structureRef", {})
        structure_id = structure_ref.get("id", "")
        agency_id = dataflow_obj.get("agencyID", structure_ref.get("agencyID", "IMF"))
        dsd_id = structure_ref.get("id", "")

        if not dsd_id or dsd_id not in self.datastructures:
            raise ValueError(f"Data structure not found for dataflow '{dataflow_id}'.")

        dsd = self.datastructures[dsd_id]
        all_dims = dsd.get("dimensions", [])

        # Get valid codes from parameters API
        try:
            params = self.get_dataflow_parameters(dataflow_id)
        except Exception:  # noqa: BLE001
            params = {}

        full_indicator_list = []

        indicator_id_candidates = [
            "INDICATOR",
            "PRODUCTION_INDEX",
            "COICOP_1999",
            "INDEX_TYPE",
            "ACTIVITY",
            "PRODUCT",
            "SERIES",
            "ITEM",
            "BOP_ACCOUNTING_ENTRY",
            "ACCOUNTING_ENTRY",
        ]

        for dim in all_dims:
            dim_id = dim.get("id")

            is_indicator_candidate = dim_id in indicator_id_candidates
            if not is_indicator_candidate and any(
                keyword in dim_id
                for keyword in ["INDICATOR", "ACCOUNTING_ENTRY", "ENTRY"]
            ):
                is_indicator_candidate = True

            if not is_indicator_candidate:
                continue

            # Get valid codes with labels from parameters API
            dim_params = params.get(dim_id, [])
            if not dim_params:
                continue

            # Resolve codelist ID for this dimension to look up descriptions
            codelist_id = self._resolve_codelist_id(dataflow_id, dsd_id, dim_id, dim)
            descriptions_map: dict = {}
            if codelist_id:
                # Try to get cached descriptions
                descriptions_map = self._codelist_descriptions.get(codelist_id, {})
                # If not cached, try to load the codelist to populate descriptions
                if not descriptions_map and codelist_id not in self._codelist_cache:
                    try:
                        self._get_codelist_map(codelist_id, agency_id, dataflow_id)
                        descriptions_map = self._codelist_descriptions.get(
                            codelist_id, {}
                        )
                    except Exception:  # noqa
                        pass  # Codelist not available, continue without descriptions

            # Parameters API already provides labels - use them directly
            for param in dim_params:
                code_id = param["value"]
                code_label = param.get("label", code_id)
                series_id = f"{dataflow_id}::{code_id}"

                # Look up description from codelist, fall back to label if not found
                description = descriptions_map.get(code_id, "")

                indicator_entry = {
                    "dataflow_id": dataflow_id,
                    "dataflow_name": dataflow_name,
                    "structure_id": structure_id,
                    "agency_id": agency_id,
                    "dimension_id": dim_id,
                    "indicator": code_id,
                    "label": code_label,
                    "description": description,
                    "series_id": series_id,
                }
                full_indicator_list.append(indicator_entry)

        # Check for activity-related codelists
        dim_ids = {d.get("id") for d in all_dims if d.get("id")}
        if "ACTIVITY" in dim_ids:
            activity_codelist_id = f"CL_{dataflow_id}_ACTIVITY"
            if activity_codelist_id in self._codelist_cache:
                codes_map = self._get_codelist_map(
                    activity_codelist_id, agency_id, dataflow_id
                )
                descriptions_map = self._codelist_descriptions.get(
                    activity_codelist_id, {}
                )
                for code_id, code_name in codes_map.items():
                    series_id = f"{dataflow_id}::{code_id}"
                    entry = {
                        "dataflow_id": dataflow_id,
                        "dataflow_name": dataflow_name,
                        "structure_id": structure_id,
                        "agency_id": agency_id,
                        "dimension_id": "ACTIVITY",
                        "indicator": code_id,
                        "label": code_name,
                        "description": descriptions_map.get(code_id, ""),
                        "series_id": series_id,
                    }
                    full_indicator_list.append(entry)

        if not full_indicator_list:
            raise KeyError(
                f"Could not find an indicator-like dimension for dataflow '{dataflow_id}'."
            )

        return full_indicator_list

    def _resolve_codelist_id(
        self, dataflow_id: str, dsd_id: str | None, dim_id: str, dim_meta: dict
    ) -> str | None:
        if not dim_id:
            return None

        # Check for explicit codelist reference first
        representation = dim_meta.get("representation", {})
        codelist_ref = representation.get("codelist")
        if isinstance(codelist_ref, dict):
            return codelist_ref.get("id")
        if isinstance(codelist_ref, str):
            return codelist_ref

        candidates: list[str] = []
        seen = set()

        def add_candidate(candidate: str):
            if candidate and candidate not in seen:
                candidates.append(candidate)
                seen.add(candidate)

        concept_ref = dim_meta.get("conceptRef") or {}
        concept_id = concept_ref.get("id")

        # For country-like dimensions (JURISDICTION, REF_AREA, COUNTRY, etc.),
        # prioritize dataflow-specific ISO country codelists first.
        country_dims = {"JURISDICTION", "REF_AREA", "COUNTRY", "AREA"}
        is_country_dim = dim_id.upper() in country_dims or (
            concept_id and concept_id.upper() in {"COUNTRY", "REF_AREA"}
        )

        if is_country_dim and dataflow_id:
            # Try dataflow-specific ISO country codelist first
            base_dataflow = dataflow_id.split("_")[0]
            add_candidate(f"CL_{base_dataflow}_ISO_COUNTRY")
            add_candidate(f"CL_{dataflow_id}_COUNTRY")
            add_candidate(f"CL_{base_dataflow}_COUNTRY")

        # Priority 1: Dataflow-specific patterns (most specific first)
        if dataflow_id:
            add_candidate(f"CL_{dataflow_id}_{dim_id}")
            add_candidate(f"CL_{dataflow_id}_{dim_id}_PUB")  # _PUB suffix variant
            if "COUNTRY" in dim_id:
                add_candidate(f"CL_{dataflow_id}_COUNTRY")
                add_candidate(f"CL_{dataflow_id}_COUNTRY_PUB")
            if "_" in dataflow_id:
                base_dataflow = dataflow_id.split("_")[0]
                add_candidate(f"CL_{base_dataflow}_{dim_id}")
                add_candidate(f"CL_{base_dataflow}_{dim_id}_PUB")

        # Priority 2: DSD patterns
        if dsd_id:
            dsd_base = dsd_id.replace("DSD_", "")
            add_candidate(f"CL_{dsd_base}_{dim_id}")

        # Priority 3: Parent scheme patterns
        parent_scheme_id = concept_ref.get("maintainableParentID")
        if parent_scheme_id:
            scheme_base = parent_scheme_id.replace("CS_", "CL_", 1)
            add_candidate(f"{scheme_base}_{dim_id}")
            add_candidate(scheme_base)

        # Priority 4: Direct/generic matches (fallback)
        add_candidate(f"CL_{dim_id}")
        if concept_id:
            add_candidate(f"CL_{concept_id}")

        # Check cache for exact matches first
        for candidate in candidates:
            if candidate in self._codelist_cache:
                return candidate

        # Case-insensitive fallback for dataflow-specific codelists
        # IMF has inconsistent casing (e.g., CL_LS_TYPE_OF_TRANSFORMAtION)
        cache_keys_upper = {k.upper(): k for k in self._codelist_cache}
        for candidate in candidates:
            actual_key = cache_keys_upper.get(candidate.upper())
            if actual_key:
                return actual_key

        # Consolidated mapping for common variations
        # This combines the old variations dict and generic_dimensions list
        common_mappings = {
            # Geographic dimensions
            (
                "REF_AREA",
                "AREA",
                "COUNTRY",
                "JURISDICTION",
                "GEOGRAPHICAL_AREA",
            ): "AREA",
            ("COUNTERPART_COUNTRY",): "COUNTRY",
            # Statistical dimensions
            ("COMPOSITE_BREAKDOWN", "COMP_BREAKDOWN"): "COMPOSITE_BREAKDOWN",
            ("DISABILITY_STATUS", "DISABILITY"): "DISABILITY",
            ("INCOME_WEALTH_QUANTILE", "QUANTILE"): "QUANTILE",
            ("TYPE_OF_TRANSFORMATION", "TRANSFORMATION"): "TRANSFORMATION",
            ("WGT_TYPE", "WEIGHT_TYPE", "CTOT_WEIGHT_TYPE"): "WEIGHT_TYPE",
            ("INDICATOR", "INDICATORS"): "INDICATOR",
            ("UNIT", "UNIT_MEASURE", "UNIT_MULT"): "UNIT",
        }

        # Check if dimension matches any common pattern
        for patterns, base_name in common_mappings.items():
            if any(pattern in dim_id.upper() for pattern in patterns):
                # Try generic first
                generic_cl = f"CL_{base_name}"
                if generic_cl in self._codelist_cache:
                    return generic_cl
                # Then try dataflow-specific
                specific_cl = f"CL_{dataflow_id}_{base_name}"
                if specific_cl in self._codelist_cache:
                    return specific_cl

        # Special handling for counterpart dimensions
        if "COUNTERPART_" in dim_id:
            base_dim_id = dim_id.replace("COUNTERPART_", "")
            if dsd_id and dsd_id in self.datastructures:
                dsd = self.datastructures[dsd_id]
                for d in dsd.get("dimensions", []):
                    if d.get("id") == base_dim_id:
                        return self._resolve_codelist_id(
                            dataflow_id, dsd_id, base_dim_id, d
                        )

        # Activity/Product fallbacks
        if "ACTIVITY" in dim_id.upper() or "PRODUCTION_INDEX" in dim_id.upper():
            activity_candidates = [
                "CL_PPI_ACTIVITY",
                "CL_MCDREO_ACTIVITY",
                "CL_ACTIVITY_ISIC4",
                "CL_NEA_ACTIVITY",
                "CL_ACTIVITY",
            ]
            for candidate in activity_candidates:
                if candidate in self._codelist_cache:
                    return candidate

        if "COICOP" in dim_id.upper():
            coicop_candidates = ["CL_COICOP_1999", "CL_COICOP_2018"]
            for candidate in coicop_candidates:
                if candidate in self._codelist_cache:
                    return candidate

        # Fuzzy matching as last resort
        dim_upper = dim_id.upper()

        # Try exact substring match
        for cache_key in self._codelist_cache:
            if cache_key.startswith("CL_MASTER"):
                continue
            if dim_upper in cache_key.upper():
                return cache_key

        # Try matching significant parts
        dim_parts = [p for p in dim_id.split("_") if len(p) > 2]
        if len(dim_parts) > 1:
            for cache_key in self._codelist_cache:
                if cache_key.startswith("CL_MASTER"):
                    continue
                cache_key_upper = cache_key.upper()
                if all(part.upper() in cache_key_upper for part in dim_parts):
                    return cache_key

        # Return first candidate or None
        return candidates[0] if candidates else None

    def _build_time_period_parameters(
        self, constraints_response: dict | None
    ) -> tuple[list[dict], str | None]:
        """Build time period parameters from a constraints API response."""
        return build_time_period_params(constraints_response)

    def _parse_codelist_urn(self, urn: str) -> str | None:
        """Parse codelist ID from owningCodelistUrn."""
        return parse_codelist_urn(urn)

    def _parse_indicator_code_from_urn(self, code_urn: str) -> str | None:
        """Parse indicator code from hierarchicalCode's code URN."""
        return parse_indicator_code_from_urn(code_urn)

    def _parse_codelist_id_from_urn(self, code_urn: str) -> str | None:
        """Parse codelist ID from hierarchicalCode's code URN."""
        return parse_codelist_id_from_urn(code_urn)

    def _get_dimension_for_codelist(
        self, dataflow_id: str, codelist_id: str
    ) -> str | None:
        """
        Find which dimension uses the given codelist ID.

        Parameters
        ----------
        dataflow_id : str
            The dataflow ID
        codelist_id : str
            The codelist ID (e.g., "CL_BOP_INDICATOR")

        Returns
        -------
        str | None
            The dimension ID that uses this codelist, or None if not found.
        """
        if dataflow_id not in self.dataflows:
            return None

        df_obj = self.dataflows[dataflow_id]
        dsd_id = df_obj.get("structureRef", {}).get("id")
        if not dsd_id or dsd_id not in self.datastructures:
            return None

        dsd = self.datastructures[dsd_id]
        dimensions = dsd.get("dimensions", [])

        # First pass: exact match
        for dim in dimensions:
            dim_id = dim.get("id")
            if not dim_id:
                continue

            # Resolve the codelist for this dimension
            resolved_codelist = self._resolve_codelist_id(
                dataflow_id, dsd_id, dim_id, dim
            )
            if resolved_codelist == codelist_id:
                return dim_id

        # Second pass: fuzzy match by dimension name appearing anywhere in codelist ID
        # e.g., CL_IRFCL_DEFAULT_INDICATOR_PUB2 should match INDICATOR dimension
        # Split codelist into segments and check if any segment matches a dimension
        codelist_segments = set(seg.upper() for seg in codelist_id.split("_"))
        for dim in dimensions:
            dim_id = dim.get("id")
            if dim_id and dim_id.upper() in codelist_segments:
                return dim_id

        # Third pass: check if dimension name is a substring of codelist ID
        # Handles cases like CL_IRFCL_DEFAULT_INDICATOR_PUB2 -> INDICATOR
        codelist_upper = codelist_id.upper()
        for dim in dimensions:
            dim_id = dim.get("id")
            if dim_id and dim_id.upper() in codelist_upper:
                return dim_id

        return None

    def _extract_all_codelists_from_hierarchy(self, hierarchy: dict) -> set[str]:
        """Recursively extract ALL codelist IDs from a hierarchy's hierarchicalCodes."""
        return extract_all_codelists_from_hierarchy(hierarchy)

    def _build_hierarchy_to_codelist_map(self) -> dict[str, str]:
        """Build mapping from hierarchy ID to codelist ID."""
        return build_hierarchy_to_codelist_map(self.hierarchies)

    def _build_codelist_to_hierarchies_map(self) -> dict[str, list[str]]:
        """Build reverse mapping from codelist ID to list of hierarchy IDs."""
        return build_codelist_to_hierarchies_map(self.hierarchies)

    def _validate_hierarchy_queryable(self, dataflow_id: str, codes: list) -> bool:
        """
        Check if a hierarchy's codes can actually be queried (map to dimensions, not just attributes).

        Parameters
        ----------
        dataflow_id : str
            The dataflow ID
        codes : list
            List of hierarchical code entries

        Returns
        -------
        bool
            True if at least some codes map to queryable dimensions
        """
        if not codes:
            return False

        # Sample a few codes to check if they map to dimensions
        sample_size = min(10, len(codes))
        valid_count = 0

        for code_entry in codes[:sample_size]:
            code_urn = code_entry.get("code", "")
            if not code_urn:
                continue

            codelist_id = self._parse_codelist_id_from_urn(code_urn)
            if not codelist_id:
                continue

            # Check if this codelist maps to a dimension (not an attribute)
            dimension_id = self._get_dimension_for_codelist(dataflow_id, codelist_id)
            if dimension_id:
                valid_count += 1

        # Consider hierarchy queryable if at least 50% of sampled codes map to dimensions
        return valid_count >= (sample_size * 0.5)

    def get_dataflow_hierarchies(self, dataflow_id: str) -> list[dict]:
        """
        Get all hierarchies (presentation tables) available for a dataflow.

        This supports two types of presentations:
        1. Hierarchies from hierarchy.json (45 codelists)
        2. Presentations embedded in dataflow metadata (31 dataflows)

        Parameters
        ----------
        dataflow_id : str
            The dataflow ID (e.g., "FSIBSIS", "BOP_AGG", "IRFCL")

        Returns
        -------
        list[dict]
            List of hierarchy/presentation metadata dicts.
        """
        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        dataflow_obj = self.dataflows[dataflow_id]
        result = []

        # First, check for hierarchies from hierarchy.json (these have actual structure)
        dsd_id = dataflow_obj.get("structureRef", {}).get("id")

        if dsd_id and dsd_id in self.datastructures:
            dsd = self.datastructures[dsd_id]
            dimensions = dsd.get("dimensions", [])

            indicator_codelist_id = None
            # Priority-ordered list of dimension names to check for indicators
            indicator_candidates = [
                "INDICATOR",
                "COICOP_1999",
                "PRODUCTION_INDEX",
                "ACTIVITY",
                "PRODUCT",
                "SERIES",
                "ITEM",
                "ACCOUNTING_ENTRY",
                "SECTOR",
            ]

            dim_lookup = {d.get("id", ""): d for d in dimensions}
            # Check candidates in priority order (not dimension order)
            for candidate in indicator_candidates:
                if candidate in dim_lookup:
                    dim = dim_lookup[candidate]
                    indicator_codelist_id = self._resolve_codelist_id(
                        dataflow_id, dsd_id, candidate, dim
                    )
                    if indicator_codelist_id:
                        # Check if this codelist actually has hierarchies
                        if self._codelist_to_hierarchies_map.get(indicator_codelist_id):
                            break
                        # If no hierarchies, continue to next candidate
                        indicator_codelist_id = None

            # Fallback: check for any dimension with "INDICATOR" in its name
            if not indicator_codelist_id:
                for dim in dimensions:
                    dim_id = dim.get("id", "")
                    if "INDICATOR" in dim_id and dim_id not in indicator_candidates:
                        indicator_codelist_id = self._resolve_codelist_id(
                            dataflow_id, dsd_id, dim_id, dim
                        )
                        if indicator_codelist_id:
                            break

            if indicator_codelist_id:
                hierarchy_ids = self._codelist_to_hierarchies_map.get(
                    indicator_codelist_id, []
                )
                # Get available indicator values for this dataflow to filter hierarchies
                available_indicator_values: set[str] = set()

                try:
                    params = self.get_dataflow_parameters(dataflow_id)

                    if "INDICATOR" in params:
                        available_indicator_values.update(
                            opt.get("value", "") for opt in params["INDICATOR"]
                        )
                except Exception:  # noqa: S110
                    pass  # If we can't get parameters, include all hierarchies

                for hier_id in hierarchy_ids:
                    hier_obj = self.hierarchies.get(hier_id)
                    hier_code_values: set[str] = set()
                    if hier_obj:
                        # If we have available values, check if this hierarchy is compatible
                        if available_indicator_values:
                            hier_codes_raw = hier_obj.get("hierarchicalCodes", [])

                            def _extract_codes(codes_list):
                                for c in codes_list:
                                    # Extract actual code from URN like:
                                    # urn:sdmx:...CL_BOP_INDICATOR(10.0+.0).NIIP_AFR
                                    code_urn = c.get("code", "")
                                    # Only extract codes from INDICATOR codelists
                                    if (
                                        code_urn
                                        and "INDICATOR" in code_urn
                                        and "." in code_urn
                                    ):
                                        actual_code = code_urn.rsplit(".", 1)[-1]
                                        if actual_code:
                                            hier_code_values.add(  # pylint: disable=W0640
                                                actual_code
                                            )
                                    # Recurse into nested codes
                                    nested = c.get("hierarchicalCodes", [])
                                    if nested:
                                        _extract_codes(nested)  # pylint: disable=W0640

                            _extract_codes(hier_codes_raw)

                            # Check if ANY of the hierarchy's codes exist in the dataflow
                            # Use prefix matching since dataflow codes may have unit suffixes
                            # e.g., hierarchy code "FSI687_TREGK" should match "FSI687_TREGK_USD"
                            if hier_code_values:
                                has_match = False
                                # First try exact match (fast path)
                                if hier_code_values & available_indicator_values:
                                    has_match = True
                                else:
                                    # Prefix matching: check if any available indicator
                                    # starts with any hierarchy code
                                    for hier_code in hier_code_values:
                                        for avail_code in available_indicator_values:
                                            if avail_code.startswith(hier_code):
                                                has_match = True
                                                break
                                        if has_match:
                                            break
                                if not has_match:
                                    # No overlap - skip this hierarchy for this dataflow
                                    continue

                        # Check if hierarchy has multiple top-level codes
                        top_level_codes = hier_obj.get("hierarchicalCodes", [])

                        if len(top_level_codes) > 1 and dataflow_id == "IRFCL":
                            # Split into separate tables - one per top-level code
                            for idx, top_code in enumerate(top_level_codes):
                                top_code_id = top_code.get("id", "")
                                top_code_urn = top_code.get("code", "")
                                # Extract actual code from URN
                                actual_code = (
                                    top_code_urn.rsplit(".", 1)[-1]
                                    if "." in top_code_urn
                                    else top_code_id
                                )
                                # Get label from the codelist specified in the URN
                                urn_codelist_id = self._parse_codelist_id_from_urn(
                                    top_code_urn
                                )
                                table_label = self._codelist_cache.get(
                                    urn_codelist_id or indicator_codelist_id, {}
                                ).get(actual_code, actual_code)
                                # Check for SECTION codelist for better labels
                                section_codelist_id = f"CL_{dataflow_id}_SECTION"
                                section_codes = self._codelist_cache.get(
                                    section_codelist_id, {}
                                )
                                # Match section by prefix in actual_code
                                for (
                                    section_code,
                                    section_label,
                                ) in section_codes.items():
                                    if actual_code.startswith(section_code):
                                        table_label = section_label
                                        break

                                result.append(
                                    {
                                        "id": f"{hier_id}:{top_code_id}",
                                        "name": table_label,
                                        "description": "",
                                        "codelist_id": indicator_codelist_id,
                                        "agency_id": hier_obj.get("agencyID", ""),
                                        "version": hier_obj.get("version", ""),
                                        "type": "hierarchy",
                                        "table_index": idx,
                                        "top_level_code_id": top_code_id,
                                        "indicator_code": actual_code,
                                    }
                                )
                        else:
                            # Single top-level code - return as single table
                            name = hier_obj.get("name", "")
                            descriptions = hier_obj.get("descriptions", {})
                            desc = descriptions.get("en", "") if descriptions else ""
                            result.append(
                                {
                                    "id": hier_id,
                                    "name": name,
                                    "description": desc,
                                    "codelist_id": indicator_codelist_id,
                                    "agency_id": hier_obj.get("agencyID", ""),
                                    "version": hier_obj.get("version", ""),
                                    "type": "hierarchy",
                                }
                            )

        return result

    def get_dataflow_table_structure(
        self, dataflow_id: str, table_id: str | None = None
    ) -> dict:
        """
        Get the presentation table structure for a dataflow.

        Handles both hierarchy-based (hierarchy.json) and embedded presentations.

        Parameters
        ----------
        dataflow_id : str
            The dataflow ID
        table_id : str | None
            The specific hierarchy/table ID. If None, uses the first available.

        Returns
        -------
        dict
            Structure with hierarchy metadata and nested indicators.
        """
        available_hierarchies = self.get_dataflow_hierarchies(dataflow_id)

        if not available_hierarchies:
            raise ValueError(
                f"No presentation hierarchies found for dataflow '{dataflow_id}'"
            )

        # Track if this is a split table (one top-level code from a multi-code hierarchy)
        top_level_code_filter: str | None = None
        base_hierarchy_id: str | None = None

        if table_id:
            # Find the specific table
            selected_table = None
            for h in available_hierarchies:
                if h["id"] == table_id:
                    selected_table = h
                    break
            if not selected_table:
                raise ValueError(
                    f"Hierarchy '{table_id}' not found. "
                    f"Available: {[h['id'] for h in available_hierarchies]}"
                )
            # Check if this is a split table (format: "base_id:top_level_code_id")
            if ":" in table_id:
                base_hierarchy_id, top_level_code_filter = table_id.split(":", 1)
            else:
                base_hierarchy_id = table_id
        else:
            selected_table = available_hierarchies[0]
            table_id = selected_table.get("id", "")
            if table_id and ":" in table_id:
                base_hierarchy_id, top_level_code_filter = table_id.split(":", 1)
            else:
                base_hierarchy_id = table_id

        # Handle hierarchy-based presentations
        # Use base_hierarchy_id to look up the actual hierarchy object
        hierarchy = self.hierarchies.get(base_hierarchy_id or table_id)
        if not hierarchy:
            raise ValueError(
                f"Hierarchy '{base_hierarchy_id or table_id}' not found in cache"
            )

        if not table_id:
            raise ValueError("table_id cannot be None")

        codelist_id = self._hierarchy_to_codelist_map.get(base_hierarchy_id or table_id)

        dataflow_obj = self.dataflows.get(dataflow_id, {})
        agency_id = dataflow_obj.get("agencyID", "IMF")
        agency_clean = agency_id.replace(".", "_")

        structure_ref = dataflow_obj.get("structureRef", {})
        dsd_id = structure_ref.get("id")
        dsd_obj = self.datastructures.get(dsd_id, {}) if dsd_id else {}
        dimensions = dsd_obj.get("dimensions", []) if isinstance(dsd_obj, dict) else []

        indicator_dimension_order: dict[str, int] = {}
        indicator_id_candidates = [
            "INDICATOR",
            "PRODUCTION_INDEX",
            "COICOP_1999",
            "ACTIVITY",
            "PRODUCT",
            "SERIES",
            "ITEM",
            "BOP_ACCOUNTING_ENTRY",
            "ACCOUNTING_ENTRY",
        ]

        for idx, dim in enumerate(dimensions):
            dim_id = dim.get("id", "")
            if not dim_id:
                continue
            is_indicator_candidate = dim_id in indicator_id_candidates or any(
                keyword in dim_id
                for keyword in ["INDICATOR", "ACCOUNTING_ENTRY", "ENTRY"]
            )
            if is_indicator_candidate:
                indicator_dimension_order[dim_id] = idx

        codelist_dimension_cache: dict[str, str | None] = {}
        # Cache for per-codelist label and description lookups
        # Hierarchies can mix codes from multiple codelists (e.g., CL_BOP_INDICATOR + CL_BOP_ACCOUNTING_ENTRY)
        codelist_labels_cache: dict[str, dict] = {}
        codelist_desc_cache: dict[str, dict] = {}

        def process_hierarchical_codes(
            codes: list,
            parent_id: str | None = None,
            depth: int = 0,
            parent_codes: list | None = None,
            parent_dimension_codes: dict[str, str] | None = None,
            order_counter: list | None = None,
            parent_full_label: str | None = None,
            ancestor_labels: list | None = None,
        ) -> list[dict]:
            """Recursively process hierarchical codes into flat indicator list."""
            # pylint: disable=import-outside-toplevel
            import re

            indicators = []

            if parent_codes is None:
                parent_codes = []
            if parent_dimension_codes is None:
                parent_dimension_codes = {}
            if order_counter is None:
                order_counter = [0]
            if ancestor_labels is None:
                ancestor_labels = []

            for code_entry in codes:
                code_id = code_entry.get("id")
                code_urn = code_entry.get("code", "")
                level = code_entry.get("level", "0")
                indicator_code = self._parse_indicator_code_from_urn(code_urn)
                codelist_id_for_code = self._parse_codelist_id_from_urn(code_urn)
                dimension_id = None

                if codelist_id_for_code:
                    if codelist_id_for_code not in codelist_dimension_cache:
                        codelist_dimension_cache[codelist_id_for_code] = (
                            self._get_dimension_for_codelist(
                                dataflow_id, codelist_id_for_code
                            )
                        )
                    dimension_id = codelist_dimension_cache[codelist_id_for_code]
                    # Cache labels and descriptions for this codelist
                    # Check if not in cache OR if cached value is empty (failed previous fetch)
                    cached_is_empty = not codelist_labels_cache.get(
                        codelist_id_for_code
                    )
                    if (
                        codelist_id_for_code not in codelist_labels_cache
                        or cached_is_empty
                    ):
                        # Try to get from main cache first
                        cached_labels = self._codelist_cache.get(
                            codelist_id_for_code, {}
                        )
                        cached_descs = self._codelist_descriptions.get(
                            codelist_id_for_code, {}
                        )
                        # If not found, try to fetch from API using URN agency
                        if not cached_labels and code_urn:
                            urn_agency = self._parse_agency_from_urn(code_urn)
                            if urn_agency:
                                self._fetch_single_codelist(
                                    urn_agency, codelist_id_for_code
                                )
                                cached_labels = self._codelist_cache.get(
                                    codelist_id_for_code, {}
                                )
                                cached_descs = self._codelist_descriptions.get(
                                    codelist_id_for_code, {}
                                )
                        codelist_labels_cache[codelist_id_for_code] = cached_labels
                        codelist_desc_cache[codelist_id_for_code] = cached_descs

                # Look up label from the code's actual codelist, not just the owning codelist
                code_labels = (
                    codelist_labels_cache.get(codelist_id_for_code, {})
                    if codelist_id_for_code
                    else {}
                )
                code_descs = (
                    codelist_desc_cache.get(codelist_id_for_code, {})
                    if codelist_id_for_code
                    else {}
                )
                full_label = (
                    code_labels.get(indicator_code, code_id)
                    if indicator_code
                    else code_id
                )
                # Detect path-based labels in INDICATOR_PUB codelists
                # These codelists store labels as comma-separated hierarchical paths
                # e.g., "Section A, Category B, Item C" -> extract relative portion
                # The hierarchy provides context, so we only need what's NEW at this node
                label = full_label
                # Check if this codelist uses path-style labels:
                # 1. Named pattern: "_INDICATOR_PUB" in codelist name
                # 2. Explicit codelist: CL_DIP_INDICATOR uses path-style labels
                is_path_style_codelist = codelist_id_for_code and (
                    "_INDICATOR_PUB" in codelist_id_for_code
                    or codelist_id_for_code == "CL_DIP_INDICATOR"
                )
                if is_path_style_codelist:
                    # Special case for CL_DIP_INDICATOR: the first part of every label
                    # is "Inward Direct investment" or "Outward Direct investment" which
                    # is redundant with the parent categories "Inward Indicators"/"Outward Indicators"
                    # Just skip the first part for DIP labels
                    if (
                        codelist_id_for_code == "CL_DIP_INDICATOR"
                        and ", " in full_label
                    ):
                        parts = full_label.split(", ")
                        if len(parts) > 1 and (
                            parts[0].startswith("Inward")
                            or parts[0].startswith("Outward")
                        ):
                            label = ", ".join(parts[1:])
                    # For other path-style codelists, try exact prefix match with parent's full label
                    elif parent_full_label and full_label.startswith(parent_full_label):
                        # Remove parent's label prefix and separator
                        relative_label = full_label[len(parent_full_label) :].lstrip(
                            ", :"
                        )
                        if relative_label:
                            label = relative_label
                        elif ", " in full_label or ": " in full_label:
                            # Child has same label as parent (e.g., USD vs FTO gold variants)
                            parts = re.split(r", |: ", full_label)
                            label = parts[-1] if parts else full_label
                    elif ancestor_labels and (", " in full_label or ": " in full_label):
                        # This handles cases where hierarchy mixes codelists
                        def normalize_part(s: str) -> str:
                            """Normalize for comparison: lowercase, remove punctuation."""
                            return re.sub(r"[^a-z0-9]", "", s.lower())

                        # Split label by both ", " and ":" separators
                        def split_label(lbl: str) -> list:
                            """Split by comma-space and colon."""
                            # First split by ", "
                            parts = lbl.split(", ")
                            # Then split each part by ":"
                            result = []
                            for p in parts:
                                if ":" in p:
                                    subparts = p.split(":")
                                    result.extend(
                                        [sp.strip() for sp in subparts if sp.strip()]
                                    )
                                else:
                                    result.append(p)
                            return result

                        # Collect all parts from all ancestor labels
                        all_ancestor_parts = []
                        for anc_label in ancestor_labels:
                            all_ancestor_parts.extend(split_label(anc_label))

                        child_parts = split_label(full_label)

                        # Build set of normalized ancestor parts
                        ancestor_normalized = {
                            normalize_part(p) for p in all_ancestor_parts
                        }

                        # Find parts in child that are genuinely new
                        new_parts = []
                        for part in child_parts:
                            part_norm = normalize_part(part)
                            # Allow for "Total X" in ancestor matching "X" in child
                            is_in_ancestor = part_norm in ancestor_normalized
                            if not is_in_ancestor:
                                for pn in ancestor_normalized:
                                    # Check "totalX" matching "X"
                                    if pn.startswith("total") and pn[5:] == part_norm:
                                        is_in_ancestor = True
                                        break
                                    # Check if ancestor part is contained in child part
                                    # e.g., "outflows" in "outflowsreservestemplate"
                                    if len(pn) >= 6 and pn in part_norm:
                                        is_in_ancestor = True
                                        break
                                    # Check if strings are very similar (>80% overlap)
                                    # This handles encoding differences like "visvis" vs "vissvis"
                                    # and inconsistent comma placement in IMF data
                                    if len(part_norm) >= 15 and len(pn) >= 15:
                                        # Check if one contains most of the other
                                        shorter = min(part_norm, pn, key=len)
                                        longer = max(part_norm, pn, key=len)
                                        # If 80%+ of shorter is in longer, consider match
                                        if shorter in longer or (
                                            len(shorter) > 30
                                            and any(
                                                shorter[i : i + 30] in longer
                                                for i in range(len(shorter) - 30)
                                            )
                                        ):
                                            is_in_ancestor = True
                                            break
                            if not is_in_ancestor:
                                new_parts.append(part)

                        if new_parts:
                            # For IRFCL path labels, keep all parts
                            if (
                                codelist_id_for_code
                                and "IRFCL" in codelist_id_for_code
                                and len(new_parts) >= 3
                            ):
                                # Keep the full label - synthetic groups will organize it
                                label = ", ".join(new_parts)
                            else:
                                label = (
                                    ", ".join(new_parts)
                                    if new_parts
                                    else child_parts[-1] if child_parts else full_label
                                )
                        else:
                            label = child_parts[-1] if child_parts else full_label
                    elif ", " in full_label:
                        # No ancestors - this is a top-level node
                        # Take just the LAST part as the actual indicator label
                        parts = full_label.split(", ")
                        label = parts[-1] if parts else full_label
                elif (
                    parent_full_label
                    and ", " in full_label
                    and full_label.startswith(parent_full_label)
                ):
                    # For other codelists, check if parent's label is a prefix
                    label = full_label.rsplit(", ", 1)[-1]
                description = (
                    code_descs.get(indicator_code, "") if indicator_code else ""
                )

                children = code_entry.get("hierarchicalCodes", [])
                is_group = len(children) > 0

                current_dimension_codes = parent_dimension_codes.copy()
                if dimension_id and indicator_code:
                    current_dimension_codes[dimension_id] = indicator_code

                # Clean parent_id: if it contains codelist prefix, extract just the code
                clean_parent_id = parent_id
                if parent_id and "___" in parent_id:
                    clean_parent_id = parent_id.split("___")[-1]

                # Assign sequential order to ALL nodes (groups and leaf nodes)
                order_counter[0] += 1
                current_order = order_counter[0]

                # For BOP dataflows, use depth (actual nesting) instead of IMF's
                # inconsistent level attribute
                use_depth_for_level = dataflow_id in ("BOP", "BOP_AGG", "IIP", "IIPCC")
                node_level = (
                    depth if use_depth_for_level else (int(level) if level else depth)
                )

                indicator_info = {
                    "id": code_id,
                    "indicator_code": indicator_code,
                    "label": label,
                    "description": description,
                    "order": current_order,
                    "level": node_level,
                    "depth": depth,
                    "parent_id": clean_parent_id,
                    "is_group": is_group,
                    "code_urn": code_urn,
                    "dimension_id": dimension_id,
                }

                # Only build series_id if indicator_code belongs to a queryable dimension
                if indicator_code and dimension_id:
                    # Filter to only dimensions that have a known position
                    ordered_dims = sorted(
                        [
                            (dim_id_iter, indicator_dimension_order[dim_id_iter])
                            for dim_id_iter in current_dimension_codes
                            if dim_id_iter in indicator_dimension_order
                            and current_dimension_codes.get(dim_id_iter)
                        ],
                        key=lambda item: item[1],
                    )
                    ordered_codes = [
                        current_dimension_codes[dim_id_iter]
                        for dim_id_iter, _ in ordered_dims
                    ]
                    unordered_dims = [
                        dim_id_iter
                        for dim_id_iter in current_dimension_codes
                        if dim_id_iter not in indicator_dimension_order
                        and current_dimension_codes.get(dim_id_iter)
                    ]
                    ordered_codes.extend(
                        [
                            current_dimension_codes[dim_id_iter]
                            for dim_id_iter in sorted(unordered_dims)
                        ]
                    )

                    if ordered_codes:
                        combined_codes = "_".join(ordered_codes)
                        indicator_info["series_id"] = (
                            f"{agency_clean}_{dataflow_id}_{combined_codes}"
                        )
                    else:
                        # Fallback to parent code ordering when dimension mapping fails
                        fallback_codes = parent_codes + [indicator_code]
                        indicator_info["series_id"] = (
                            f"{agency_clean}_{dataflow_id}_{'_'.join(fallback_codes)}"
                        )

                indicators.append(indicator_info)

                if children:
                    child_parent_codes = parent_codes + (
                        [indicator_code] if indicator_code else []
                    )
                    # Accumulate ancestor labels for path-based label extraction
                    child_ancestor_labels = ancestor_labels + [full_label]
                    child_indicators = process_hierarchical_codes(
                        children,
                        parent_id=code_id,
                        depth=depth + 1,
                        parent_codes=child_parent_codes,
                        parent_dimension_codes=current_dimension_codes.copy(),
                        order_counter=order_counter,
                        parent_full_label=full_label,
                        ancestor_labels=child_ancestor_labels,
                    )
                    indicators.extend(child_indicators)

            return indicators

        hierarchical_codes = hierarchy.get("hierarchicalCodes", [])

        # If a top-level code filter is set, only include that specific top-level code
        if top_level_code_filter:
            filtered_codes = [
                c for c in hierarchical_codes if c.get("id") == top_level_code_filter
            ]
            if filtered_codes:
                hierarchical_codes = filtered_codes

        indicators = process_hierarchical_codes(hierarchical_codes)

        # Post-processing: Fix IRFCL hierarchy issues
        if dataflow_id == "IRFCL":
            indicators = self._fix_irfcl_hierarchy(indicators)

        # Get table name from selected_table if available (for split tables)
        table_name = (
            selected_table.get("name", hierarchy.get("name"))
            if selected_table
            else hierarchy.get("name")
        )

        return {
            "hierarchy_id": table_id,  # Use full table_id including split suffix
            "hierarchy_name": table_name,
            "hierarchy_description": hierarchy.get("description", ""),
            "dataflow_id": dataflow_id,
            "codelist_id": codelist_id,
            "agency_id": hierarchy.get("agencyID"),
            "version": hierarchy.get("version"),
            "indicators": indicators,
            "total_indicators": len([i for i in indicators if not i["is_group"]]),
            "total_groups": len([i for i in indicators if i["is_group"]]),
            "type": "hierarchy",
        }

    def _fix_irfcl_hierarchy(self, indicators: list[dict]) -> list[dict]:
        """
        Fix IRFCL hierarchy issues where instrument types are incorrectly nested.

        The IMF hierarchy has "futures", "swaps", "options", "other" as children of
        "forwards", but they should be siblings (different instrument types at the
        same level). This method re-parents them to be siblings of "forwards".
        """
        # Find "forwards" node and get its parent
        forwards_node = None
        for ind in indicators:
            if ind.get("label", "").lower() == "forwards":
                forwards_node = ind
                break

        if not forwards_node:
            return indicators

        forwards_id = forwards_node.get("id")
        forwards_parent_id = forwards_node.get("parent_id")
        forwards_depth = forwards_node.get("depth", 0)

        # Re-parent children of "forwards" to be siblings instead
        instrument_labels = {"futures", "swaps", "options", "other"}
        for ind in indicators:
            if ind.get("parent_id") == forwards_id:
                label_lower = ind.get("label", "").lower()
                if label_lower in instrument_labels:
                    # Move to same level as forwards
                    ind["parent_id"] = forwards_parent_id
                    ind["depth"] = forwards_depth

        return indicators

    def _create_synthetic_groups_for_shared_prefixes(
        self, indicators: list[dict]
    ) -> list[dict]:
        """
        Create synthetic group nodes for IRFCL siblings with shared label patterns.

        For IRFCL path-encoded labels like:
        - "Up to 1 month, Long positions"
        - "More than 1 and up to 3 months, Long positions"

        This creates a parent group "Long positions" and re-parents the children
        with simplified labels ("Up to 1 month", etc.).

        Also handles shared prefixes like "Options in foreign currencies...".
        """
        # pylint: disable=import-outside-toplevel
        import re
        from collections import defaultdict

        # These are specific to IRFCL memo items structure
        IRFCL_PATH_PATTERNS = [  # pylint: disable=C0103
            "Options in foreign currencies",
            "Up to 1 month",
            "More than 1 and up to",
            "More than 3 months",
            "In-the-money",
            "Long positions",
            "Short positions",
        ]

        def is_irfcl_path_label(label: str) -> bool:
            """Check if label contains IRFCL path patterns."""
            return any(
                pattern.lower() in label.lower() for pattern in IRFCL_PATH_PATTERNS
            )

        # Group indicators by parent_id
        by_parent: dict[str | None, list[dict]] = defaultdict(list)
        for ind in indicators:
            by_parent[ind.get("parent_id")].append(ind)

        # Track new synthetic groups
        synthetic_groups: list[dict] = []

        # For each parent, check if children share a common prefix OR suffix
        for parent_id, children in by_parent.items():
            # Only process if multiple children with comma-separated labels
            # and they have IRFCL-specific path patterns (time periods, positions, options)
            path_children = [
                c
                for c in children
                if ", " in c.get("label", "")
                and c.get("id")
                and is_irfcl_path_label(c.get("label", ""))
            ]
            if len(path_children) < 2:
                continue

            # Find common prefix among path_children labels
            labels = [c["label"] for c in path_children]
            split_labels = [lbl.split(", ") for lbl in labels]
            if not all(split_labels):
                continue

            # Find how many leading parts are shared (prefix)
            min_parts = min(len(parts) for parts in split_labels)
            shared_prefix_count = 0
            for i in range(min_parts - 1):
                first_part = split_labels[0][i]
                if all(parts[i] == first_part for parts in split_labels):
                    shared_prefix_count += 1
                else:
                    break

            # Find how many trailing parts are shared (suffix)
            shared_suffix_count = 0
            for i in range(1, min_parts):
                last_part = split_labels[0][-i]
                if all(parts[-i] == last_part for parts in split_labels):
                    shared_suffix_count += 1
                else:
                    break

            # Use whichever is longer (prefix or suffix), prefer suffix for IRFCL
            if shared_suffix_count > 0 and shared_suffix_count >= shared_prefix_count:
                suffix_parts = split_labels[0][-shared_suffix_count:]
                # Reverse so outermost (last part) is created first as parent
                suffix_parts_reversed = list(reversed(suffix_parts))
                first_child_order = min(c.get("order", 0) for c in path_children)
                first_child_depth = path_children[0].get("depth", 0)
                # Create nested synthetic groups
                current_parent_id = parent_id
                current_depth = first_child_depth
                innermost_synthetic_id = None

                for i, suffix_part in enumerate(suffix_parts_reversed):
                    synthetic_id = f"_SYNTH_{current_parent_id}_{re.sub(r'[^a-zA-Z0-9]', '_', suffix_part[:30])}_{i}"
                    synthetic_group = {
                        "id": synthetic_id,
                        "indicator_code": None,
                        "label": suffix_part,
                        "description": "",
                        "order": first_child_order - 0.5 + (i * 0.01),
                        "level": current_depth,
                        "depth": current_depth,
                        "parent_id": current_parent_id,
                        "is_group": True,
                        "code_urn": None,
                        "dimension_id": None,
                        "series_id": None,
                    }
                    synthetic_groups.append(synthetic_group)
                    # Next group will be child of this one
                    current_parent_id = synthetic_id
                    current_depth += 1
                    innermost_synthetic_id = synthetic_id

                # re-parent to innermost synthetic group and remove suffix
                for child in path_children:
                    child_parts = child["label"].split(", ")
                    remaining_parts = child_parts[:-shared_suffix_count]
                    if remaining_parts:
                        child["label"] = ", ".join(remaining_parts)
                    child["parent_id"] = innermost_synthetic_id
                    child["depth"] = current_depth
                    child["depth"] = first_child_depth + 1

            elif shared_prefix_count > 0:
                # Create group from shared prefix
                shared_prefix = ", ".join(split_labels[0][:shared_prefix_count])
                synthetic_id = f"_SYNTH_{parent_id}_{re.sub(r'[^a-zA-Z0-9]', '_', shared_prefix[:30])}"
                first_child_order = min(c.get("order", 0) for c in path_children)
                first_child_depth = path_children[0].get("depth", 0)
                synthetic_group = {
                    "id": synthetic_id,
                    "indicator_code": None,
                    "label": shared_prefix,
                    "description": "",
                    "order": first_child_order - 0.5,
                    "level": first_child_depth,
                    "depth": first_child_depth,
                    "parent_id": parent_id,
                    "is_group": True,
                    "code_urn": None,
                    "dimension_id": None,
                    "series_id": None,
                }
                synthetic_groups.append(synthetic_group)

                # re-parent and remove prefix
                for child in path_children:
                    child_parts = child["label"].split(", ")
                    remaining_parts = child_parts[shared_prefix_count:]
                    if remaining_parts:
                        child["label"] = ", ".join(remaining_parts)
                    child["parent_id"] = synthetic_id
                    child["depth"] = first_child_depth + 1

        # Merge synthetic groups into indicators list
        if synthetic_groups:
            all_indicators = indicators + synthetic_groups
            all_indicators.sort(key=lambda x: x.get("order", 0))
            for i, ind in enumerate(all_indicators):
                ind["order"] = i + 1
            # After creating one level of groups, the children may still
            # have shared prefixes/suffixes that need another level of grouping
            return self._create_synthetic_groups_for_shared_prefixes(all_indicators)

        return indicators

    def list_all_dataflow_tables(self) -> dict[str, list[dict]]:
        """
        Get a mapping of all dataflows to their available presentation tables.

        Returns a curated list of validated dataflow/table combinations that
        are known to work correctly with the IMF API.

        Returns
        -------
        dict[str, list[dict]]
            Mapping of dataflow IDs to their available hierarchies.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.constants import (
            PRESENTATION_TABLES,
        )

        result: dict[str, list[dict]] = {}

        for friendly_name, table_spec in PRESENTATION_TABLES.items():
            # Parse the table spec: "DATAFLOW_ID::HIERARCHY_ID" or "DATAFLOW_ID::HIERARCHY_ID:SPLIT_CODE"
            parts = table_spec.split("::")
            if len(parts) != 2:
                continue

            dataflow_id = parts[0]
            table_id = parts[1]

            if dataflow_id not in self.dataflows:
                continue

            try:
                # Get all hierarchies for this dataflow
                all_hierarchies = self.get_dataflow_hierarchies(dataflow_id)
                if not all_hierarchies:
                    continue

                # Find the matching hierarchy
                matching_hierarchy = None
                for h in all_hierarchies:
                    if h.get("id") == table_id:
                        matching_hierarchy = h
                        break

                if matching_hierarchy:
                    # Add friendly_name to the hierarchy info
                    hierarchy_with_name = matching_hierarchy.copy()
                    hierarchy_with_name["friendly_name"] = friendly_name
                    hierarchy_with_name["dataflow_id"] = dataflow_id

                    if dataflow_id not in result:
                        result[dataflow_id] = []
                    result[dataflow_id].append(hierarchy_with_name)
            except Exception:  # noqa: S110  # pylint: disable=broad-exception-caught
                pass

        return result
