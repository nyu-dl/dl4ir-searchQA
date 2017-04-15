"""
This module deals with crawling Google search results and parsing result pages.

A SearchResult is an object that holds parsed search results.

collect_query_results_from_google() function is to crawl a query's search results into SearchResult objects.

Terminology is taken from Google help at: https://support.google.com/websearch/answer/35891?hl=en#results
"""
import logging
import random
import sys
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

import google_dom_info

GDOM = None


def collect_query_results_from_google(query, settings):
    """
    Get formatted search results given a search query and the number of pages to parse.

    :param query: search query
    :type query: str
    :param settings: Crawler settings object
    :type settings: qacrawler.crawler.CrawlerSettings
    :return: A list of SearchResult objects
    :rtype: list[SearchResult]
    """
    set_gdom(settings.disable_javascript)
    if settings.disable_javascript:
        visit_google(settings.driver, query='%20')  # request a search result page with no results
    else:
        visit_google(settings.driver)
    check_google_bot_police(settings.driver)
    search_box = wait_for_and_get_search_box(settings.driver)
    submit_query(query, search_box, settings.simulate_typing, settings.driver)
    all_results = parse_n_search_result_pages(settings,
                                              num_pages=settings.num_pages, wait_duration=settings.wait_duration)
    return all_results


def set_gdom(disable_javascript):
    """Choose the Google DOM information according whether Javascript is disabled or not."""
    global GDOM
    if disable_javascript:
        GDOM = google_dom_info.GoogleDomInfoWithoutJS
    else:
        GDOM = google_dom_info.GoogleDomInfoWithJS


def visit_google(driver, query=None):
    """If a query is given directly search that query otherwise just open Google's front page."""
    url = 'http://google.com'
    if query is not None:
        url = url + '/search?q=' + query
    driver.get(url)  # visit a search results page with no search results


def check_google_bot_police(driver):
    """Give error and quit if caught by Google Bot Police."""
    robot_police_text = 'Our systems have detected unusual traffic'
    if robot_police_text in driver.page_source:
        logging.critical('Caught by Google Bot Police :-(. Exiting...')
        quit_driver_and_exit(driver)


def wait_for_and_get_search_box(driver):
    search_box_locator = (By.XPATH, GDOM.SEARCH_BOX_XPATH)
    search_box = wait_for_presence_and_get_element(driver, search_box_locator)
    return search_box


def wait_for_presence_and_get_element(driver, locator, timeout=10):
    try:
        condition = EC.presence_of_element_located(locator)
        element = WebDriverWait(driver, timeout=timeout).until(condition)
        return element
    except TimeoutException:
        logging.critical('TimeoutException: Could not get the element at %s. ' % str(locator) +
                         'There is a connection problem. Exiting.')
        quit_driver_and_exit(driver)


def quit_driver_and_exit(driver):
    driver.quit()
    sys.exit()


def submit_query(query, search_box, simulate_typing, driver):
    """Choose query submission type according to simulate_typing."""
    if simulate_typing:
        submit_query_by_typing(driver, query, search_box)
    else:
        submit_query_at_once(query, search_box)


def submit_query_by_typing(driver, query, search_box):
    """Submit query by sending keys one-by-one."""
    ActionChains(driver).move_to_element(search_box).click().perform()
    simulate_typing(search_box, query)
    result_divs = driver.find_elements_by_class_name(GDOM.RESULT_DIV_CLASS)
    search_box.send_keys(Keys.ENTER)
    search_box.submit()
    if result_divs:
        wait_for_page_load_after_submission(driver, result_divs)


def wait_for_page_load_after_submission(driver, result_divs):
    """Wait for the query string to arrive Search Engine."""
    logging.debug('wait for staleness after submitting search query')
    WebDriverWait(driver, timeout=5).until(
        EC.staleness_of(result_divs[0])
    )
    logging.debug('staleness ended')


def simulate_typing(element, text):
    for char in text:
        element.send_keys(char)
        wait_with_variance(0.05, variation=0.05)


def submit_query_at_once(query, search_box):
    """Submit query by entering whole question string at once."""
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    # search_box.submit()


def parse_n_search_result_pages(settings, num_pages, wait_duration):
    """
    Parse num_pages of search result pages and return all SearchResults found.

    :param wait_duration: duration to wait between search results pages in seconds
    :type wait_duration: float
    :param num_pages: Number of search result pages to parse per query
    :type num_pages: int
    :return: list of SearchResult parsed from num_pages of search result pages
    :rtype: list[SearchResult]
    """
    all_results = []
    for page_no in range(num_pages):
        logging.debug('Parsing page %d.' % page_no)
        page_results = parse_one_search_result_page(settings.driver)
        if not page_results:
            return all_results
        all_results.extend(page_results)
        wait_with_variance(duration=wait_duration)
        next_page_exists = request_next_page(settings.driver, settings.simulate_clicking, settings.disable_javascript)
        if not next_page_exists:
            break
    return all_results


def request_next_page(driver, simulate_clicking, disable_javascript):
    """
    Find next page element/url and if exists request it.

    :param driver: selenium driver with which we'll collect data from opened search result page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param simulate_clicking: if True request next page by clicking on element otherwise request it via
    driver.get method
    :type simulate_clicking: bool
    :return: Whether the next page element exists or not
    :rtype: bool
    """
    if simulate_clicking:
        next_page_element = get_next_page_element(driver)
        if next_page_element:
            ActionChains(driver).move_to_element(next_page_element).perform()
            wait_with_variance(duration=0.2, variation=0.2)
            ActionChains(driver).click(next_page_element).perform()
            wait_for_page_load_after_clicking_on_link(driver)
            return True
    else:
        next_page_url = get_next_page_url_no_js(driver) if disable_javascript else get_next_page_url_js(driver)
        if next_page_url:
            driver.get(next_page_url)
            return True
    return False


def wait_for_page_load_after_clicking_on_link(driver):
    """
    Unlike opening a new page via driver.get opening a new page via clicking on a link is a more complicated process.
    Clicking on a link is an asynchronious operation, i.e. browser driver does not wait for the action that is
    trigger by clicking to finish. Because the action can be anything including opening a new page,
    sending an AJAX request, or even nothing.

    Our technique to make the operation a blocking operation by waiting until the new page request is to see whether the
    search results that appeared while we were simulated-typing went stale.
    """
    a_div = get_search_result_divs(driver)[0]
    logging.debug('wait for staleness after clicking next page')
    WebDriverWait(driver, timeout=5).until(
        EC.staleness_of(a_div)
    )
    logging.debug('staleness ended')


def parse_one_search_result_page(driver):
    """
    Wait the search result page to load and call page parse function.

    :param driver: selenium driver with which we'll open results page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: A list of SearchResult objects. If there are no results return an empty list
    :rtype: list[SearchResult]
    """
    try:
        wait_for_search_results(driver)
    except TimeoutException:
        logging.warning('TimeoutException: Either there are no search results (e.g. false alarm) '
                        'or Google realized that we are a bot :-( '
                        'or there is connection problem (less likely).')
        return []
    results = parse_opened_results_page(driver)
    logging.debug('Collected %d search results.' % len(results))
    return results


def wait_for_search_results(driver, timeout=10):
    elem = WebDriverWait(driver, timeout=timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, GDOM.RESULT_DIV_CLASS))
    )
    logging.debug('wait_for_search_results ENDED')


def wait_with_variance(duration, variation=1.0):
    """Wait a while to pass Google's bot detection."""
    uniform = random.random() * variation
    duration += uniform
    time.sleep(duration)


def get_next_page_element(driver):
    """
    Get HTML element for next page link so that we can click on it.

    :param driver: the selenium driver that is used to open the search results page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: next page element if exists else None
    :rtype: selenium.webdriver.remote.webelement.WebElement
    """
    next_page_elements = driver.find_elements(By.ID, GDOM.NEXT_PAGE_ID)
    if next_page_elements:
        next_page_element = next_page_elements[0]
    else:
        next_page_element = None
        logging.debug('There is no next page.')
    return next_page_element


def get_next_page_url_js(driver):
    """
    Get next page url when Javascript is enabled.

    :param driver: the selenium driver that is used to open the search results page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: url if exists else None
    :rtype: str
    """
    next_page_link = driver.find_elements(By.ID, GDOM.NEXT_PAGE_ID)
    if next_page_link:
        next_page_url = next_page_link[0].get_attribute('href')
    else:
        next_page_url = None
        logging.debug('There is no next page.')
    return next_page_url


def get_next_page_url_no_js(driver):
    """
    Get next page url when Javascript is disabled.

    Google does not give an HTML id to next page link element when Javascript is disabled.

    :param driver: the selenium driver that is used to open the search results page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: url if exists else None
    :rtype: str
    """
    navigation_elements = driver.find_elements(By.CLASS_NAME, GDOM.NAVIGATION_LINK_CLASS)
    if not navigation_elements:
        logging.debug('There is no next page.')
        return None
    last_navigation_element = navigation_elements[-1]
    if last_navigation_element.text != 'Next':
        logging.debug('There is no next page.')
        return None
    next_page_url = last_navigation_element.get_attribute('href')
    return next_page_url


def parse_opened_results_page(driver):
    """Parse a loaded search result page into a list of SearchResult objects.

    It parses 4 parts ("title", "url", "short description" and, if exists, "related links") from each
    search result item.

    :param driver: the selenium driver that is used to open the search results page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: A list of SearchResult objects
    :rtype: list[SearchResult]
    """
    elements = get_search_result_divs(driver)
    results = []
    for no, elem in enumerate(elements):
        try:
            results.append(SearchResult(elem))
        except NotAParsableSearchResult:
            logging.debug('Search result DIV no %d is not parsable. '
                          'It can be a non-website result such as a video.' % no)
            continue
    return results


def get_search_result_divs(driver):
    """From the opened page, get a list of DIVs where each DIV is a result.

    :param driver: selenium driver with which results page is opened
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :rtype: list[bs4.element.Tag]
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.select('.' + GDOM.RESULT_DIV_CLASS)  # tag: div
    return elements


class SearchResult(object):
    """Parses search result information such as title, url, snippet from div and keep them in related attributes"""
    def __init__(self, element):
        """Parse a search result DIV to get title, url, short description.

        :param element: HTML element, a DIV that holds a search result
        :type element: bs4.element.Tag
        """
        self.element = element
        self.title = self.parse_title(element)
        logging.debug('parsing result ' + self.title)
        self.url = self.parse_url(element)
        self.snippet = self.parse_snippet(element)
        self.related_links = self.parse_related_links(element)

    @staticmethod
    def parse_title(element):
        title = element.select_one('.' + GDOM.RESULT_TITLE_CLASS)
        if title is None:
            raise NotAParsableSearchResult
        return title.text.encode('ascii', 'ignore')

    @staticmethod
    def parse_url(element):
        h3 = element.select_one('.' + GDOM.RESULT_TITLE_CLASS)
        anchor = h3.find('a')  # tag: a
        if anchor is None:
            raise NotAParsableSearchResult
        url = anchor['href']
        return url.encode('ascii', 'ignore')

    @staticmethod
    def parse_snippet(element):
        # snippet might not exist for result item
        snippet = element.select_one('.' + GDOM.RESULT_DESCRIPTION_CLASS)  # tag: span
        return snippet.text.encode('ascii', 'ignore') if snippet else None

    @staticmethod
    def parse_related_links(element):
        # related links might not exist for result item
        # first check if their div exists. If yes, get the list of link elements
        related_links_div = element.select_one('.' + GDOM.RESULT_RELATED_LINKS_DIV_CLASS)  # tag: div
        if related_links_div:
            related_links = related_links_div.select('.' + GDOM.RESULT_RELATED_LINK_CLASS)  # tag: a
            related_links = [rl.text.encode('ascii', 'ignore') for rl in related_links]
        else:
            related_links = None
        return related_links

    def to_dict(self):
        """Convert data in SearchResult object into a dictionary"""
        dict_representation = {'title': self.title,
                               'url': self.url,
                               'snippet': self.snippet,
                               'related_links': self.related_links}
        return dict_representation

    def __str__(self):
        """Format a parsed Google search result into a tab separated string"""
        s = '%s\t' % self.title
        s += '%s\t' % self.url
        s += '%s\t' % (self.snippet if self.snippet else '')
        s += '%s' % (';'.join(self.related_links) if self.related_links else '')
        s = s
        return s


class NotAParsableSearchResult(Exception):
    pass
