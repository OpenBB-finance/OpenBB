# OpenBB Cramer

This provider fetches Jim Cramer's stock picks.

At the moment it scrapers a website where JC picks are published daily.
In the near future i have been promised an RSS Endpoint which will provide the same information.

Provider can be exercised with the following python code

>>from openbb_cramer.utils.helpers import get_cramer
>>get_cramer()()


Out[3]: 
[[CramerData(ticker=VST, as_of_date=2024-05-30, recommendation=Bullish),
  CramerData(ticker=SNOW, as_of_date=2024-05-30, recommendation=Bearish),
  CramerData(ticker=DIS, as_of_date=2024-05-29, recommendation=Bullish),
  CramerData(ticker=SHOP, as_of_date=2024-05-29, recommendation=Hold),
  CramerData(ticker=META, as_of_date=2024-05-29, recommendation=Long),
  CramerData(ticker=CCI, as_of_date=2024-05-29, recommendation=Bearish),
  CramerData(ticker=NVDA , as_of_date=2024-05-29, recommendation=Bullish),
  CramerData(ticker=TGNA, as_of_date=2024-05-28, recommendation=Bearish),
  CramerData(ticker=BX, as_of_date=2024-05-28, recommendation=Hold),
  CramerData(ticker=BLDR, as_of_date=2024-05-28, recommendation=Buy on a Pullback),
  CramerData(ticker=TROW, as_of_date=2024-05-28, recommendation=Bullish)