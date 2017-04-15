"""
Main entry point of qacrawler

Parses command line arguments. Loads the dataset. Chooses the entries to crawl. Crawl chosen entries. Quit.
"""
import argparse
import logging
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import driver_wrapper
import jeopardy
import crawler
import sr_parser
from google_dom_info import GoogleDomInfoWithoutJS as GDom


def main():
    crawler_settings, entries = initialize()
    crawler.crawl(crawler_settings, entries)
    finalize(crawler_settings.driver)


def initialize():
    """Initialize collector.

    Initialize by parsing command line arguments, reading Jeopardy entries from dataset file
    and getting browser driver.
    """
    args = parse_command_line_arguments()
    configure_logging(log_level=args.log_level)
    create_folder_if_not_exists(args.output_folder)
    dataset = jeopardy.Dataset(filepath=args.jeopardy_json)
    entries = get_entries_to_search(dataset, first=args.first, last=args.last)
    driver = driver_wrapper.get_selenium_driver(args.driver_type)
    if args.disable_javascript:
        driver_wrapper.disable_javascript(driver, args.driver_type)
    set_number_of_results_per_page(driver, args.results_per_page)
    settings = crawler.CrawlerSettings(driver, args.num_pages, args.output_folder, args.wait_duration,
                                       args.simulate_typing, args.simulate_clicking, args.disable_javascript)
    logging.info('Start.')
    return settings, entries


def parse_command_line_arguments():
    """Parse command line arguments

    :return: An object of which attributes are command line arguments
    :rtype: argparse.ArgumentParser
    """
    argparser = argparse.ArgumentParser(description='Crawl Google to generate QA dataset')
    argparser.add_argument('-j', '--jeopardy-json', type=str, required=True,
                           help='Path to Jeopardy dataset file')
    argparser.add_argument('-d', '--driver-type', type=str, default='Firefox',
                           help='The browser/driver type to be used by crawler',
                           choices=['Firefox', 'Chrome', 'PhantomJS'])
    argparser.add_argument('-o', '--output-folder', type=str, required=True,
                           help='If a folder is given the output files will be written there. '
                                'If given folder does not exist it will be created first.')
    argparser.add_argument('-f', '--first', type=int, default=0,
                           help='First entry from which to start reading questions')
    argparser.add_argument('-l', '--last', type=int, default=216930,
                           help='Last entry at which to stop reading questions')
    argparser.add_argument('-n', '--num-pages', type=int, default=1,
                           help='Number of search result pages to parse per query')
    argparser.add_argument('-g', '--log-level', type=str, default='INFO',
                           help='Set the level of log messages below which will be saved to log file',
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    argparser.add_argument('-w', '--wait-duration', type=int, default=4,
                           help='Number of seconds to wait before getting the next page')
    argparser.add_argument('--simulate-typing', action='store_true',
                           help='When included simulates human typing by pressing keys one-by-one')
    argparser.add_argument('--simulate-clicking', action='store_true',
                           help='When included simulates mouse clicking on next page link')
    argparser.add_argument('--disable-javascript', action='store_true',
                           help='When included disables JavaScript (only for Firefox)')
    argparser.add_argument('--results-per-page', type=int, default=10,
                           help='The number of search results in a page per query',
                           choices=[10, 20, 30, 50, 100])
    args = argparser.parse_args()
    return args


def configure_logging(log_level, log_file='jeopardy_crawler.log',
                      log_format='%(levelname)s:%(asctime)s:%(module)s:%(funcName)s:%(message)s'):
    """Configure Crawler's logger and Suppress selenium's browser logger.

    Selenium's browser logger logs every HTTP requests etc. We are not interested in that."""
    log_level_num = getattr(logging, log_level)
    logging.basicConfig(filename=log_file, format=log_format, level=log_level_num)
    from selenium.webdriver.remote.remote_connection import LOGGER as SELENIUM_LOGGER
    SELENIUM_LOGGER.setLevel(logging.INFO)


def create_folder_if_not_exists(folder):
    """
    :param folder: path to folder
    :type folder: str
    :rtype None:
    """
    if not os.path.exists(folder):
        os.makedirs(folder)


def get_entries_to_search(dataset, first, last):
    """Get entries to do search queries.

    :rtype generator[jeopardy.Entry]"""
    if last >= dataset.size: last = dataset.size
    entries = (dataset.get_entry(no) for no in range(first, last))
    return entries


def set_number_of_results_per_page(driver, num_results):
    """Manually set the number of search results per page when Javascript is disabled.

    Manually
    - visit Google Search's preferences page
    - find the element to set number of results per page
    - set it to the value given in command-line arguments
    """
    logging.debug('Setting search results per page to %d...' % num_results)
    redirect_nonjavascript_version_of_google_by_making_a_dummy_query(driver)
    visit_google_search_preferences_page(driver)
    find_select_and_set(driver, num_results)
    save_preferences(driver)


def redirect_nonjavascript_version_of_google_by_making_a_dummy_query(driver):
    """
    If we first visit preferences page directly, Google gives "Your cookies seem to be disabled." warning.
    Hence first do a dummy search, so that Google redirects us to its non-Javascript version.
    """
    sr_parser.visit_google(driver, 'Increase search results per page...')
    sr_parser.wait_for_presence_and_get_element(driver, (By.XPATH, GDom.SEARCH_BOX_XPATH))


def visit_google_search_preferences_page(driver):
    google_preferences_page_url = 'http://www.google.com/preferences?hl=en'
    driver.get(google_preferences_page_url)


def find_select_and_set(driver, num_results):
    select = wait_for_and_scroll_into_view_and_get_num_results_select(driver)
    time.sleep(1)
    select.select_by_value(str(num_results))
    logging.info('Selected value: %s' % select.first_selected_option.text)
    time.sleep(1)


def wait_for_and_scroll_into_view_and_get_num_results_select(driver):
    """
    :return: Select html element to set number of search results per page
    :rtype: selenium.webdriver.support.ui.Select
    """
    select_locator = (By.ID, GDom.NUMBER_OF_RESULTS_SELECT_ID)
    select = sr_parser.wait_for_presence_and_get_element(driver, select_locator)
    coordinates = select.location_once_scrolled_into_view  # first scrolls to element then returns location
    select = Select(select)
    return select


def save_preferences(driver):
    save_preferences_button = driver.find_element(By.NAME, GDom.SAVE_PREFERENCES_BUTTON_NAME)
    save_preferences_button.click()
    time.sleep(1)


def finalize(driver):
    logging.info('End.')
    driver.quit()


if __name__ == '__main__':
    main()
