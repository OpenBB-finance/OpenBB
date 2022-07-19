"""Economy helpers"""
__docformat__ = "numpy"


def update_stored_datasets_string(datasets) -> str:
    stored_datasets_string = ""
    for key in datasets:
        stored_datasets_string += (
            "\n" + " " * (len("Stored datasets") - len(key)) + key + ": "
        )
        for i, col in enumerate(datasets[key].columns):
            if i == 0:
                stored_datasets_string += col
            else:
                stored_datasets_string += ", " + col

    return stored_datasets_string
