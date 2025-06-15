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
    /government
    /index
    /news
    /regulators

Extensions:
    - commodity@1.3.1
    - crypto@1.4.1
    - currency@1.4.1
    - derivatives@1.4.1
    - economy@1.4.2
    - equity@1.4.1
    - etf@1.4.1
    - fixedincome@1.4.3
    - government@1.4.2
    - index@1.4.1
    - news@1.4.1
    - regulators@1.4.2

    - benzinga@1.4.1
    - bls@1.1.2
    - cftc@1.1.1
    - congress_gov@1.0.0
    - econdb@1.3.1
    - federal_reserve@1.4.3
    - fmp@1.4.2
    - fred@1.4.4
    - imf@1.1.1
    - intrinio@1.4.1
    - oecd@1.4.1
    - polygon@1.4.1
    - sec@1.4.3
    - tiingo@1.4.1
    - tradingeconomics@1.4.1
    - us_eia@1.1.1
    - yfinance@1.4.6    """
    # fmt: on

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def commodity(self):
        # pylint: disable=import-outside-toplevel
        from . import commodity

        return commodity.ROUTER_commodity(command_runner=self._command_runner)

    @property
    def crypto(self):
        # pylint: disable=import-outside-toplevel
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
    def economy(self):
        # pylint: disable=import-outside-toplevel
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
    def government(self):
        # pylint: disable=import-outside-toplevel
        from . import government

        return government.ROUTER_government(command_runner=self._command_runner)

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
    def regulators(self):
        # pylint: disable=import-outside-toplevel
        from . import regulators

        return regulators.ROUTER_regulators(command_runner=self._command_runner)
