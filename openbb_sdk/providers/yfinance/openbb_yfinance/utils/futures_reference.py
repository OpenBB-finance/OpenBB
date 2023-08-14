from pathlib import Path

import pandas as pd

MONTHS = {
    1: "F",
    2: "G",
    3: "H",
    4: "J",
    5: "K",
    6: "M",
    7: "N",
    8: "Q",
    9: "U",
    10: "V",
    11: "X",
    12: "Z",
}

futures_data = pd.read_csv(Path(__file__).resolve().parent / "futures.csv")
