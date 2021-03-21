""" thought_of_the_day.py tests """
import unittest

from bs4 import BeautifulSoup

from gamestonk_terminal import thought_of_the_day

import mock

mock_goodreads_page = """
<html>
<body>
<div class="quotes">
<h2>Epicurus quotes   <span class="smallText">
Showing 1-30 of 171
</span>
</h2>
  	  <div class='quote'>
<div class='quoteDetails'>

<div class="quoteText">
      &ldquo;Do not spoil what you have&rdquo;
  <br>  &#8213;
  <span class="authorOrTitle">
    Epicurus
  </span>
</div>


<div class="quoteFooter">
   <div class="greyText smallText left">
     tags:
       <a href="/quotes/tag/desire">desire</a>,
       <a href="/quotes/tag/gratitude">gratitude</a>,
       <a href="/quotes/tag/hope">hope</a>
   </div>
   <div class="right">
     <a class="smallText" title="View this quote" href="/quotes/169009-do-not-spoil-what-you-have-by-desiring-what-you">2582 likes</a>
   </div>
</div>

</div>
<div class='action'>
<a class="gr-button gr-button--small" rel="nofollow" href="/user/new">Like</a>
</div>
</div>
<div style="text-align: right; width: 100%">
<div><span class="previous_page disabled">« previous</span> <em class="current">1</em> <a rel="next" href="/author/quotes/114041.Epicurus?page=2">2</a> <a href="/author/quotes/114041.Epicurus?page=3">3</a> <a href="/author/quotes/114041.Epicurus?page=4">4</a> <a href="/author/quotes/114041.Epicurus?page=5">5</a> <a href="/author/quotes/114041.Epicurus?page=6">6</a> <a class="next_page" rel="next" href="/author/quotes/114041.Epicurus?page=2">next »</a></div>
</div>
</body>
</html>
"""


class TestThoughtOfTheDay(unittest.TestCase):
    def test_get_urls(self):
        urls = {"some author": "https://www.goodreads.com/author/quotes/someauthor"}

        a_totd = thought_of_the_day.ThoughtOfTheDay(urls)

        self.assertEqual(a_totd.get_urls(), urls)

    @mock.patch("gamestonk_terminal.thought_of_the_day.requests")
    def test_get_metadata(self, mock_request_get):
        urls = {"some author": "https://www.goodreads.com/author/quotes/someauthor"}

        mock_request_get.get().text = mock_goodreads_page

        a_totd = thought_of_the_day.ThoughtOfTheDay(urls)

        meta = a_totd.get_metadata("some author")

        self.assertEqual(
            meta,
            {
                "pages": "6",
                "quoutes": "171",
                "quotes": [
                    "\n      “Do not spoil what you have”\n    ―\n  \n    Epicurus\n  \n"
                ],
            },
        )
