"""ECB provider module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_ecb._installed import currency_key, economy_key, fixedincome_key
from openbb_ecb.models.available_indicators import ECBAvailableIndicatorsFetcher
from openbb_ecb.models.balance_of_payments import ECBBalanceOfPaymentsFetcher
from openbb_ecb.models.currency_historical import ECBCurrencyHistoricalFetcher
from openbb_ecb.models.currency_reference_rates import ECBCurrencyReferenceRatesFetcher
from openbb_ecb.models.ecb_interest_rates import ECBInterestRatesFetcher
from openbb_ecb.models.economic_calendar import ECBEconomicCalendarFetcher
from openbb_ecb.models.economic_indicators import ECBEconomicIndicatorsFetcher
from openbb_ecb.models.eligible_assets import ECBEligibleAssetsFetcher
from openbb_ecb.models.euro_short_term_rate import ECBEuroShortTermRateFetcher
from openbb_ecb.models.mfi_interest_rates import ECBMfiInterestRatesFetcher
from openbb_ecb.models.yield_curve import ECBYieldCurveFetcher

ecb_provider = Provider(
    name="ECB",
    website="https://data.ecb.europa.eu",
    description="""The ECB Data Portal provides access to all official ECB statistics
through the SDMX 2.1 REST API, plus euro reference exchange rates, key ECB interest
rates, the euro short-term rate (€STR), MFI/bank interest rates, the statistical
release calendar, ECB releases & publications, and the Eurosystem list of eligible
collateral assets.""",
    fetcher_dict={
        economy_key("AvailableIndicators", "AvailableEcbIndicators"): (
            ECBAvailableIndicatorsFetcher
        ),
        economy_key("EconomicIndicators", "EcbIndicators"): (
            ECBEconomicIndicatorsFetcher
        ),
        economy_key("BalanceOfPayments", "EcbBalanceOfPayments"): (
            ECBBalanceOfPaymentsFetcher
        ),
        economy_key("EconomicCalendar", "EcbReleaseCalendar"): (
            ECBEconomicCalendarFetcher
        ),
        currency_key("CurrencyHistorical", "EcbCurrencyHistorical"): (
            ECBCurrencyHistoricalFetcher
        ),
        currency_key("CurrencyReferenceRates", "EcbCurrencyReferenceRates"): (
            ECBCurrencyReferenceRatesFetcher
        ),
        fixedincome_key("YieldCurve", "EcbYieldCurve"): ECBYieldCurveFetcher,
        fixedincome_key("EuroShortTermRate", "EcbEuroShortTermRate"): (
            ECBEuroShortTermRateFetcher
        ),
        "EcbKeyInterestRates": ECBInterestRatesFetcher,
        "EcbMfiInterestRates": ECBMfiInterestRatesFetcher,
        "EcbEligibleAssets": ECBEligibleAssetsFetcher,
    },
    repr_name="European Central Bank (ECB)",
)
