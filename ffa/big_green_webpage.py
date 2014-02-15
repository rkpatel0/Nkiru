'''
Module creates copy of Big Green HTML templete for visual data analysis.

Created on Feb 13, 2014

@author: rpatel
'''

import pandas as pd
import shutil


class WriteHtml(object):
    '''
    All to-html functions will reside here, return code can be directly written
    to file as this class does not store anything.
    '''

    def __init__(self, page_path, page_name):
        'Set all html string formats.'

        self._set_parent_constants()
        self._set_child_constants()
        self._set_html_format()

        self.page_path = page_path
        self.PAGE_NAME = page_path + page_name
        self.TEMPLATE_PATH = self.WEB_TEMPLATE + self.TEMPLATE_NAME

        shutil.copy(self.TEMPLATE_PATH, self.PAGE_NAME)
        self.TEMPLAGE_PAGE = open(self.PAGE_NAME, 'r')
        self.page_str = self.TEMPLAGE_PAGE.read()

    def _set_parent_constants(self):
        'Set all HTML default templates here'

        self.DEBUG = False
        self.WEB_TEMPLATE = r'../../References/HtmlTemplates/BigGreen/'

    def _set_html_format(self):
        'Static HTML Big-Green Fromat'

        self.IMAGE_FMT = "<img width=%s src=%s height=%s/>"
        self.LINK_FMT = "<a href=%s>%s</a>"
        self.TBL_STYLESIZE_FMT = 'width:%(width)spx;height:%(height)spx;'

        self.TEXT_FMT = "<p>%s<p>\n"
        self.LIST_FMT = "<li>%s</li>\n"
        self.HEADER_FMT = "<h%s>%s</h%s>\n"

        self.HTML_FMT = '<{name}>\n%s\n</{name}>\n'
        self.TBL_IDX = self.HTML_FMT.format(name='th')
        self.TBL_ITEM = self.HTML_FMT.format(name='td')
        self.TBL_ROW = self.HTML_FMT.format(name='tr')
        self.TBL_NAME = self.HTML_FMT.format(name='table')

        self.TBL_DEFAULT = {
                            'class': 'tableone',
                            'width': 100,
                            'height': 50,
                            }

        self.CSS_STYLE = '<div class="{cls}" style="{style}">\n{data}</div>\n'

    def text(self, text):
        'Convert basic test to html format'

        text_html = self.TEXT_FMT % (text)
        self.write_to_file(text_html)

    def link(self, url, name='Click Here'):
        'Convert name to a url link'

        link_html = self.LINK_FMT % (url, name)
        #self.write_to_file(link_html)
        return(link_html)

    def header(self, header, level=2):
        'Convert string to basic header'

        header_html = self.HEADER_FMT % (level, header, level)
        self.write_to_file(header_html)

    def image(self, path, w='50%', l='50%'):
        'Add image path to html webpage.'

        image_html = self.IMAGE_FMT % (w, path, l)
        #self.write_to_file(image_html)
        return(image_html)

    def list(self, title, items, bullet='ol'):
        'Convert a list into a html list and write to file.'

        self.text(title)
        self.write_to_file('<' + bullet + '>\n')
        for words in items:
            str_html = self.LIST_FMT % (words)
            self.write_to_file(str_html)

        self.write_to_file('</' + bullet + '>\n')

    def to_table_html(self, raw_html, info={}):
        'Convert raw_html to standard table html'

        for key in self.TBL_DEFAULT.keys():
            if not key in info:
                info[key] = self.TBL_DEFAULT[key]

        tbl_html = self.TBL_NAME % (raw_html)
        style_html = self.TBL_STYLESIZE_FMT % (info)
        css_html = self.CSS_STYLE.format(cls=info['class'],
                                         style=style_html,
                                         data=tbl_html)

        if self.DEBUG:
            print css_html

        return(css_html)

    def dataframe_to_table(self, df, info={}):
        'Convert dataframe to table'

        info['height'] = 25 * (df.index.size + 1)
        info['width'] = 50 * (df.columns.size + 1)

        df_html = self.list_to_tablerow(df.columns.tolist(), df.index.name)

        for idx in df.index:
            df_html += self.list_to_tablerow(df.ix[idx].tolist(), idx)

        css_html = self.to_table_html(df_html, info)

        return(css_html)

    def dict_to_table(self, my_dict, tbl_class='', tbl_style=''):
        'Convert a dictionary to a table'

        df = pd.DataFrame([my_dict.values()], columns=my_dict.keys())
        css_html = self.dataframe_to_table(df)

        return(css_html)

    def list_to_tablerow(self, my_list, idx=''):
        'Convert list to a row for html table - in any convert_to_html_table'

        html_str = self.TBL_ITEM % idx

        for name in my_list:
            html_str += self.TBL_ITEM % name

        if self.DEBUG:
            print html_str

        return(self.TBL_ROW % html_str)

    def write_to_file(self, str_html):
        '''
        All HTML formated writing should be done through here.
        '''

        if self.DEBUG:
            print str_html

        self.PAGE.write(str_html)

    def write_page(self):
        'Write Variables to webpage'

        self.page_update = self.page_str % self.page_text

        self.PAGE = open(self.PAGE_NAME, 'w')
        self.PAGE.write(self.page_update)
        self.PAGE.close()


class Summary(WriteHtml):
    '''
    Summary gives an overview of the simulation that was jus ran.  Not to be
    confused with the site homepage.
    '''

    def _set_child_constants(self):
        'Set static variables here'

        self.page_text = {
                          "TITLE": "FFA",
                          'NAME': 'SPORTS ANALYTICS',
                          'SLO_1A': 'Those crazy enough to think they can',
                          'SLO_1B': 'change the world, do',
                          'SEC1_TITLE': 'League Roster',
                          'SEC1_BODY1': 'SET - TO - LEAGUE - ROSTER',
                          'SEC2_TITLE': 'League Teams',
                          'SEC2_BODY1': 'SET - TO - LEAGUE - TEAMS',
                          }
        self.TEMPLATE_NAME = 'summary.html'


class Data(WriteHtml):
    'Data gives an overview of the simulation that was jus ran.'

    def _set_child_constants(self):
        'Set static variables here'

        self.page_text = {
                          "TITLE": "FFA",
                          'NAME': 'SPORTS ANALYTICS',
                          'SLO_1A': 'Those crazy enough to think they can',
                          'SLO_1B': 'change the world, do',
                          'SEC1_TITLE': 'League Roster',
                          'SEC1_BODY1': 'SET - TO - LEAGUE - ROSTER',
                          }

        self.TEMPLATE_NAME = 'data.html'
