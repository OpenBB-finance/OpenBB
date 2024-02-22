"""OpenBB filters."""

from typing import Dict, List, Optional

from openbb_core.app.utils import check_single_item, convert_to_basemodel


def filter_inputs(
    data_processing: bool = False,
    extra_info: Optional[Dict[str, Dict[str, List[str]]]] = None,
    **kwargs,
) -> dict:
    """Filter command inputs."""
    for key, value in kwargs.items():
        if data_processing and key == "data":
            kwargs[key] = convert_to_basemodel(value)

    if extra_info:
        PROPERTY = "multiple_items_allowed"

        # Here we check if list items are passed and multiple items allowed for
        # the given provider/input combination. In that case we transform the list
        # into a comma-separated string
        for field, props in extra_info.items():
            if PROPERTY in props and (
                provider := kwargs.get("provider_choices", {}).get("provider")
            ):
                for p in ("standard_params", "extra_params"):
                    if field in kwargs.get(p, {}):
                        current = kwargs[p][field]
                        new = (
                            ",".join(current) if isinstance(current, list) else current
                        )

                        if provider and provider not in props[PROPERTY]:
                            check_single_item(
                                new,
                                f"{field} -> multiple items not allowed for '{provider}'",
                            )

                        kwargs[p][field] = new
                        break

    return kwargs
