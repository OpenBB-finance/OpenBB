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
    /economy
    /equity
    /etf
    /fixedincome
    /index
    /news
    /regulators

Extensions:
    - commodity@1.0.0
    - crypto@1.1.1
    - currency@1.1.1
    - derivatives@1.1.1
    - economy@1.1.1
    - equity@1.1.1
    - etf@1.1.1
    - fixedincome@1.1.1
    - index@1.1.1
    - news@1.1.1
    - regulators@1.1.1

    - benzinga@1.1.1
    - federal_reserve@1.1.1
    - fmp@1.1.1
    - fred@1.1.1
    - intrinio@1.1.1
    - oecd@1.1.1
    - polygon@1.1.1
    - sec@1.1.1
    - tiingo@1.1.1
    - tradingeconomics@1.1.1
    - yfinance@1.1.1    """
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
    def currency(self):
        # pylint: disable=import-outside-toplevel
        from . import currency

        return currency.ROUTER_currency(command_runner=self._command_runner)

    @property
    def derivatives(self):
        # pylint: disable=import-outside-toplevel
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
    def equity(self):
        # pylint: disable=import-outside-toplevel
        from . import equity

        return equity.ROUTER_equity(command_runner=self._command_runner)

    @property
    def etf(self):
        # pylint: disable=import-outside-toplevel
        from . import etf

        return etf.ROUTER_etf(command_runner=self._command_runner)

    @property
    def fixedincome(self):
        # pylint: disable=import-outside-toplevel
        from . import fixedincome

        return fixedincome.ROUTER_fixedincome(command_runner=self._command_runner)

    @property
    def index(self):
        # pylint: disable=import-outside-toplevel
        from . import index

        return index.ROUTER_index(command_runner=self._command_runner)

    @property
    def news(self):
        # pylint: disable=import-outside-toplevel
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
