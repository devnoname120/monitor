import time
from urllib.parse import urlparse
import os

import requests
from selenium import webdriver

from .base import USERSCRIPT, download, quiting, Runner


CHROME_DRIVER_META_URL = 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE'
CHROME_DRIVER_URL = 'http://chromedriver.storage.googleapis.com/{version}/chromedriver_linux64.zip'
CHROME_STORE_URL = 'https://clients2.google.com/service/update2/crx?response=redirect&prodversion=40.0&x=id%3D{id}%26installsource%3Dondemand%26uc'
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36',
    'Referer': 'https://chrome.google.com',
}
CD_PATH = '/tmp/chromedriver'
TM_ID = 'dhdgffkkebhmkfjojejmpbldmpobfkfo'
TM_PATH = '/tmp/tampermonkey.crx'


def get_version():
    r = requests.get(url=CHROME_DRIVER_META_URL)
    return r.text


class ChromeRunner(Runner):

    def do_prepare(self):
        if not os.path.exists(CD_PATH):
            version = get_version()
            download(CHROME_DRIVER_URL.format(version=version), CD_PATH)
        if not os.path.exists(TM_PATH):
            download(CHROME_STORE_URL.format(id=TM_ID), TM_PATH, headers=REQUEST_HEADERS)

        profile = webdriver.ChromeOptions()
        profile.add_extension(extension=TM_PATH)

        with quiting(webdriver.Chrome(executable_path=CD_PATH, chrome_options=profile)) as driver:
            # Tampermonkey may not ready yet
            time.sleep(5)
            driver.get(USERSCRIPT)
            time.sleep(5)

            # find the confirm tab
            # TODO close tabs
            handles = driver.window_handles
            for handle in handles:
                driver.switch_to.window(handle)
                if driver.current_url.startswith('chrome-extension://'):
                    install = driver.find_element_by_css_selector('input.install[value$=nstall]')
                    install.click()
                    break