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

    def __init__(self, info, results, name='', directory=''):
        '''
        Folder will be created once this class is generated.  Create a new
        class each time another project needs to be created.
        '''

        # RKP: Sister Projects ?
        # That need two top level folders but share low level files
        self.league = info.league
        self.profile = info.profile
        self.players = results.player_obj
        self.results = results

        self._set_constants()
        self.set_webpage(name, directory)

    def _set_constants(self):
        '''
        Set intial/default variables.
        '''

        self.page_names = {
                           'Summary': 'summary.html',
                           'Players': 'players.html',
                           'Results': 'results.html',
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
        self.plot_path = self.path + 'plots/'

        # Create Report Directory
        if os.path.exists(self.path):
            print 'WARNING OVER-WRITING FILES IN DICTORY:\n', self.path
            shutil.rmtree(self.path)
        else:
            print 'Creating new directory:\n', self.path

        shutil.copytree(self.WEB_TEMPLATE + 'standard', self.path)

        self.SUM_WEB = webpage.Summary(self.path, self.page_names['Summary'])
        self.PLY_WEB = webpage.Data(self.path, self.page_names['Players'])
        self.RES_WEB = webpage.Data(self.path, self.page_names['Results'])

    def update_summary_page(self):
        'Copy webpage templete to new location'

        self.SUM_WEB.page_text['SEC1_TITLE'] = 'League Roster'
        self.SUM_WEB.page_text['SEC1_BODY1'] = \
        self.SUM_WEB.dict_to_table(self.league.roster)
        self.SUM_WEB.page_text['SEC2_TITLE'] = 'Team Summary',
        self.SUM_WEB.page_text['SEC2_BODY1'] = \
        self.SUM_WEB.dataframe_to_table(pd.DataFrame(self.league.team_info))
        self.SUM_WEB.page_text['TOC_LIST'] = \
        self.link_list_of_pages()

    def link_list_of_pages(self):
        'Convert dictionary of pages to a list of links'

        list_html = ''
        for name in self.page_names:
            link = self.SUM_WEB.LINK_FMT.format(url=self.page_names[name],
                                                name=name)
            list_html += self.SUM_WEB.LIST_FMT % link

        return(self.SUM_WEB.HTML_FMT.format(name='ul') % list_html)

    def update_players_page(self):
        'Copy webpage templete to new location'

        self.PLY_WEB.page_text['SEC1_TITLE'] = 'Player List'
        self.PLY_WEB.page_text['SEC1_BODY1'] = \
        self.PLY_WEB.dataframe_to_table(self.players.players.set_index('name'))
        self.PLY_WEB.page_text['TOC_LIST'] = \
        self.SUM_WEB.page_text['TOC_LIST']

        # Generate and Save Image + Add URL
        url = self.plot_path + 'players_by_pos.png'
        self.players.plot_position_points(url)
        self.PLY_WEB.page_text['OPT_IMG1'] = \
        self.PLY_WEB.IMAGE_FMT.format(width='100%', url=url, height='100%')

    def update_results_page(self):
        'Update Results Page'

        self.RES_WEB.page_text['SEC1_TITLE'] = 'Draft Results'
        self.RES_WEB.page_text['SEC1_BODY1'] = \
        self.RES_WEB.dataframe_to_table(self.results.summary)
        self.RES_WEB.page_text['TOC_LIST'] = \
        self.SUM_WEB.page_text['TOC_LIST']

    def update_pages(self):
        'Update selected pages'

        # Do not change this order!!!
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


