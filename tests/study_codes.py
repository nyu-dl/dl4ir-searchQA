"""
The codes in each function are meant to be run in a Python interpreter at project root folder.

These are different than test modules. Here the goal is to have some variables in an interpreted to be
analyzed interactively. For example, to create a SearchResult, or Entry object and see how it works.

In PyCharm, to run the source code from the editor in Python console:
1) Select code in editor
2) Choose "Execute selection in console" in context menu (ALT + SHIFT + E)

Source: https://www.jetbrains.com/help/pycharm/2016.2/loading-code-from-editor-into-console.html
"""

def study_initialize_visit():
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC

    from qacrawler import driver_wrapper
    from qacrawler import google_dom_info
    from qacrawler import sr_parser

    sr_parser.gdom = google_dom_info.GoogleDomInfoWithoutJS
    driver = driver_wrapper.get_firefox_driver()
    driver_wrapper.disable_javascript_on_firefox(driver)

    sr_parser.visit_google(driver, 'foo')
    search_box = sr_parser.wait_for_and_get_search_box(driver)


def study_google_preferences():
    from qacrawler.google_dom_info import GoogleDomInfoWithoutJS as GDom
    from qacrawler import main

    google_preferences_page_url = 'http://www.google.com/preferences?hl=en'
    driver.get(google_preferences_page_url)

    main.set_number_of_results_per_page(driver, 20)


def study_entry():
    from crawler import jeopardy
    tiny_dataset = jeopardy.Dataset('tests/data/tiny_dataset.json')
    for no in range(len(tiny_dataset.data)):
        entry = tiny_dataset.get_entry(no)
        print entry.id, entry.tag, entry.question


def study_next_page_links():
    from crawler import parser
    from crawler import driver_wrapper

    driver = driver_wrapper.get_chrome_driver('/usr/local/bin/chromedriver')
    parser.visit_google_front_page(driver)
    search_box = parser.wait_for_and_get_search_box(driver)
    parser.submit_query('abidin', search_box)

    for n in range(2):
        parser.wait_for_search_results(driver)
        npu = parser.get_next_page_url(driver)
        print npu
        driver.get(npu)

    driver.quit()


def study_parsing_result_divs():
    import os
    from selenium.webdriver.common.by import By
    from crawler import parser
    from crawler import driver_wrapper
    from crawler import google_dom_info as gdom
    driver = driver_wrapper.get_chrome_driver('/usr/local/bin/chromedriver')

    html_file = 'tests/data/cheese%20-%20Google%20Search.html'
    local_file_url = 'file://' + os.path.abspath(html_file)
    driver.get(local_file_url)

    results = parser.get_search_result_divs(driver)

    for element in results:
        h3 = element.find_element(By.CLASS_NAME, gdom.RESULT_TITLE_CLASS)
        anchor = h3.find_element(By.TAG_NAME, 'a')  # tag: a
        url = anchor.get_attribute('href')
        print url

    driver.quit()


def study_logging():
    """
    Log message formatting items
    https://docs.python.org/2/library/logging.html#logrecord-attributes
    :return:
    """
    import logging
    reload(logging)
    log_attributes = ['levelname', 'asctime', 'module', 'funcName', 'message']
    log_format = ':'.join(['%%(%s)s' % attr for attr in log_attributes])
    logging.basicConfig(filename='example.log',
                        format=log_format,
                        level=logging.DEBUG)
    logging.info('started.')
    logging.debug('analyzing this...')


def study_command_line():
    pass
    # Study logging level
    # python -c 'import main; print main.parse_command_line_arguments()' --log-level=DEBUG -j='aa'


def misc():
    from crawler import jeopardy
    from crawler import main
    dataset = jeopardy.Dataset('tests/data/tiny_dataset.json')
    gen = main.get_entries_to_search(dataset, 0, len(dataset.data))
