"""EconDB Yield Curve Utilities"""

from typing import Literal

DAILY = {
    "australia": {
        "RBA_F02D.FCMYGBAG2D.D.AU": "year_2",
        "RBA_F02D.FCMYGBAG3D.D.AU": "year_3",
        "RBA_F02D.FCMYGBAG5D.D.AU": "year_5",
        "RBA_F02D.FCMYGBAG10D.D.AU": "year_10",
    },
    "canada": {
        "BOC_MONEY_MARKET.TB_CDN_30D_MID.D.CA": "month_1",
        "BOC_MONEY_MARKET.TB_CDN_60D_MID.D.CA": "month_2",
        "BOC_MONEY_MARKET.TB_CDN_90D_MID.D.CA": "month_3",
        "BOC_MONEY_MARKET.TB_CDN_180D_MID.D.CA": "month_6",
        "BOC_MONEY_MARKET.TB_CDN_1Y_MID.D.CA": "year_1",
        "BOC_BOND_YIELDS_ALL.BD_CDN_2YR_DQ_YLD.D.CA": "year_2",
        "BOC_BOND_YIELDS_ALL.BD_CDN_3YR_DQ_YLD.D.CA": "year_3",
        "BOC_BOND_YIELDS_ALL.BD_CDN_5YR_DQ_YLD.D.CA": "year_5",
        "BOC_BOND_YIELDS_ALL.BD_CDN_7YR_DQ_YLD.D.CA": "year_7",
        "BOC_BOND_YIELDS_ALL.BD_CDN_10YR_DQ_YLD.D.CA": "year_10",
        "BOC_BOND_YIELDS_ALL.BD_CDN_LONG_DQ_YLD.D.CA": "long_term",
    },
    "china": {
        "CCDC_CGB.CHB_3M.D.CN": "month_3",
        "CCDC_CGB.CHB_6M.D.CN": "month_6",
        "CCDC_CGB.CHB_1Y.D.CN": "year_1",
        "CCDC_CGB.CHB_3Y.D.CN": "year_3",
        "CCDC_CGB.CHB_5Y.D.CN": "year_5",
        "CCDC_CGB.CHB_7Y.D.CN": "year_7",
        "CCDC_CGB.CHB_10Y.D.CN": "year_10",
        "CCDC_CGB.CHB_30Y.D.CN": "year_30",
    },
    "hong_kong": {
        "HK_YLD.Y2YD.D.HK": "year_2",
        "HK_YLD.Y3YD.D.HK": "year_3",
        "HK_YLD.Y5YD.D.HK": "year_5",
        "HK_YLD.Y10YD.D.HK": "year_10",
        "HK_YLD.Y15YD.D.HK": "year_15",
        "HK_YLD.Y20YD.D.HK": "year_20",
    },
    "india": {
        "RBI_RATES.M3.D.IN": "month_3",
        "RBI_RATES.M6.D.IN": "month_6",
        "RBI_RATES.Y1.D.IN": "year_1",
        "RBI_RATES.Y10.D.IN": "year_10",
    },
    "japan": {
        "MFJP_IR.1Y.D.JP": "year_1",
        "MFJP_IR.2Y.D.JP": "year_2",
        "MFJP_IR.3Y.D.JP": "year_3",
        "MFJP_IR.4Y.D.JP": "year_4",
        "MFJP_IR.5Y.D.JP": "year_5",
        "MFJP_IR.6Y.D.JP": "year_6",
        "MFJP_IR.7Y.D.JP": "year_7",
        "MFJP_IR.8Y.D.JP": "year_8",
        "MFJP_IR.9Y.D.JP": "year_9",
        "MFJP_IR.10Y.D.JP": "year_10",
        "MFJP_IR.15Y.D.JP": "year_15",
        "MFJP_IR.20Y.D.JP": "year_20",
        "MFJP_IR.25Y.D.JP": "year_25",
        "MFJP_IR.30Y.D.JP": "year_30",
        "MFJP_IR.40Y.D.JP": "year_40",
    },
    "russia": {
        "CBR_BONDS.M3YD.D.RU": "month_3",
        "CBR_BONDS.M6YD.D.RU": "month_6",
        "CBR_BONDS.M9YD.D.RU": "month_9",
        "CBR_BONDS.Y1YD.D.RU": "year_1",
        "CBR_BONDS.Y2YD.D.RU": "year_2",
        "CBR_BONDS.Y3YD.D.RU": "year_3",
        "CBR_BONDS.Y5YD.D.RU": "year_5",
        "CBR_BONDS.Y7YD.D.RU": "year_7",
        "CBR_BONDS.Y10YD.D.RU": "year_10",
        "CBR_BONDS.Y15YD.D.RU": "year_15",
        "CBR_BONDS.Y20YD.D.RU": "year_20",
        "CBR_BONDS.Y30YD.D.RU": "year_30",
    },
    "saudi_arabia": {
        "EXSA_YLD.Y1.D.SA": "year_1",
        "EXSA_YLD.Y2.D.SA": "year_2",
        "EXSA_YLD.Y3.D.SA": "year_3",
        "EXSA_YLD.Y5.D.SA": "year_5",
        "EXSA_YLD.Y10.D.SA": "year_10",
        "EXSA_YLD.Y15.D.SA": "year_15",
    },
    "south_africa": {
        "RBZA_YLD.M3YD.D.ZA": "month_3",
        "RBZA_YLD.Y10YD.D.ZA": "year_10",
    },
    "south_korea": {
        "BOK_IR.KORIBOR_3M.D.KR": "month_3",
        "BOK_IR.KORIBOR_6M.D.KR": "month_6",
        "BOK_IR.TB1Y.D.KR": "year_1",
        "BOK_IR.TB2Y.D.KR": "year_2",
        "BOK_IR.TB3Y.D.KR": "year_3",
        "BOK_IR.TB5Y.D.KR": "year_5",
        "BOK_IR.TB10Y.D.KR": "year_10",
        "BOK_IR.TB20Y.D.KR": "year_20",
        "BOK_IR.TB30Y.D.KR": "year_30",
        "BOK_IR.TB50Y.D.KR": "year_50",
    },
    "taiwan": {
        "TWSE_YLD.2.D.TW": "year_2",
        "TWSE_YLD.5.D.TW": "year_5",
        "TWSE_YLD.10.D.TW": "year_10",
        "TWSE_YLD.20.D.TW": "year_20",
        "TWSE_YLD.30.D.TW": "year_30",
    },
    "united_kingdom": {
        "BOE_YLD.6M.D.UK": "month_6",
        "BOE_YLD.9M.D.UK": "month_9",
        "BOE_YLD.1Y.D.UK": "year_1",
        "BOE_YLD.2Y.D.UK": "year_2",
        "BOE_YLD.3Y.D.UK": "year_3",
        "BOE_YLD.5Y.D.UK": "year_5",
        "BOE_YLD.7Y.D.UK": "year_7",
        "BOE_YLD.10Y.D.UK": "year_10",
        "BOE_YLD.15Y.D.UK": "year_15",
        "BOE_YLD.20Y.D.UK": "year_20",
        "BOE_YLD.30Y.D.UK": "year_30",
    },
    "united_states": {
        "FRB_H15.45E95.D.US": "month_1",
        "FRB_H15.FE7E7.D.US": "month_3",
        "FRB_H15.29909.D.US": "month_6",
        "FRB_H15.C6F60.D.US": "year_1",
        "FRB_H15.B0E4B.D.US": "year_2",
        "FRB_H15.B279A.D.US": "year_3",
        "FRB_H15.3E1BD.D.US": "year_5",
        "FRB_H15.D7F32.D.US": "year_7",
        "FRB_H15.37BF6.D.US": "year_10",
        "FRB_H15.C279E.D.US": "year_20",
        "FRB_H15.F5280.D.US": "year_30",
    },
}

DAILY_COUNTRIES = list(DAILY.keys())

COUNTRIES = Literal[",".join(DAILY_COUNTRIES)]


HK = "https://www.hkgb.gov.hk/en/others/documents/DailyClosings.xls"
HK_HISTORICAL_DAILY = "https://www.hkgb.gov.hk/en/others/documents/T090403.xls"


def duration_sorter(durations: list) -> list:
    """Sort durations labeled as month_5, year_5, etc."""

    def duration_to_months(duration):
        """Convert duration to months."""
        if duration == "long_term":
            return 360
        parts = duration.split("_")
        months = 0
        for i in range(0, len(parts), 2):
            number = int(parts[i + 1])
            if parts[i] == "year":
                number *= 12  # Convert years to months
            months += number
        return months

    return sorted(durations, key=duration_to_months)
