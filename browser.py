import os
import pyautogui
import re
from time import sleep
from configparser import ConfigParser
from typing import Union, Tuple
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
    TimeoutException,
    WebDriverException,
)
import csv
global timeout
timeout = 10


class Explorer:
    """The web browser instance object needed for TEZote."""
    def __init__(self, **kwargs):
        self.zotero_addon = {"x_pos": 0, "y_pos": 0}
        self._browser_exe = kwargs.get("browser_exe",os.path.join(os.path.expanduser('~'), 'AppData','Local','Mozilla Firefox','firefox.exe'))
        self._driver_exe = kwargs.get("driver_exe",r"src\drivers\geckodriver.exe")
        self.timeout = kwargs.get("timeout",10)
        self.browser = self.create_browser()
        firefox_profiles = ConfigParser()
        firefox_profiles.read(os.path.join(os.getenv("APPDATA"),r"Mozilla\Firefox\profiles.ini"))
        firefox_profile = firefox_profiles.get('Profile0', 'Path')
        self._test_url: str = r"https://www.legifrance.gouv.fr/download/securePrint?token=a5ZgN9nEj$5neyPSKVW!",
        self.max_tries = 3
        # Login to TE portal.
        self.count = 0
        if os.path.isfile(r"src\decrees.txt"):
            self.decree = dict(csv.DictReader(open(r"src\decrees.txt")))
        else:
            self.decree = {i:None for i in range(0,1000)}

    def __new__(cls, **kwargs) -> Union[None]:
        """Class constructor, returns None if it does not find the executables

        Class constructor, tests if the executables are there and returns the class
        if they are found, returns a None if they are not.

        Extra arg/kwarg Parameters
        ------------------
        Allowed extra parameters (*args, or **kwargs) passed by specifying the keyword from the following list.
        **kwargs : optional.
            By default browser_exe, and driver_exe should be passed.

            browser_exe : str
                By default os.path.join(os.path.expanduser('~'), 'AppData','Local','Mozilla Firefox','firefox.exe')
                => The browser executable path.

            driver_exe : str
                By default r"src\\drivers\\geckodriver.exe"
                => The driver executable path.

        Returns
        -------
        Union[None]:

        class => Either the Explorer class object, or None
        """
        browser_exe = kwargs.get("browser_exe",os.path.join(os.path.expanduser('~'), 'AppData','Local','Mozilla Firefox','firefox.exe'))
        driver_exe = kwargs.get("driver_exe",r"src\drivers\geckodriver.exe")
        if (os.path.isfile(browser_exe) and os.path.isfile(driver_exe)):
            return super(Explorer,cls).__new__(cls)


    def create_browser(self,
    ) -> WebDriver:
        """Create a browser instance

        Creates a instance by using the corresponding driver. For the moment only firefox
        is supported, but in practice extension to chrome and edge should be simple.

        Returns
        -------
        WebDriver:

        browser => The browser instance object.


        Example
        -------
        >>> create_browser(browser_exe=os.path.join(os.path.expanduser('~'), 'AppData','Local','Mozilla Firefox','firefox.exe'),driver_exe=r"src\\drivers\\geckodriver.exe",)
        >>> type(browser)
        <class 'selenium.webdriver.firefox.webdriver.WebDriver'>
        """

        options = Options()
        # Provide user location for preferred browser (TODO: Implement standard location for other browsers)
        options.binary_location = self._browser_exe
        desired_caps = DesiredCapabilities.FIREFOX.copy()
        desired_caps.update({"acceptInsecureCerts": True, "acceptSslCerts": True})
        # Open a new driver session for firefox (tests to be added for other browsers, but concept is the same and selenium functions are common, hence not expecting much to be changed)
        browser = webdriver.Firefox(
            # profile,
            capabilities=desired_caps,
            options=options,
            executable_path=self._driver_exe,
            firefox_binary=self._browser_exe,
        )
        return browser


    def end_browsing(self):
        """Closes the browser instance.


        Example
        -------
        >>> end_browsing()
        """
        # After all references are imported or updated, quits the selenium browser
        self.browser.quit()
