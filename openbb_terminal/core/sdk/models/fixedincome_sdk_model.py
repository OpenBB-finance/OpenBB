# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class FixedincomeRoot(Category):
    """Fixedincome Module

    Attributes:
        `ameribor`: Obtain data for American Interbank Offered Rate (AMERIBOR)\n
        `cp`: Obtain Commercial Paper data\n
        `dwpcr`: Obtain data for the Discount Window Primary Credit Rate.\n
        `ecb`: Obtain data for ECB interest rates.\n
        `ecbycrv`: Gets euro area yield curve data from ECB.\n
        `estr`: Obtain data for Euro Short-Term Rate (ESTR)\n
        `fed`: Obtain data for Effective Federal Funds Rate.\n
        `ffrmc`: Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate\n
        `hqm`: The HQM yield curve represents the high quality corporate bond market, i.e.,\n
        `icebofa`: Get data for ICE BofA US Corporate Bond Indices.\n
        `icespread`: Get data for ICE BofA US Corporate Bond Spreads\n
        `iorb`: Obtain data for Interest Rate on Reserve Balances.\n
        `moody`: Get data for Moody Corporate Bond Index\n
        `projection`: Obtain data for the Federal Reserve's projection of the federal funds rate.\n
        `sofr`: Obtain data for Secured Overnight Financing Rate (SOFR)\n
        `sonia`: Obtain data for Sterling Overnight Index Average (SONIA)\n
        `spot`: The spot rate for any maturity is the yield on a bond that provides\n
        `tbffr`: Get data for Selected Treasury Bill Minus Federal Funds Rate.\n
        `tmc`: Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.\n
        `treasury`: Gets interest rates data from selected countries (3 month and 10 year)\n
        `usrates`: Plot various treasury rates from the United States\n
        `ycrv`: Gets yield curve data from FRED.\n
        `ycrv_chart`: Display yield curve based on US Treasury rates for a specified date.\n
    """

    _location_path = "fixedincome"

    def __init__(self):
        super().__init__()
        self.ameribor = lib.fixedincome_fred_model.get_ameribor
        self.cp = lib.fixedincome_fred_model.get_cp
        self.dwpcr = lib.fixedincome_fred_model.get_dwpcr
        self.ecb = lib.fixedincome_fred_model.get_ecb
        self.ecbycrv = lib.fixedincome_ecb_model.get_ecb_yield_curve
        self.estr = lib.fixedincome_fred_model.get_estr
        self.fed = lib.fixedincome_fred_model.get_fed
        self.ffrmc = lib.fixedincome_fred_model.get_ffrmc
        self.hqm = lib.fixedincome_fred_model.get_hqm
        self.icebofa = lib.fixedincome_fred_model.get_icebofa
        self.icespread = lib.fixedincome_fred_model.get_icespread
        self.iorb = lib.fixedincome_fred_model.get_iorb
        self.moody = lib.fixedincome_fred_model.get_moody
        self.projection = lib.fixedincome_fred_model.get_projection
        self.sofr = lib.fixedincome_fred_model.get_sofr
        self.sonia = lib.fixedincome_fred_model.get_sonia
        self.spot = lib.fixedincome_fred_model.get_spot
        self.tbffr = lib.fixedincome_fred_model.get_tbffr
        self.tmc = lib.fixedincome_fred_model.get_tmc
        self.treasury = lib.fixedincome_oecd_model.get_treasury
        self.usrates = lib.fixedincome_fred_model.get_usrates
        self.ycrv = lib.fixedincome_fred_model.get_yield_curve
        self.ycrv_chart = lib.fixedincome_fred_view.display_yield_curve
