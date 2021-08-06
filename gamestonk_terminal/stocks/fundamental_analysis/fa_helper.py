import pandas as pd


def clean_df_index(df: pd.DataFrame):
    df.index = [
        "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
        for idx in df.index.tolist()
    ]
    df.index = [s_val.capitalize() for s_val in df.index]
