import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import pandas as pd

from sr_parser import main as p


def nlp_parsing():
    text = ['What track on beautiful life has the same name as a country?',
            'what kinds of movie is the desperate hours']
    parsed_text = p.parser(text)
    all_results = p.subject_object_getter(parsed_text)
    for i, j in zip(all_results, text):
        i.append(j)
    df = pd.DataFrame(all_results, columns=[
                      'subject', 'object', 'raw_question'])
    assert df.ix[0, 0][0] == 'track'
