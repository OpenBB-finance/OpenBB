# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class FixedincomeRoot(Category):
    """Fixedincome Module

    Attributes:
        `ecbycrv`: Gets euro area yield curve data from ECB.\n
        `ycrv`: Gets yield curve data from FRED.\n
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
