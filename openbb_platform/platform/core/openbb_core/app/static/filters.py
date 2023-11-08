"""OpenBB filters."""


from openbb_core.app.utils import convert_to_basemodel


def filter_inputs(data_processing: bool = False, **kwargs) -> dict:
    """Filter command inputs."""
    for key, value in kwargs.items():
        if data_processing and key == "data":
            kwargs[key] = convert_to_basemodel(value)

    return kwargs
