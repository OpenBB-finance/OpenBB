"""OpenBB 过滤器。"""

from typing import Any

from openbb_core.app.utils import check_single_item, convert_to_basemodel


def filter_inputs(
    data_processing: bool = False,
    info: dict[str, dict[str, Any]] | None = None,
    **kwargs,
) -> dict:
    """过滤命令输入。"""
    for key, value in kwargs.items():
        if data_processing and key == "data":
            kwargs[key] = convert_to_basemodel(value)

    if info:
        # 这里我们检查是否通过了列表项以及对于给定的
        # 提供者/输入组合是否允许多个项目。在这种情况下，我们将列表转换
        # 为逗号分割的字符串
        provider = kwargs.get("provider_choices", {}).get("provider")
        for field, properties in info.items():
            for p in ("standard_params", "extra_params"):
                if field in kwargs.get(p, {}):
                    current = kwargs[p][field]
                    new = (
                        ",".join(map(str, current))
                        if isinstance(current, list)
                        else current
                    )

                    provider_properties = properties.get(provider, {})
                    if isinstance(provider_properties, dict):
                        multiple_items_allowed = provider_properties.get(
                            "multiple_items_allowed"
                        )
                    elif isinstance(provider_properties, list):
                        # 为了向后兼容，以前这是一个列表
                        multiple_items_allowed = (
                            "multiple_items_allowed" in provider_properties
                        )
                    else:
                        multiple_items_allowed = True

                    if not multiple_items_allowed:
                        check_single_item(
                            new,
                            f"{field} -> '{provider}' 不允许多个项目",
                        )

                    kwargs[p][field] = new
                    break
    else:
        provider = kwargs.get("provider_choices", {}).get("provider")
        for param_category in ("standard_params", "extra_params"):
            if param_category in kwargs:
                for field, value in kwargs[param_category].items():
                    if isinstance(value, list):
                        kwargs[param_category][field] = ",".join(map(str, value))
                    check_single_item(
                        kwargs[param_category][field],
                        f"{field} -> '{provider}' 不允许多个项目",
                    )

    return kwargs
