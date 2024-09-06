import json

from openbb_core.provider.utils.helpers import make_request

payload = json.dumps(
    {
        "first_name": None,
        "last_name": None,
        "submitted_start_date": "07/29/2024",
        "submitted_end_date": "07/31/2024",
    }
)


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://efdsearch.senate.gov/search/",
}

url = "https://efdsearch.senate.gov/search/"

response = make_request(url, data=payload, method="POST")

response.content
