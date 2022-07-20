"""Economy helpers"""
__docformat__ = "numpy"


def update_stored_datasets_string(datasets) -> str:
    stored_datasets_string = ""
    for key in datasets:
        # ensure that column name is not empty
        if not datasets[key].columns.empty:
            # update string
            for i, col in enumerate(datasets[key].columns):
                if i == 0:
                    stored_datasets_string += (
                        "\n"
                        + " " * 2
                        + key
                        + " " * (len("Stored datasets") - len(key) - 2)
                        + ": "
                    )
                    stored_datasets_string += col
                else:
                    stored_datasets_string += ", " + col

    return stored_datasets_string
