""" Simple test to make sure selenium installed.  Taken from the docs"""
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as cOpts
from selenium.webdriver.firefox.options import Options as fOpts

from gamestonk_terminal.config_terminal import (
    PATH_TO_SELENIUM_DRIVER as path_to_driver,
    WEBDRIVER_TO_USE as web,
)


class PythonOrgSearch(unittest.TestCase):
    def setUp(self):
        if path_to_driver is None:
            raise FileNotFoundError("driver path not found in config_terminal.py")
        if web == "firefox":
            opts = fOpts()
            opts.headless = True
            self.driver = webdriver.Firefox(
                options=opts, executable_path=path_to_driver
            )
        elif web == "chrome":
            opts = cOpts()
            opts.headless = True
            self.driver = webdriver.Chrome(options=opts, executable_path=path_to_driver)
        else:
            raise FileNotFoundError("Webbrowser not found in config_terminal.py")

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("http://www.python.org")
        self.assertIn("Python", driver.title)
        elem = driver.find_element_by_name("q")
        elem.send_keys("pycon")
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
