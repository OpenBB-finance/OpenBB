from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import random
def get_cramer_picks(lookback=3):
    baseUrl = 'https://www.quiverquant.com/cramertracker/'

    req = requests.get(baseUrl, headers={'User-Agent': get_user_agent()})
    soup = BeautifulSoup(req.text, "html.parser")

    table = soup.find_all('div', {"class": "holdings-table table-inner"})[0]

    holder = []

    for row in table.find_all('tr'):
        tds = row.find_all('td')
        if not tds:
            continue
        else:
            ticker  = tds[0].text
            direction = tds[1].text
            cob = datetime.strptime(tds[2].text, '%B %d, %Y').date()

            if (date.today() - cob).days > lookback:
                continue
            else:
                holder.append(dict(ticker=ticker, recommendation=direction, as_of_date=cob))
    return holder

def get_user_agent():
    uastrings = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0", \
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko", \
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36" \
        ]

    return random.choice(uastrings)

