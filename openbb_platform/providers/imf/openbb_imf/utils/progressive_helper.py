"""IMF Progressive Query Helper."""

# pylint: disable=W0212

from openbb_imf.utils.query_builder import ImfQueryBuilder


class ImfParamsBuilder:
    """A helper class to build IMF queries progressively by making sequential dimension selections,
    for each dimension of a dataflow, filtering the available options at each step based on previous selections.
    """

    def __init__(self, dataflow_id: str):
        """Initialize the ImfParamsBuilder object.

        Parameters
        ----------
        dataflow_id : str
            The ID of the dataflow to build a query for.
        """
        self._builder = ImfQueryBuilder()
        if dataflow_id not in self._builder.metadata.dataflows:
            raise KeyError(
                f"Dataflow '{dataflow_id}' not found."
                f" Available dataflows: {list(self._builder.metadata.dataflows.keys())}"
            )

        self.dataflow_id = dataflow_id
        self.dsd = self._get_dsd()
        self._dimensions = self._get_dimensions_in_order()
        self.current_dimension = self._dimensions[0] if self._dimensions else None
        self._selections: dict = {dim: None for dim in self._dimensions}
        self._last_constraints_response: dict = {}

    def _get_dsd(self):
        """Get the Data Structure Definition (DSD) for the current dataflow."""
        df_obj = self._builder.metadata.dataflows[self.dataflow_id]
        dsd_id = df_obj.get("structureRef", {}).get("id")
        return self._builder.metadata.datastructures.get(dsd_id, {})

    def _get_dimensions_in_order(self) -> list[str]:
        """Get the list of dimension IDs in their specified order."""
        dimensions_metadata = self.dsd.get("dimensions", [])

        # Sort by position if available, otherwise keep original order
        if dimensions_metadata and all(
            d.get("position") is not None for d in dimensions_metadata
        ):
            dimensions_metadata = sorted(
                dimensions_metadata, key=lambda x: int(x.get("position"))  # type: ignore
            )

        return [
            d["id"]
            for d in dimensions_metadata
            if d.get("id") and d.get("id") != "TIME_PERIOD"
        ]

    def get_next_dimension_to_select(self) -> str | None:
        """
        Get the ID of the next dimension that needs a selection.

        Returns
        -------
        str or None
            The ID of the next dimension, or None if all dimensions have been selected.
        """
        for dim in self._dimensions:
            if self._selections[dim] is None:
                return dim
        return None

    def get_options_for_dimension(
        self, dimension_id: str | None = None
    ) -> list[dict[str, str]]:
        """Get the available options for a given dimension, based on the current selections.

        Parameters
        ----------
        dimension_id : str
            The ID of the dimension to get options for.

        Returns
        -------
        list[dict]
            A list of available options, where each option is a dictionary with
            'label' and 'value' keys.
        """
        dimension_id = dimension_id or self.get_next_dimension_to_select()
        if not dimension_id:
            return []
        if dimension_id not in self._dimensions:
            raise ValueError(
                f"Dimension '{dimension_id}' not found for dataflow '{self.dataflow_id}'."
            )

        key_parts: list = []
        for dim in self._dimensions:
            if self._selections[dim] is not None:
                key_parts.append(self._selections[dim])
            else:
                # Use wildcard '*' for unselected dimensions instead of empty string
                # Empty string creates malformed URLs like '../'
                key_parts.append("*")
        key = ".".join(key_parts)

        constraints = self._builder.metadata.get_available_constraints(
            dataflow_id=self.dataflow_id,
            key=key,
            component_id=dimension_id,
        )
        # Store the last constraints response for time period validation
        self._last_constraints_response = constraints

        options: list[dict[str, str]] = []
        key_values = constraints.get("key_values", [])
        for kv in key_values:
            if kv.get("id") == dimension_id:
                codelist_map = self._get_codelist_for_dim(dimension_id)
                for value_id in kv.get("values", []):
                    options.append(
                        {
                            "label": codelist_map.get(value_id, value_id),
                            "value": value_id,
                        }
                    )
        return options

    def _get_codelist_for_dim(self, dimension_id: str) -> dict:
        """Get the codelist map for a given dimension."""
        df_obj = self._builder.metadata.dataflows[self.dataflow_id]
        agency_id = df_obj.get("agencyID")
        if not agency_id:
            return {}

        dimensions_metadata = {
            d["id"]: d for d in self.dsd.get("dimensions", []) if d.get("id")
        }
        dim_meta = dimensions_metadata.get(dimension_id)
        if not dim_meta:
            return {}

        dsd_id = self.dsd.get("id")
        codelist_id = self._builder.metadata._resolve_codelist_id(
            self.dataflow_id, dsd_id, dimension_id, dim_meta
        )

        if codelist_id:
            return self._builder.metadata._get_codelist_map(
                codelist_id, agency_id, self.dataflow_id
            )
        return {}

    def set_dimension(self, dimension: tuple[str, str]) -> dict:
        """Set a value for a dimension and clear downstream selections.

        Parameters
        ----------
        dimension : tuple
            A tuple of (dimension_id, value) to set.

        Returns
        -------
        dict
            The updated selections after setting the dimension.
        """
        if dimension[0] not in self._dimensions:
            raise KeyError(
                f"Dimension '{dimension[0]}' not valid for this dataflow."
                f" Valid dimensions: {list(self._selections.keys())}"
            )
        self._selections[dimension[0]] = dimension[1]
        # When a selection is made, we clear selections for downstream dimensions
        # as they might now be invalid.
        found_dim = False
        for dim in self._dimensions:
            if found_dim:
                self._selections[dim] = None
            if dim == dimension[0]:
                found_dim = True

        self.current_dimension = self.get_next_dimension_to_select()

        return self._selections.copy()

    def get_dimensions(self) -> dict[str, str | None]:
        """Get the current selections for the dimension_id.

        Returns
        -------
        dict
            A dictionary of the current dimension selections.
        """
        return self._selections.copy()

    def build_url(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> str:
        """
        Build the final API URL based on the current selections.

        Parameters
        ----------
        start_date : str, optional
            The start date for the data query.
        end_date : str, optional
            The end date for the data query.

        Returns
        -------
        str
            The constructed IMF API URL.
        """
        return self._builder.build_url(
            dataflow=self.dataflow_id,
            start_date=start_date,
            end_date=end_date,
            **self._selections,
        )

    def fetch(self, start_date: str | None = None, end_date: str | None = None) -> dict:
        """
        Build the URL and fetch the data based on the current selections.

        Parameters
        ----------
        start_date : str, optional
            The start date for the data query.
        end_date : str, optional
            The end date for the data query.

        Returns
        -------
        dict
            The fetched data and metadata.
        """
        return self._builder.fetch_data(
            dataflow=self.dataflow_id,
            start_date=start_date,
            end_date=end_date,
            **self._selections,
        )
