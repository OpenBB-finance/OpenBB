"""Economy helpers"""
__docformat__ = "numpy"


def update_stored_datasets_string(datasets) -> str:
    stored_datasets_string = ""
    for key in datasets:
        for col in datasets[key].columns:
            stored_datasets_string += f"\n  {key}    : {col}"

    return stored_datasets_string
