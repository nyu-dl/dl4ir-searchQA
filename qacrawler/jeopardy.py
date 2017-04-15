"""
This module is about abstracting away reading Jeopardy dataset.

An Entry is an object that holds parsed Jeopardy entry information such as question, answer etc.

Dataset class is responsible from reading Jeopardy dataset file and converting entries to Entry objects.
"""
import json

from bs4 import BeautifulSoup


class Dataset(object):
    """
    Class that represents Jeopardy! question answer dataset.
    """
    def __init__(self, filepath):
        self.data = self.load_jeopardy_dataset_from_json_file(filepath)
        self.size = len(self.data)

    @staticmethod
    def load_jeopardy_dataset_from_json_file(filepath):
        """
        Read Jeopardy entries from file.

        :param filepath: the path of json file
        :return: A list of dictionaries that hold entry information.
        :rtype: list[dict]
        """
        with open(filepath, 'rt') as json_file:
            data = json.load(json_file)
            return data

    def get_entry(self, no):
        """
        Create an Entry object from the jeopardy entry at line no.

        :param no: The number of entry, in the order they are saved in json file
        :return: at the at the line no
        :rtype: Entry
        """
        entry = Entry(entry_dict=self.data[no], entry_id=no)
        return entry


class Entry(object):
    """Class that represents a Jeopardy! entry."""
    KEYS = [u'category', u'air_date', u'question', u'value', u'answer', u'round', u'show_number']

    def __init__(self, entry_dict, entry_id):
        """
        Construct an Entry object

        :param entry_dict: Entry data read from json file
        :type entry_dict: dict
        :param entry_id: An integer ID for the entry, which is the spatial rank in the dataset file
        :type entry_id: int
        """
        self.id = entry_id
        self.question = self.get_question(entry_dict['question'])
        self.answer = entry_dict['answer']
        self.category = entry_dict['category']
        self.air_date = entry_dict['air_date']
        self.show_number = entry_dict['show_number']
        self.round = entry_dict['round']
        self.value = entry_dict['value']
        self.tag = self.get_tag(entry_dict)

    def to_dict(self):
        d = {key: getattr(self, key) for key in Entry.KEYS}
        d.update({'id': self.id})
        return d

    @staticmethod
    def get_question(string):
        """
        Trim quotation marks and remove HTML tags.

        Trim quotation marks in the beginning and at the end of the string. Remove HTML tags if there are any. (Some
        questions have <a> and <i> tags.

        For some reason json version of the dataset has that quotes.
        """
        string = string[1:-1]
        soup = BeautifulSoup(string, 'html.parser')
        return soup.text

    @staticmethod
    def get_tag(entry_dict):
        """
        Generate a unique tag from entry metadata.

        example: 4999_Double Jeopardy!_AUTHORS IN THEIR YOUTH_$800

        :param entry_dict: A dictionary with keys ['show_number', 'round', 'category', 'value']
        :type entry_dict: dict
        :return: tag of entry
        :rtype: str
        """
        tag_keys = ['show_number', 'round', 'category', 'value']
        tag_parts = [Entry.format_tag_part(entry_dict[key]) for key in tag_keys]
        tag = '_'.join(tag_parts)
        return tag

    @staticmethod
    def format_tag_part(s):
        """
        Make input string all lowercase and filter out non-alphanumeric characters.

        :param s: tag part string to format
        :type s: str
        :return: formatted string
        :rtype: str
        """
        if s is None:
            return ''
        s = s.lower()
        s = ''.join([ch for ch in s if ch.isalnum()])
        return s
