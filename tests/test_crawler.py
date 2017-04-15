import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from qacrawler import driver_wrapper
from qacrawler import sr_parser as parser2
from qacrawler import crawler
from qacrawler import main


def test_result_div_parsing():
    driver = driver_wrapper.get_chrome_driver()
    html_file = 'data/one_result.html'
    local_file_url = 'file://' + os.path.abspath(html_file)
    driver.get(local_file_url)

    result_divs = parser2.get_search_result_divs(driver)

    result_div = result_divs[0]
    print 'result_div', result_div
    sr = parser2.SearchResult(result_div)
    assert sr.title == 'Cheese - Wikipedia, the free encyclopedia'
    assert sr.url == 'https://en.wikipedia.org/wiki/Cheese'
    assert sr.snippet == 'Cheese is a food derived from milk that is produced in a wide range of flavors, textures, and forms by coagulation of the milk protein casein. It comprises proteins ...'
    assert sr.related_links == ['Etymology', 'History', 'Production', 'Processing']
    assert str(sr) == 'Cheese - Wikipedia, the free encyclopedia\thttps://en.wikipedia.org/wiki/Cheese\tCheese is a food derived from milk that is produced in a wide range of flavors, textures, and forms by coagulation of the milk protein casein. It comprises proteins ...\tEtymology;History;Production;Processing'

    driver.quit()


def test_page_parsing(html_file='data/cheese%20-%20Google%20Search.html', parsed_file='data/parsed.tsv'):
    driver = driver_wrapper.get_chrome_driver()
    local_file_url = 'file://' + os.path.abspath(html_file)
    driver.get(local_file_url)

    parsed_results = parser2.parse_opened_results_page(driver)
    formatted = crawler.results_list_to_tsv(parsed_results)

    with open(parsed_file, 'rt') as f:
        from_file = f.read()

    assert formatted == from_file

    driver.quit()
