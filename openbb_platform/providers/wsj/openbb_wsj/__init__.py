"""WSJ provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_wsj.models.active import WSJActiveFetcher
from openbb_wsj.models.gainers import WSJGainersFetcher
from openbb_wsj.models.losers import WSJLosersFetcher

wsj_provider = Provider(
    name="wsj",
    website="www.wsj.com",
    description="""WSJ (Wall Street Journal) is a business-focused, English-language
    international daily newspaper based in New York City. The Journal is published six
    days a week by Dow Jones & Company, a division of News Corp, along with its Asian
    and European editions. The newspaper is published in the broadsheet format and
    online. The Journal has been printed continuously since its inception on
    July 8, 1889, by Charles Dow, Edward Jones, and Charles Bergstresser.
    The WSJ is the largest newspaper in the United States, by circulation.
    """,
    fetcher_dict={
        "ETFGainers": WSJGainersFetcher,
        "ETFLosers": WSJLosersFetcher,
        "ETFActive": WSJActiveFetcher,
    },
)
