"""OpenBB filters."""

from typing import Dict, Optional, Set

from openbb_core.app.utils import convert_to_basemodel
from openbb_core.provider.utils.validators import check_single_value


def filter_inputs(
    data_processing: bool = False,
    extra_info: Optional[Dict[str, Set[str]]] = None,
    **kwargs,
) -> dict:
    """Filter command inputs."""
    for key, value in kwargs.items():
        if data_processing and key == "data":
            kwargs[key] = convert_to_basemodel(value)

    if extra_info:
        PROPERTY = "multiple_items_allowed"
        provider = kwargs["provider_choices"]["provider"]

        for field, props in extra_info.items():
            if PROPERTY in props:
                for p in ("standard_params", "extra_params"):
                    if field in kwargs.get(p, {}):
                        current = kwargs[p][field]
                        new = (
                            ",".join(current) if isinstance(current, list) else current
                        )
                        if provider not in props[PROPERTY]:
                            check_single_value(
                                new, f"multiple values not allowed for '{provider}'"
                            )
                        kwargs[p][field] = new
                        break

    return kwargs
