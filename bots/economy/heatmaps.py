import io
import logging
import time

import bs4
import requests
import undetected_chromedriver.v2 as uc
from PIL import Image
from selenium.webdriver.common.by import By

from bots import imps
from bots.helpers import uuid_get
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent

# pylint:disable=no-member

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def heatmaps_command(maps: str = "sec", timeline: str = ""):
    """Display Heatmaps [Finviz]"""

    # Debug
    if imps.DEBUG:
        logger.debug("heatmaps")

    maps_dict = {
        "S&P 500 Map": "sec",
        "Stock Market Map": "sec_all",
        "World Map": "geo",
        "ETF Map - Exchange Traded Funds Map": "etf",
    }
    url = f"https://finviz.com/map.ashx?t={maps_dict[maps]}"
    url += f"&st={timeline}" if timeline else ""
    options = uc.ChromeOptions()

    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--incognito")
    driver = uc.Chrome(options=options, version_main=100)
    driver.set_window_size(1920, 1080)
    driver.get(url)

    time.sleep(0.5)
    driver.find_element(By.XPATH, "//div[@id='root']/div/div[3]/button[2]/div").click()
    time.sleep(0.5)
    soup5 = bs4.BeautifulSoup(driver.page_source, "html.parser")
    images = soup5.findAll("img", alt=f"{maps}")

    img_scr = []
    for image in images:
        img_scr.append(image["src"])

    driver.quit()
    r = requests.get(
        f'{"".join(img_scr)}',
        stream=True,
        headers={"User-Agent": get_user_agent()},
        timeout=5,
    )
    r.raise_for_status()
    r.raw.decode_content = True

    dataBytesIO = io.BytesIO(r.content)
    im = Image.open(dataBytesIO)

    imagefile = f"heat_map_{uuid_get()}.png"
    filesave = imps.IMG_DIR.joinpath(imagefile)

    im.save(filesave, "PNG", quality=100)
    im.close()

    return {
        "title": f"Stocks: [Finviz] {maps.replace('Map', 'Heatmap')}",
        "imagefile": imagefile,
    }
