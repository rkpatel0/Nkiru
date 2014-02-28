'''
Module creates copy of Big Green HTML templete for visual data analysis.

Created on Feb 13, 2014

@author: rpatel
'''

import shutil


class WriteHtml(object):
    '''
    All to-html functions will reside here, return code can be directly written
    to file as this class does not store anything.
    '''

    def __init__(self, page_path='', page_name=''):
        'Set all html string formats.'

        # Do not change parent-child order!
        self._set_parent_constants()
        self._set_child_constants()
        self._set_html_format()

        self.page_path = page_path
        self.PAGE_NAME = page_path + page_name + '.html'
        self.TEMPLATE_PATH = self.WEB_TEMPLATE + self.TEMPLATE_NAME

        # Compbine Dictionaries: Don't move or change order: parent + child
        self.remap = dict(self.page_parent.items() + self.page_child.items())

        # Check for dummy page
        if not page_name:
            pass
        else:
            shutil.copy(self.TEMPLATE_PATH, self.PAGE_NAME)
            self.TEMPLAGE_PAGE = open(self.PAGE_NAME, 'r')
            self.page_str = self.TEMPLAGE_PAGE.read()

    def _set_parent_constants(self):
        'Set all HTML default templates here'

        self.DEBUG = False
        self.MAX_TEXT_WIDTH = 600
        self.TBL_ROW_HEIGHT = 28
        self.TBL_ROW_WIDTH = 60

        self.WEB_TEMPLATE = r'../../References/HtmlTemplates/BigGreen/'
        SLOGAN = ('Those <strong>crazy</strong> enough to think they can<br>'
                 '<strong>change</strong> the world, <strong>do</strong>')

        self.page_parent = {
                            'TITLE': 'FFA',
                            'NAME': 'Fantasy Sports Analytics',
                            'SBAR1_BODY': 'Fill-in once # of webpages are known',
                            'SEC1_TITLE': '',
                            'SEC1_BODY1': '',
                            'SEC2_TITLE': '',
                            'SEC2_BODY1': '',
                            'SEC3_TITLE': '',
                            'SEC3_BODY1': '',
                            'SBAR1_TITLE': 'Main Menu',
                            'SBAR1_BODY': '',
                            'SBAR2_TITLE': 'Football 2014',
                            'SBAR2_BODY': 'How will you do this season?',
                            'SLOGAN': SLOGAN,
                            'HOME': 'overview.html',
                            'BLOG': 'overview.html',
                            'SERVICES': 'overview.html',
                            'CONTACT': 'overview.html',
                            'RESOURCES': 'overview.html',
                            'PARTNERS': 'overview.html',
                            'ABOUT': 'overview.html',
                            }

    def _set_html_format(self):
        'Static HTML Big-Green Fromat'

        self.IMAGE_FMT = "<img width={w} src={url} height={h}/>"
        self.LINK_FMT = "<a href={url}>{name}</a>"
        self.TBL_STYLESIZE_FMT = 'width:%(width)spx;height:%(height)spx;'

        self.BREAK_FMT = '<br>'
        self.HEADER_FMT = "<h%s>%s</h%s>\n"
        self.HTML_FMT = '<{name}>%s</{name}>\n'
        self.TBL_IDX = self.HTML_FMT.format(name='th')
        self.TBL_ITEM = self.HTML_FMT.format(name='td')
        self.TBL_ROW = self.HTML_FMT.format(name='tr')
        self.TBL_NAME = self.HTML_FMT.format(name='table')
        self.TEXT_FMT = self.HTML_FMT.format(name='p')
        self.LIST_FMT = self.HTML_FMT.format(name='li')

        self.TBL_DEFAULT = {
                            'class': 'tableone',
                            'width': 100,
                            'height': 50,
                            }

        self.CSS_STYLE = '<div class="{cls}" style="{style}">\n{data}</div>\n'

    def text(self, text):
        'Convert basic test to html format'

        text_html = self.TEXT_FMT % (text)
        return(text_html)

    def link(self, url, name='Click Here'):
        'Convert name to a url link'

        link_html = self.LINK_FMT % (url, name)
        return(link_html)

    def header(self, header, level=2):
        'Convert string to basic header'

        header_html = self.HEADER_FMT % (level, header, level)
        return(header_html)

    def image(self, path, w='50%', l='50%'):
        'Add image path to html webpage.'

        image_html = self.IMAGE_FMT % (w, path, l)
        return(image_html)

    def to_list(self, items):
        'Convert a list into a html list'

        str_html = ''
        for words in items:
            str_html += self.LIST_FMT % (words)

        return(str_html)

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
        return(css_html + '<br>')

    def df_to_table(self, df, info={}):
        'Convert dataframe to table'

        info['height'] = self.TBL_ROW_HEIGHT * (df.index.size + 1)
        width = self.TBL_ROW_WIDTH * (df.columns.size + 2)

        if width > self.MAX_TEXT_WIDTH:
            width = self.MAX_TEXT_WIDTH
        info['width'] = width

        df_html = self.list_to_tablerow(df.columns.tolist(), df.index.name)

        for idx in df.index:
            df_html += self.list_to_tablerow(df.ix[idx].tolist(), idx)

        css_html = self.to_table_html(df_html, info)

        return(css_html)

    def list_to_tablerow(self, my_list, idx=''):
        'Convert list to a row for html table - in any convert_to_html_table'

        html_str = self.TBL_ITEM % idx

        for name in my_list:
            html_str += self.TBL_ITEM % name

        return(self.TBL_ROW % html_str)

    def dict_to_list_of_links(self, my_dict):
        'Convert dictionary of pages to a list of links'

        list_html = ''
        for name in my_dict.keys():
            link = self.LINK_FMT.format(url=my_dict[name], name=name)
            list_html += self.LIST_FMT % link

        return(self.HTML_FMT.format(name='ul') % list_html)

    def create_page(self):
        'Write to webpage'

        self.page_update = self.page_str % self.remap

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

        self.page_child = {
                          }

        self.TEMPLATE_NAME = 'overview.html'


class Data(WriteHtml):
    'Data gives an overview of the simulation that was jus ran.'

    def _set_child_constants(self):
        'Set static variables here'

        self.page_child = {
                          }

        self.TEMPLATE_NAME = 'data.html'
