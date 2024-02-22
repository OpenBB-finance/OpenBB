"""ECB Yield Curve Series IDs"""

from typing import Dict, Literal

RATING_DICT = {"aaa": "A", "all_ratings": "C"}

YIELD_TYPE_DICT = {
    "spot_rate": "SR",
    "instantaneous_forward": "IF",
    "par_yield": "PY",
}


def get_yield_curve_ids(
    rating: Literal["aaa", "all_ratings"] = "aaa",
    yield_curve_type: Literal[
        "spot_rate", "instantaneous_forward", "par_yield"
    ] = "spot_rate",
) -> Dict:
    """Get Yield Curve Series IDs"""

    YIELD_CURVE = {
        "month_3": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_3M",
        "month_6": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_6M",
        "year_1": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_1Y",
        "year_2": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_2Y",
        "year_3": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_3Y",
        "year_4": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_4Y",
        "year_5": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_5Y",
        "year_6": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_6Y",
        "year_7": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_7Y",
        "year_8": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_8Y",
        "year_9": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_9Y",
        "year_10": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_10Y",
        "year_11": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_11Y",
        "year_12": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_12Y",
        "year_13": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_13Y",
        "year_14": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_14Y",
        "year_15": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_15Y",
        "year_16": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_16Y",
        "year_17": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_17Y",
        "year_18": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_18Y",
        "year_19": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_19Y",
        "year_20": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_20Y",
        "year_21": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_21Y",
        "year_22": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_22Y",
        "year_23": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_23Y",
        "year_24": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_24Y",
        "year_25": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_25Y",
        "year_26": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_26Y",
        "year_27": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_27Y",
        "year_28": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_28Y",
        "year_29": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_29Y",
        "year_30": f"YC.B.U2.EUR.4F.G_N_{RATING_DICT[rating]}.SV_C_YM.{YIELD_TYPE_DICT[yield_curve_type]}_30Y",
    }

    MATURITY_VALUES = {
        "month_3": 0.25,
        "month_6": 0.5,
        "year_1": 1,
        "year_2": 2,
        "year_3": 3,
        "year_4": 4,
        "year_5": 5,
        "year_6": 6,
        "year_7": 7,
        "year_8": 8,
        "year_9": 9,
        "year_10": 10,
        "year_11": 11,
        "year_12": 12,
        "year_13": 13,
        "year_14": 14,
        "year_15": 15,
        "year_16": 16,
        "year_17": 17,
        "year_18": 18,
        "year_19": 19,
        "year_20": 20,
        "year_21": 21,
        "year_22": 22,
        "year_23": 23,
        "year_24": 24,
        "year_25": 25,
        "year_26": 26,
        "year_27": 27,
        "year_28": 28,
        "year_29": 29,
        "year_30": 30,
    }

    return dict(SERIES_IDS=YIELD_CURVE, MATURITIES=MATURITY_VALUES)
