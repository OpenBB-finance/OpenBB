import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(r"openbb_platform\extensions\quant_ml"))

from openbb_quant_ml.service.macro_domain import get_macro_series
from openbb_quant_ml.service.macro_transforms import apply_transform

for k in ["INDPRO", "PAYEMS", "RSAFS"]:
    try:
        s = get_macro_series(k, date(2023,1,1), date.today(), "M")
        if s.empty:
            print(f"{k} is EMPTY")
            continue
        z = apply_transform(s, "yoy_zscore")
        print(f"{k} raw shape: {s.shape}, yoy_zscore valid shape: {z.dropna().shape}")
        if not z.dropna().empty:
            print(f"{k} last zscore: {z.dropna().iloc[-1]}")
    except Exception as e:
        print(f"{k} Error: {e}")
