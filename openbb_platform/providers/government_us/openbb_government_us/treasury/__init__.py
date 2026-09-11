"""US Treasury provider module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_government_us.treasury.models.auction_results import (
    TreasuryAuctionResultsFetcher,
)
from openbb_government_us.treasury.models.bill_offerings import (
    TreasuryBillOfferingsFetcher,
)
from openbb_government_us.treasury.models.daily_treasury_statement import (
    DailyTreasuryStatementFetcher,
)
from openbb_government_us.treasury.models.debt_to_penny import DebtToPennyFetcher
from openbb_government_us.treasury.models.treasury_auctions import (
    UsTreasuryAuctionsFetcher,
)
from openbb_government_us.treasury.models.treasury_bulletin import (
    TreasuryBulletinFetcher,
)
from openbb_government_us.treasury.models.treasury_prices import (
    UsTreasuryPricesFetcher,
)
from openbb_government_us.treasury.models.upcoming_auctions import (
    UpcomingTreasuryAuctionsFetcher,
)
from openbb_government_us.treasury.models.usaspending_award import (
    UsSpendingAwardFetcher,
)
from openbb_government_us.treasury.models.usaspending_award_search import (
    UsSpendingAwardSearchFetcher,
)
from openbb_government_us.treasury.models.usaspending_explorer import (
    UsSpendingExplorerFetcher,
)
from openbb_government_us.treasury.models.usaspending_recipient_awards import (
    UsSpendingRecipientAwardsFetcher,
)
from openbb_government_us.treasury.models.usaspending_recipient_search import (
    UsSpendingRecipientSearchFetcher,
)

FIXEDINCOME_INSTALLED = find_spec("openbb_fixedincome") is not None

us_treasury_provider = Provider(
    name="us_treasury",
    website="https://fiscaldata.treasury.gov",
    description="""Data published by the U.S. Department of the Treasury -
auction announcements and results from TreasuryDirect, plus FiscalData API
datasets covering the debt to the penny, the Daily Treasury Statement,
upcoming and historical marketable securities auctions, and the Treasury
Bulletin. All sources are public and keyless.""",
    fetcher_dict={
        "DailyTreasuryStatement": DailyTreasuryStatementFetcher,
        "DebtToPenny": DebtToPennyFetcher,
        "TreasuryAuctionResults": TreasuryAuctionResultsFetcher,
        "TreasuryAuctions": UsTreasuryAuctionsFetcher,
        "TreasuryBillOfferings": TreasuryBillOfferingsFetcher,
        "TreasuryBulletin": TreasuryBulletinFetcher,
        "TreasuryPrices": UsTreasuryPricesFetcher,
        "UpcomingTreasuryAuctions": UpcomingTreasuryAuctionsFetcher,
        "UsSpendingAward": UsSpendingAwardFetcher,
        "UsSpendingAwardSearch": UsSpendingAwardSearchFetcher,
        "UsSpendingExplorer": UsSpendingExplorerFetcher,
        "UsSpendingRecipientAwards": UsSpendingRecipientAwardsFetcher,
        "UsSpendingRecipientSearch": UsSpendingRecipientSearchFetcher,
    },
    repr_name="U.S. Department of the Treasury",
    instructions="""All endpoints use public, keyless data from TreasuryDirect
and the FiscalData API, so no credentials are required.""",
)
