'''
Created on Feb 11, 2014

@author: rpatel
'''

import os
import pandas as pd
import shutil
import ffa.big_green_webpage as webpage


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

    def __init__(self, info, players, results, name='', directory=''):
        '''
        Folder will be created once this class is generated.  Create a new
        class each time another project needs to be created.
        '''

        # RKP: Sister Projects ?
        # That need two top level folders but share low level files
        self.league = info.league
        self.profile = info.profile
        self.players = players
        self.results = results

        self._set_constants()
        self.set_webpage(name, directory)

    def _set_constants(self):
        '''
        Set intial/default variables.
        '''

        self.page_names = {
                           'sum': 'summary.html',
                           'ply': 'players.html',
                           'res': 'results.html',
                           }

        self.WEB_TEMPLATE = r'../../References/HtmlTemplates/BigGreen/'
        self.DEFAULT_DIRECTORY = r'../../Analysis/'
        self.DEFAULT_PROJECT_NAME = 'DEFAULT'

    def save_league_summary(self, league):
        '''
        Create TOC and League Summary Page.
        '''

        # TODO: (1) Author (2) Date (3) TOC
        pass

    def set_webpage(self, name, directory):
        '''
        Create project directories and open webpages.
        '''

        # Check if folder names exist
        if not name:
            name = self.DEFAULT_PROJECT_NAME

        if not directory:
            directory = self.DEFAULT_DIRECTORY

        if not name[-1] == '/':
            name = name + '/'
        self.path = directory + name

        # Create Report Directory
        if os.path.exists(self.path):
            print 'WARNING OVER-WRITING FILES IN DICTORY:\n', self.path
        else:
            print 'Creating new directory:\n', self.path
            shutil.copytree(self.WEB_TEMPLATE + 'standard', self.path)

        self.SUM_WEB = webpage.Summary(self.path, self.page_names['sum'])
        self.PLY_WEB = webpage.Data(self.path, self.page_names['ply'])
        self.RES_WEB = webpage.Data(self.path, self.page_names['res'])

    def update_summary_page(self):
        'Copy webpage templete to new location'

        self.SUM_WEB.page_text['SEC1_BODY1'] = \
        self.SUM_WEB.dict_to_table(self.league.roster)
        self.SUM_WEB.page_text['SEC2_BODY1'] = \
        self.SUM_WEB.dataframe_to_table(pd.DataFrame(self.league.team_info))

    def update_players_page(self):
        'Copy webpage templete to new location'

        self.PLY_WEB.page_text['SEC1_TITLE'] = 'Player List'
        self.PLY_WEB.page_text['SEC1_BODY1'] = \
        self.PLY_WEB.dataframe_to_table(self.players)

    def update_results_page(self):
        'Update Results Page'

        res_df_disp = self.results.summary
        #res_df_disp.set_index('name', inplace=True)

        self.RES_WEB.page_text['SEC1_TITLE'] = 'Draft Results'
        self.RES_WEB.page_text['SEC1_BODY1'] = \
        self.RES_WEB.dataframe_to_table(res_df_disp)

    def update_pages(self):
        'Update selected pages'

        self.update_summary_page()
        self.update_players_page()
        self.update_results_page()

    def close_pages(self):
        '''
        Close pages and any other on-exit actions.
        '''

        self.SUM_WEB.write_page()
        self.PLY_WEB.write_page()
        self.RES_WEB.write_page()


