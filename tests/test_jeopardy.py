import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from crawler import jeopardy

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'data', 'tiny_dataset.json')
DATASET = jeopardy.Dataset(DATASET_PATH)


def test_loading():
    dataset_size = 7
    assert len(DATASET.data) == dataset_size
    first_entry_dict = DATASET.data[0]
    assert first_entry_dict['answer'] == 'Copernicus'


def test_getting_entry():
    entry_no = 0
    entry = DATASET.get_entry(entry_no)
    assert isinstance(entry, jeopardy.Entry)
    assert entry.id == entry_no
    assert entry.answer == 'Copernicus'
