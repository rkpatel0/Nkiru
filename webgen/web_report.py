'''
Created on Mar 22, 2014

@author: rpatel
'''

import webgen.html_converter
import os
import numpy as np
import shutil
import matplotlib.pyplot as plt


class ReportGen(object):
    '''
    Parent Class used to Convert Dict of DataFrames to webpages.  Either use as
    a generic Webpage Templete or as a parent class for a specific template.

    Format:
    pages_dict = { url     tyoe  title data  text
                   name1 : FIG   plot  oFig  description
                   Table : DATA  Blah  DF    description
                   Text  : PARA  Intro False text
                  }
    '''

    def __init__(self):
        ''
        self.oHtml = webgen.html_converter.ToHtml()

        self.save_path = r'../../Analysis/'
        self.PLOT_DIR = 'plots/'

    def toc_links(self, names):
        'Convert list of list/series to url'

        # TODO: Fix format when running
        toc = []
        for name in names:
            name = name.replace(' ', '_')
            toc.append(self.oHtml.LINK_FMT(url=name + '.html', name=name))

        toc_html = self.oHtml._to_html_list(toc)
        return toc_html

    def _make_dir(self, name='default'):
        'Make Project Directory'

        self.path = self.save_path + name + '/'

        # Check and Create HTML Folder
        if os.path.exists(self.path):
            print 'WARNING OVER-WRITING FILES IN DICTORY:\n', self.path
            shutil.rmtree(self.path)
        else:
            print 'Creating new directory:\n', self.path

        #os.mkdir(self.path)
        #shutil.copytree(self.dummy_page.WEB_TEMPLATE + 'standard', self.path)
        oPage = BigGreen(path=self.path)
        oPage.copy_content()

    def web_report(self, pages, name='tmp'):
        'Convert DDF (dict of DFs) to individual pages'

        # TODO: replace ' ' with '_' first (messy the way I do it)
        page_names = pages['name'].unique()
        self._make_dir(name)

        # Create a TOC of Links
        toc_html = self.toc_links(page_names)
        for name in page_names:
            self.webpage(pages[pages['name'] == name], toc_html)

    def webpage(self, info, toc):
        '''
        Convert DataFrame where each row contains a block decription into body.
        Read WebPage Template and save converted block data as new webpage.

        Idea is that each page follows the same template but can be brokwn down
        into sublocks with a much higher degree of flexibility.
        '''

        # Convert DataFrame rows to Body of HTML Page
        body_html = ''
        for idx in info.index:
            row = info.ix[idx]
            if row['type'] == 'FIG':
                body = self._figure_block(row)
            elif row['type'] == 'DATA':
                body = self._data_block(row)
            elif row['type'] == 'TEXT':
                body = self._text_block(row)
            else:
                raise KeyError('Page Type Unknown!')
            body_html += self.oHtml.HEAD_TP1(title=row['title'], body=body)

        content = {'MAIN_BODY': body_html, 'SBAR1_BODY': toc}
        oPage = BigGreen(path=self.path, name=info['name'].iloc[0])
        oPage.create_page(content)

    def _figure_block(self, info):
        'Save Image and Convert Path to htnl code'

        # Save Image to Desired Path
        title = info['title'].replace(' ', '_')
        title = title.replace('.', '_')
        save_path = self.path + self.PLOT_DIR + title + '.png'
        info['data'].savefig(save_path)

        return self.oHtml.IMAGE_FMT(w='100%', url=save_path, h='100%')

    def _data_block(self, info):
        'Convert dataframe into html table'

        return self.oHtml.df_to_html(info['data'])

    def _text_block(self, info):
        'Convert text to HTML paragraph'

        return self.oHtml.PRGH_FMT % info['data']


class WebPage(object):
    'Generic Webpage Class'

    def __init__(self, path, name=''):
        '''
        Constructor
        '''
        self.SAVE_PATH = path
        self.PAGE_NAME = name.replace(' ', '_')

        self._load_defaults()

    def _load_defaults(self):
        'This function gets overloaded by child. - careful'

        self.content = {}

    def create_page(self, content={}):
        'Merge data into page dict, open template, write, and save'

        for key in self.content.keys():
            if key not in content:
                content[key] = self.content[key]

        TEMPLATE_HTML = self._get_template()
        html = TEMPLATE_HTML % content
        self._save_page(html)

    def _save_page(self, html):
        'Save page to desired path'

        name = self.PAGE_NAME.replace(' ', '_')
        PAGE = open(self.SAVE_PATH + name + '.html', 'w')
        PAGE.write(html)
        PAGE.close()

    def _get_template(self):
        'Get HTML raw content'

        TEMPLATE = open(self.WEB_TEMPLATE + self.TEMPLATE_NAME, 'r')
        html = TEMPLATE.read()
        TEMPLATE.close()

        return html

    def copy_content(self):
        'Copy webpage files - images, css, etc'

        shutil.copytree(self.WEB_TEMPLATE + 'standard', self.SAVE_PATH)


class BigGreen(WebPage):
    '''
    Child Class of ReportGen.  Use to save DDF (Dictionary Data Frame) as a
    webpage with BigGreen Template.
    '''

    def _load_defaults(self):
        'Set Defaults for where files should be found.'

        self.DEBUG = False

        self.WEB_TEMPLATE = r'../../References/HtmlTemplates/BigGreen/'
        self.TEMPLATE_NAME = 'standard.html'

        self.MAX_TEXT_WIDTH = 600
        self.TBL_ROW_HEIGHT = 28
        self.TBL_ROW_WIDTH = 60

        SLOGAN = ('Those <strong>crazy</strong> enough to think they can<br>'
                 '<strong>change</strong> the world, <strong>do</strong>')

        self.content = {
                        'TITLE': 'FFA',
                        'NAME': 'Fantasy Sports Analytics',
                        'MAIN_BODY': '',
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
