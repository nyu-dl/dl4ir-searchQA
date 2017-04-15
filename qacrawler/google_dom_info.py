"""
This module includes information about Google search page specific HTML information to be used in parsing.

It includes class names such as the class assigned to search result DIV's etc.
"""


class GoogleDomInfoBase(object):
    RESULT_TITLE_CLASS = 'r'
    RESULT_URL_CLASS = '_Rm'
    RESULT_DESCRIPTION_CLASS = 'st'
    RESULT_RELATED_LINKS_DIV_CLASS = 'osl'
    RESULT_RELATED_LINK_CLASS = 'fl'
    NEXT_PAGE_ID = 'pnnext'


class GoogleDomInfoWithJS(GoogleDomInfoBase):
    RESULT_DIV_CLASS = 'rc'
    SEARCH_BOX_XPATH = '//*[@id="lst-ib"]'


class GoogleDomInfoWithoutJS(GoogleDomInfoBase):
    RESULT_DIV_CLASS = 'g'
    SEARCH_BOX_XPATH = '//*[@id="sbhost"]'
    NAVIGATION_LINK_CLASS = 'fl'
    PREFERENCES_BUTTON_ID = 'gbi5'
    NUMBER_OF_RESULTS_SELECT_ID = 'numsel'
    SAVE_PREFERENCES_BUTTON_NAME = 'submit2'
