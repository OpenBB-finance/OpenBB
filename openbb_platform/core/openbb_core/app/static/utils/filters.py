"""OpenBB filters."""

from typing import Dict, List, Optional

from openbb_core.app.utils import check_single_value, convert_to_basemodel


def filter_inputs(
    data_processing: bool = False,
    extra_info: Optional[Dict[str, List[str]]] = None,
    **kwargs,
) -> dict:
    """Filter command inputs."""
    for key, value in kwargs.items():
        if data_processing and key == "data":
            kwargs[key] = convert_to_basemodel(value)

    if extra_info:
        PROPERTY = "multiple_items_allowed"

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
                            check_single_value(
                                new, f"multiple values not allowed for '{provider}'"
                            )

                        kwargs[p][field] = new
                        break

    return kwargs
