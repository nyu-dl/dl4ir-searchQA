"""
Module to crawl entries and save the results.
"""
import json
import logging
import os

import sr_parser


def crawl(settings, entries):
    """
    Crawl search results of given Jeopardy entries according to given crawler settings.

    :param settings: Crawler settings object
    :type settings: CrawlerSettings
    :param entries: Jeopary dataset entries
    :type entries: collections.Iterable[qacrawler.jeopardy.Entry]
    :return:
    """
    for entry in entries:
        logging.info('Question no %06d: %s. Crawl!' % (entry.id, entry.question))
        results = sr_parser.collect_query_results_from_google(entry.question, settings)
        logging.info('Question no %06d. Collected %d search results.' % (entry.id, len(results)))
        if results:
            save_results_for_entry(results, entry, settings.output_folder)


def save_results_for_entry(results, entry, output_folder, file_type='json'):
    """
    Format search results into json or tsv and save them to a file.

    :param results: a list of SearchResults
    :type results: list[sr_parser.SearchResult]
    :param entry: jeopardy Entry
    :type entry: jeopardy.Entry
    :param output_folder: path to output folder
    :type output_folder: str
    :param file_type: the type of the saved file. Can only have values ['json', 'tsv']
    :type file_type: str
    :rtype: None
    """
    if file_type == 'json':
        formatted_results = results_list_to_output(results, entry)
    else:
        formatted_results = results_list_to_tsv(results)

    file_folder = output_folder if output_folder else '.'
    file_name = generate_filename(entry, file_type)
    file_path = os.path.join(file_folder, file_name)
    with open(file_path, 'wt') as f:
        f.write(formatted_results)


def results_list_to_output(results, entry):
    """
    Format a list of SearchResults into a JSON string.

    :param results: a list of SearchResults
    :type results: list[sr_parser.SearchResult]
    :param entry: Jeopardy entry
    :type entry: jeopardy.Entry
    :return: string in JSON format
    :rtype: str
    """
    result_dicts = [res.to_dict() for res in results]
    output_dict = {'search_results': result_dicts}
    output_dict.update(entry.to_dict())
    results_json = json.dumps(output_dict, indent=4)  # Pretty-print via indent. Splits keys into multiple lines.
    return results_json


def results_list_to_tsv(results):
    """
    Format a list of SearchResults into a TSV (Tab Separated Values) string.

    :param results: a list of SearchResults
    :type results: list[sr_parser.SearchResult]
    :return: string in TSV format
    :rtype: str
    """
    results_tab_separated = [str(res) for res in results]
    results_str = '\n'.join(results_tab_separated)
    return results_str


def generate_filename(entry, extension):
    filename = '%06d-%s.%s' % (entry.id, entry.tag, extension)
    return filename


# TODO have a process pipeline
def process_pipeline():
    pass
    # Get a SearchResult
    # save %06d-%s-raw.txt % (q_num_id, q_text_id)
    # Filter out exact matches
    # save %06d-%s-flt.txt % (q_num_id, q_text_id)
    # Tokenize
    # save %06d-%s-tok.txt % (q_num_id, q_text_id)
    # Other NLP operator
    # save %06d-%s-oth.txt % (q_num_id, q_text_id)


class CrawlerSettings:
    def __init__(self, driver, num_pages, output_folder, wait_duration,
                 simulate_typing, simulate_clicking, disable_javascript):
        """
        Singleton class that holds configuration info for crawler.

        It is to make sharing of crawler settings easier among the project. We do not want higher-level
        functions in the functionality abstraction hierarchy to be bloated with too many arguments.

        :param driver: selenium driver with which we are going to visit Google
        :type driver: selenium.webdriver.chrome.webdriver.WebDriver
        :param num_pages: number of results pages to read (at most)
        :type num_pages: int
        :param output_folder:
        :param wait_duration: duration to wait between search results pages in seconds
        :type wait_duration: float
        :param simulate_typing: indicates whether or not to simulate human key typing
        :type simulate_typing: bool
        :param simulate_typing: indicates whether or not to simulate human mouse clicking
        :type simulate_clicking: bool
        """
        self.driver = driver
        self.num_pages = num_pages
        self.output_folder = output_folder
        self.wait_duration = wait_duration
        self.simulate_typing = simulate_typing
        self.simulate_clicking = simulate_clicking
        self.disable_javascript = disable_javascript
