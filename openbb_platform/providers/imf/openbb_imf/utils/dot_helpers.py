"""Direction Of Trade Utilities."""

# pylint: disable=R0917,R0913,R0914,R0801


def load_country_choices() -> list[dict[str, str]]:
    """Load IMF IRFCL country map."""
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.metadata import ImfMetadata

    data = ImfMetadata().get_dataflow_parameters("IMTS")["COUNTRY"]
    countries_list: list = []
    g_regions: list = []
    tx_groups: list = []

    for item in data:
        if item["value"].startswith("G") and (
            item["value"][1:].isdigit()
            or (item["value"][1] == "X" and item["value"][2:].isdigit())
        ):
            g_regions.append(item)
        elif item["value"].startswith("TX"):
            tx_groups.append(item)
        else:
            countries_list.append(item)

    # Sort each group alphabetically by label
    countries_sorted = sorted(countries_list, key=lambda x: x["label"])
    g_regions_sorted = sorted(g_regions, key=lambda x: x["label"])
    tx_groups_sorted = sorted(tx_groups, key=lambda x: x["label"])

    return countries_sorted + g_regions_sorted + tx_groups_sorted


def list_country_choices() -> list[str]:
    """List IMF IRFCL country choices."""
    countries = load_country_choices()
    return [item["value"] for item in countries]


def get_label_to_code_map() -> dict[str, str]:
    """Get a mapping from normalized labels to country codes.

    Normalizes labels to lower_snake_case for flexible matching.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.helpers import normalize_country_label

    countries = load_country_choices()
    return {normalize_country_label(item["label"]): item["value"] for item in countries}


def get_code_to_label_map() -> dict[str, str]:
    """Get a mapping from country codes to normalized labels."""
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.helpers import normalize_country_label

    countries = load_country_choices()
    return {item["value"]: normalize_country_label(item["label"]) for item in countries}


def resolve_country_input(value: str) -> str:
    """Resolve a country input to its ISO code.

    Accepts both ISO3 codes (e.g., 'USA') and snake_case country names
    (e.g., 'united_states'). Returns the ISO code.

    Parameters
    ----------
    value : str
        Country code or name to resolve.

    Returns
    -------
    str
        The resolved ISO country code.

    Raises
    ------
    ValueError
        If the input cannot be resolved to a valid country code.
    """
    if not value:
        raise ValueError("Country value cannot be empty.")

    # Handle wildcards
    if value.lower() in ["all", "*"]:
        return "*"

    # Common aliases for frequently used regions
    common_aliases = {
        "world": "G001",
        "euro_area": "G163",
        "eurozone": "G163",
        "eu": "G998",
        "european_union": "G998",
        "europe": "GX170",
    }

    v_lower = value.lower().replace(" ", "_")

    # Check common aliases first
    if v_lower in common_aliases:
        return common_aliases[v_lower]

    code_set = set(list_country_choices())
    label_to_code = get_label_to_code_map()

    v_upper = value.upper()

    # Check if it's a valid ISO code
    if v_upper in code_set:
        return v_upper

    # Check if it's a valid snake_case country name
    if v_lower in label_to_code:
        return label_to_code[v_lower]

    # Not found - raise error with helpful message
    raise ValueError(
        f"Country '{value}' is not a valid IMF country code or country name. "
        f"Use ISO3 codes (e.g., 'USA', 'DEU') or snake_case names (e.g., 'united_states', 'germany')."
    )


def imts_query(
    country: str | list[str],
    counterpart: str | list[str],
    indicator: str | list[str],
    freq: str = "A",
    start_date: str | None = None,
    end_date: str | None = None,
    **kwargs,
) -> dict:
    """Query the Direction of Trade (IMTS) dataset.
    This function handles input validation for countries and counterparts.

    Parameters
    ----------
    country : str | list[str]
        The country or countries to fetch data for.
    counterpart : str | list[str]
        The counterpart country or countries. Use "*" for all.
    indicator : str | list[str]
        The indicator or indicators to fetch. Use "*" for all.
    freq : str | None
        The frequency of the data, by default "A" (annual).
    start_date : str | None
        The start date of the data, by default None.
    end_date : str | None
        The end date of the data, by default None.
    **kwargs : dict
        Additional query parameters to pass to the API.

    Returns
    -------
    dict
        A dictionary with keys: 'data' containing the fetched data,
        and 'metadata' containing the related metadata.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.query_builder import ImfQueryBuilder

    if not country or not counterpart:
        raise ValueError("Country and counterpart parameters cannot be empty.")

    freq = freq[0].upper()

    if freq and freq not in ["A", "Q", "M"]:
        raise ValueError("Frequency must be one of 'A', 'Q', or 'M'.")

    query_builder = ImfQueryBuilder()
    dataflow_id = "IMTS"
    params = query_builder.metadata.get_dataflow_parameters(dataflow_id)
    country_values = {item["value"] for item in params.get("COUNTRY", [])}
    counterpart_values = {
        item["value"]
        for item in params.get("COUNTERPART_COUNTRY", params.get("COUNTRY", []))
    }

    def _validate_selection(selection, valid_values, name):
        """Validate country or counterpart selection."""
        if not valid_values:
            return selection

        # Handle wildcards - return "*" as-is
        if selection == "*":
            return "*"

        # Parse the selection into a list
        if isinstance(selection, str):
            # Check if it contains commas (comma-separated list)
            selection_list = (
                [item.strip() for item in selection.split(",")]
                if "," in selection
                else [selection]
            )
        else:
            selection_list = selection

        # Check if any item is a wildcard
        if "*" in selection_list:
            return "*"

        invalid = [item for item in selection_list if item not in valid_values]
        if invalid:
            raise ValueError(f"Invalid {name}(s): {', '.join(invalid)}")
        return selection_list if len(selection_list) > 1 else selection_list[0]

    validated_country = _validate_selection(country, country_values, "country")
    validated_counterpart = _validate_selection(
        counterpart, counterpart_values, "counterpart"
    )

    # For indicator, handle wildcards and comma-separated values the same way
    if isinstance(indicator, str) and "," in indicator:
        validated_indicator = [item.strip() for item in indicator.split(",")]
    else:
        validated_indicator = indicator if indicator != "*" else "*"  # type: ignore

    return query_builder.fetch_data(
        dataflow=dataflow_id,
        start_date=start_date,
        end_date=end_date,
        FREQUENCY=freq,
        COUNTRY=validated_country,
        COUNTERPART_COUNTRY=validated_counterpart,
        INDICATOR=validated_indicator,
        **kwargs,
    )
