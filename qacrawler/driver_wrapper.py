"""
This module abstracts away getting a browser driver.

Currently we only have Chrome bindings.
"""
import logging
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


def get_selenium_driver(driver_type='Firefox'):
    if driver_type == 'Firefox':
        return get_firefox_driver()
    elif driver_type == 'Chrome':
        return get_chrome_driver()
    elif driver_type == 'PhantomJS':
        raise NotImplementedError('PhantomJS usage is not implemented.')


def get_chrome_driver():
    """
    Get a Chrome Driver.

    The driver executable (chromedriver) must be in the system path.

    :return: selenium Chrome webdriver
    :rtype: selenium.webdriver.chrome.webdriver.WebDriver
    """
    driver = webdriver.Chrome()
    return driver


def get_firefox_driver():
    """
    Get a Firefox Driver.

    The driver executable (wires) must be in the system path.

    :return: selenium Firefox webdriver
    :rtype: selenium.webdriver.firefox.webdriver.WebDriver
    """
    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    driver = webdriver.Firefox(capabilities=firefox_capabilities)
    return driver


def disable_javascript(driver, driver_type='Firefox'):
    if driver_type == 'Firefox':
        return disable_javascript_on_firefox(driver)
    elif driver_type == 'Chrome':
        raise NotImplementedError('Disabling Javascript on Chrome is not implemented.')


def disable_javascript_on_firefox(driver):
    """
    Manually disable Javascript on Firefox.

    Setting profile preference on Javascript method (shown below) does not work anymore.
    Hence, we have to manually
    - visit Firefox Configuration page (about:config)
    - click on 'I accept the risk!' button that warns about messing with Firefox settings
    - narrow down the configurations list by typing 'javascript.enabled' into text box
    - togge javascript.enabled setting to False by highlighting it and pressing return

    Not working method:
    profile = webdriver.FirefoxProfile()
    profile.set_preference("javascript.enabled", False);
    driver = webdriver.Firefox(profile)
    """
    logging.info('Disabling Javascript...')
    driver.get(FirefoxConfigInfo.CONFIG_PAGE_URL)  # Firefox's configuration page opens when this url is visited
    try:
        warning_button = driver.find_element_by_id(FirefoxConfigInfo.ACCEPT_WARNING_BUTTON_ID)
        warning_button.click()
    except NoSuchElementException:
        pass
    text_box = driver.find_element_by_id(FirefoxConfigInfo.CONFIGURATIONS_SEARCH_BOX)
    text_box.send_keys(FirefoxConfigInfo.JAVASCRIPT_CONFIGURATION_NAME)
    time.sleep(2.0)  # wait for the configuration list to respond to entered text
    config_tree = driver.find_element_by_id(FirefoxConfigInfo.CONFIGURATION_ELEMENTS_LIST_ID)
    config_tree.send_keys(Keys.ARROW_DOWN)  # Select first item in the list
    time.sleep(1.0)  # wait for the configuration list to respond to selecting setting
    config_tree.send_keys(Keys.RETURN)  # Toggle selected item
    time.sleep(1.0)


class FirefoxConfigInfo(object):
    """Has DOM information for Firefox's Configuration Page."""
    FIREFOX_VERSION = '49.0.1'  # works on this version
    CONFIG_PAGE_URL = 'about:config'
    ACCEPT_WARNING_BUTTON_ID = 'warningButton'
    CONFIGURATIONS_SEARCH_BOX = 'textbox'
    JAVASCRIPT_CONFIGURATION_NAME = 'javascript.enabled'
    CONFIGURATION_ELEMENTS_LIST_ID = 'configTree'


def get_phantomjs_driver():
    # TODO Implement PhantomJS driver version instead of Chrome driver
    pass
