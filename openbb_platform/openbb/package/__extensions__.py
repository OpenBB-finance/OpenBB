### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from openbb_core.app.static.container import Container


class Extensions(Container):
    # fmt: off
    """
Routers:
    /commodity
    /crypto
    /currency
    /derivatives
    /econometrics
    /economy
    /equity
    /etf
    /fixedincome
    /index
    /news
    /quantitative
    /regulators
    /technical

Extensions:
    - commodity@1.0.0
    - crypto@1.0.0
    - currency@1.0.0
    - derivatives@1.0.0
    - econometrics@1.0.0
    - economy@1.0.0
    - equity@1.0.0
    - etf@1.0.0
    - fixedincome@1.0.0
    - index@1.0.0
    - news@1.0.0
    - openbb_charting@1.0.0
    - quantitative@1.0.0
    - regulators@1.0.0
    - technical@1.0.0

    - alpha_vantage@1.0.0
    - benzinga@1.0.0
    - biztoc@1.0.0
    - cboe@1.0.0
    - ecb@1.0.0
    - finra@1.0.0
    - fmp@1.0.0
    - fred@1.0.0
    - government_us@1.0.0
    - intrinio@1.0.0
    - nasdaq@1.0.0
    - oecd@1.0.0
    - polygon@1.0.0
    - sec@1.0.0
    - seeking_alpha@1.0.0
    - stockgrid@1.0.0
    - tiingo@1.0.0
    - tradingeconomics@1.0.0
    - ultima@1.0.0b0
    - wsj@1.0.0
    - yfinance@1.0.0    """
    # fmt: on
    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def commodity(self):  # route = "/commodity"
        from . import commodity

        return commodity.ROUTER_commodity(command_runner=self._command_runner)

    @property
    def crypto(self):  # route = "/crypto"
        from . import crypto

        return crypto.ROUTER_crypto(command_runner=self._command_runner)

    @property
    def currency(self):  # route = "/currency"
        from . import currency

        return currency.ROUTER_currency(command_runner=self._command_runner)

    @property
    def derivatives(self):  # route = "/derivatives"
        from . import derivatives

        return derivatives.ROUTER_derivatives(command_runner=self._command_runner)

    @property
    def econometrics(self):  # route = "/econometrics"
        from . import econometrics

        return econometrics.ROUTER_econometrics(command_runner=self._command_runner)

    @property
    def economy(self):  # route = "/economy"
        from . import economy

        return economy.ROUTER_economy(command_runner=self._command_runner)

    @property
    def equity(self):  # route = "/equity"
        from . import equity

        return equity.ROUTER_equity(command_runner=self._command_runner)

    @property
    def etf(self):  # route = "/etf"
        from . import etf

        return etf.ROUTER_etf(command_runner=self._command_runner)

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from . import fixedincome

        return fixedincome.ROUTER_fixedincome(command_runner=self._command_runner)

    @property
    def index(self):  # route = "/index"
        from . import index

        return index.ROUTER_index(command_runner=self._command_runner)

    @property
    def news(self):  # route = "/news"
        from . import news

        return news.ROUTER_news(command_runner=self._command_runner)

    @property
    def quantitative(self):  # route = "/quantitative"
        from . import quantitative

        return quantitative.ROUTER_quantitative(command_runner=self._command_runner)

    @property
    def regulators(self):  # route = "/regulators"
        from . import regulators

        return regulators.ROUTER_regulators(command_runner=self._command_runner)

    @property
    def technical(self):  # route = "/technical"
        from . import technical

        return technical.ROUTER_technical(command_runner=self._command_runner)
