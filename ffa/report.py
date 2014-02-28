'''
Created on Feb 11, 2014

@author: rpatel
'''

import os
import numpy as np
import shutil
import ffa.big_green_webpage as webpage
import matplotlib.pyplot as plt


class ReportGen(object):
    '''
    Generate Reports in html format for later analysis.  This class should be
    created on the top level and information should be passed into here.

    Each major class (1) PreRank (2) Player Projection (3) InSeason should have
    a special-report method to get internal data in a report-friendly format
    that will be passed to this class.

    Report will create a folder where all files will be saved into this folder.
    The next-project-phase would be to use these report files as a second-level
    database to use as player-default-ranking and more indepth analysis without
    having to rerun all the phase-one abstration layer code.
    '''

    def __init__(self, pages, name='', directory=''):
        '''
        Folder will be created once this class is generated.  Create a new
        class each time another project needs to be created.
        '''

        self.pages = pages
        self.dummy_page = webpage.Data()
        self._set_constants()
        self._set_webpage(name, directory)

    def _set_constants(self):
        '''
        Set intial/default variables.
        '''

        self.DEFAULT_PROJECT_NAME = 'DEFAULT'
        self.DEFAULT_DIRECTORY = r'../../Analysis/'
        self.PLOT_PATH = 'plots/'

    def _set_webpage(self, name, directory):
        '''
        Create project directories and open webpages.
        '''

        # Check if folder names exist
        if not name:
            name = self.DEFAULT_PROJECT_NAME
        if not directory:
            directory = self.DEFAULT_DIRECTORY
        self.path = directory + name + '/'

        # Check and Create HTML Folder
        if os.path.exists(self.path):
            print 'WARNING OVER-WRITING FILES IN DICTORY:\n', self.path
            shutil.rmtree(self.path)
        else:
            print 'Creating new directory:\n', self.path
        shutil.copytree(self.dummy_page.WEB_TEMPLATE + 'standard', self.path)

    def overview_page(self, info):
        'Copy webpage templete to new location'

        data = info['pg_data']
        oPage = webpage.Summary(self.path, info['pg_name'])

        oPage.remap['SBAR1_BODY'] = self.toc_html
        oPage.remap['SEC1_TITLE'] = data['SEC1_TITLE']
        oPage.remap['SEC1_BODY1'] = data['SEC1_BODY1']
        oPage.remap['SEC2_TITLE'] = data['SEC2_TITLE']
        oPage.remap['SEC2_BODY1'] = oPage.df_to_table(data['roster'])
        oPage.remap['SEC3_TITLE'] = data['SEC3_TITLE']
        oPage.remap['SEC3_BODY1'] = oPage.df_to_table(data['team_df'])
        oPage.create_page()

    def player_page(self, info):
        'Copy webpage templete to new location'

        data = info['pg_data']
        oPlayers = data['obj']

        url_path = self.PLOT_PATH + 'players_by_pos.png'
        data['fig_by_pos'].savefig(self.path + url_path)

        oPage = webpage.Data(self.path, info['pg_name'])
        image_html = oPage.IMAGE_FMT.format(w='100%', url=url_path, h='100%')
        SEC2_BODY1 = oPage.df_to_table(data['ovr_body']) + '<br>' + image_html

        oPage.remap['SBAR1_BODY'] = self.toc_html
        oPage.remap['SEC1_TITLE'] = oPlayers.bio['header']
        oPage.remap['SEC1_BODY1'] = oPlayers.bio['msg']
        oPage.remap['SEC2_TITLE'] = data['ovr_title']
        oPage.remap['SEC2_BODY1'] = SEC2_BODY1
        oPage.remap['SEC3_TITLE'] = data['details_title']
        oPage.remap['SEC3_BODY1'] = oPage.df_to_table(data['details_data'])
        oPage.create_page()

    def prerank_result_page(self, info):
        'Update Results Page'

        data = info['pg_data']
        oPage = webpage.Data(self.path, info['pg_name'])

        oPage.remap['SBAR1_BODY'] = self.toc_html
        oPage.remap['SEC1_TITLE'] = 'Projected Team Standings after Draft'
        oPage.remap['SEC1_BODY1'] = oPage.df_to_table(data['outcome'])
        oPage.remap['SEC2_TITLE'] = 'Draft Results After Each Iteration'
        oPage.remap['SEC2_BODY1'] = oPage.df_to_table(data['summary'])
        oPage.create_page()

    def roster_result_page(self, info):
        'Update Results Page'

        data = info['pg_data']
        oPage = webpage.Data(self.path, info['pg_name'])

        # TODO: Clean up roster rank image!
        plt.figure()
        df_plt = data['summary'].convert_objects().dropna().sort('pre')
        df_plt['pre'] = np.arange(len(df_plt)) + 1
        df_plt.plot(x='pre', style='o')
        plt.plot(df_plt['pre'], df_plt['pre'], 'k--')
        plt.tight_layout()
        plt.xlabel('Pre Rank Default')
        plt.ylabel('Pre Rank by League Settings')
        plt.title('Pre Rankings: Custom vs. Default')

        f5 = df_plt.drop('pos', axis=1)
        f5 = f5.set_index('pre')

        for idx in f5.columns:
            f5[idx] = f5[idx] - np.arange(len(f5)) - 1

        f6 = f5.std()
        l_std = [idx + ': STD = ' + str(f6[idx].round(1)) for idx in f6.index]
        plt.legend(l_std, loc='best')
        fig = plt.gcf()
        url_path = self.PLOT_PATH + 'Summary_of_Results.png'
        data['fig_summary'].savefig(self.path + url_path)

        image_html = oPage.IMAGE_FMT.format(w='100%', url=url_path, h='100%')

        data['summary']['pre'] = df_plt['pre']
        SEC2_BODY1 = image_html + '<br>' + oPage.df_to_table(data['summary'])

        oPage.remap['SBAR1_BODY'] = self.toc_html
        oPage.remap['SEC1_TITLE'] = data['SEC1_TITLE']
        oPage.remap['SEC1_BODY1'] = data['SEC1_BODY1']
        oPage.remap['SEC2_TITLE'] = data['SEC2_TITLE']
        oPage.remap['SEC2_BODY1'] = SEC2_BODY1
        oPage.create_page()

    def update_pages(self):
        'Update selected pages'

        toc_dict = {val: val + '.html' for val in self.pages.ix['pg_name']}
        self.toc_html = self.dummy_page.dict_to_list_of_links(toc_dict)

        for col in self.pages.columns:
            page = self.pages[col]

            if page['pg_type'] == 'view':
                self.overview_page(page)
            elif page['pg_type'] == 'ply':
                self.player_page(page)
            elif  page['pg_type'] == 'pre':
                self.prerank_result_page(page)
            elif  page['pg_type'] == 'fin':
                self.roster_result_page(page)
            else:
                raise ValueError('No such page type!!')
