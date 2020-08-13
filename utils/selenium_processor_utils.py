from selenium import webdriver
import utils.constants as c
import time


def chrome_driver_setup():
    """
    run this function to setup a chrome driver and open a window
    :return: browser object representing the window opened
    """
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    option.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=c.CHROMEDRIVER_PATH,
                               chrome_options=option)
    return browser


def scroll_down(browser, page):
    # Get scroll height.
    last_height = browser.execute_script("return document.documentElement.scrollHeight")
    i = 0
    while i < page:
        # Scroll down to the bottom.
        browser.execute_script("window.scrollTo({}, document.documentElement.scrollHeight);".format(last_height))
        # Wait to load the page.
        time.sleep(2)
        # Calculate new scroll height and compare with last scroll height.
        new_height = browser.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        i += 1