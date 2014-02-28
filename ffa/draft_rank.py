'''
Created on Feb 7, 2014

@author: rpatel
'''

import pandas as pd
import numpy as np
import ffa.draft
import ffa.report
import matplotlib.pyplot as plt


class PreRank(object):
    '''
    classdocs
    '''

    def __init__(self, oLeague, oPlayers):
        '''
        Constructor
        '''

        self.oLeague = oLeague
        self.oPlayers = oPlayers

        self._setup()

    def _setup(self):

        self.RUN_TO_LEARN = 6   # Max for webpage = 8
        self.DEFAULT_STRATEGY = 'search'
        self.PLAYER_COL = ['pos', 'name', 'pts', 'pre']  # Player Cols to Keep
        self.DRAFT_COL = ['rnd', 'team']                 # Draft Cols to keep

    def generate_preranks(self):
        '''
        Returns optimal pre-ranks for players based off of (1) league settings
        (2) player intial pre-ranks (3) player-projected-points.
        '''

        players = self.oPlayers.df.sort('pts', ascending=False)
        self.oDraft = ffa.draft.Simulator(self.oLeague, players)

        # 1. Sort Players and Draft Class for Initial Draft Conditions
        self._set_team_strategy()
        self._setup_result_df(players)

        for i in np.arange(self.RUN_TO_LEARN):

            # 2. Update Draft Players
            self.oDraft.players = players

            # 3. Run Draft
            self.oDraft.live_draft()

            # 4. Update and Sort Players by Draft Results
            players.pre = self.oDraft.oResults.df.pick.order()
            players = players.sort('pre')

            # 5. Add coloumns to summary-to-save
            new_col = [x + str(i) for x in self.oDraft.oResults.SUMMARY_COL]
            self.summary['rnk' + str(i)] = self.oDraft.oResults.df['pick']
            self.outcome[new_col] = self.oDraft.oResults.summarize()

        # 6. Set league settings back to default
        self.players_optimal = players
        self._save_preranks('rnk' + str(i))

    def _save_preranks(self, FINAL_IDX):
        ' Save preranks to easy-to-use format for higher-level functions'

        self.oLeague.team_info = self.team_info_default

        self.summary[self.DRAFT_COL] = self.oDraft.oResults.df[self.DRAFT_COL]
        self.summary.set_index('name',  inplace=True)

        self.summary.sort(FINAL_IDX, inplace=True)
        self.outcome.sort(FINAL_IDX, inplace=True)
        self.results = {
                        'final': self.summary[FINAL_IDX],
                        'summary': self.summary.dropna(),
                        'outcome': self.outcome.dropna(),
                        }

    def _setup_result_df(self, players):
        'Set up summary data frame to store pre-rank generator results.'

        self.summary = pd.DataFrame(index=players.index)
        self.summary[self.PLAYER_COL] = players[self.PLAYER_COL]
        self.summary['start'] = np.arange(len(self.summary.index)) + 1

        self.outcome = pd.DataFrame(index=self.oLeague.team_names)
        self.outcome.index.name = 'Team'

    def _set_team_strategy(self):
        '''
        Make a copy of league.team_profile and set each player strategy to
        'search' to find player pre-ranks.
        '''

        STRATEGY_TYPE = 'search'
        self.team_info_default = self.oLeague.team_info.copy(deep=True)

        for team in self.oLeague.team_names:
            self.oLeague.team_info[team]['strategy'] = STRATEGY_TYPE


class RunRanks(object):
    'Run any PreRank Tests here if they are to be saved'

    def __init__(self, state, oPlayers):

        self.state = state
        self.oLeague = state.oLeague
        self.oPlayers = oPlayers

        self._load_constants()

    def _load_constants(self):
        'Load Constants from here'

        self.PAGES_INDEX = ['pg_name', 'pg_type', 'pg_data']

        self.FINAL_MSG = (
        'Below is a list of the optimal preranking for each league setting. '
        'Depending on what parameters are being compared you should be able '
        'see the difference in pre-rankings across each league.  Evening '
        'minor changes like 2 WR + 3 RB vs. 3 WR + 2 RB can have major a '
        'signficant impact of prerankings.<br><br>'
        'One other thing that has a major impact on prerankings are player '
        'point totals.  Whether that be players (1) from previous years, (2) '
        'simulated players - exponential vs. linear or (3) projected players. '
        'It is quiet important how to players drop off (slope) relaitve to '
        'one another.  Many projects use a very basic linear approximation '
        'which are great for basic rankings but much of the signal gets lost '
        'in the noise.<br>')

        self.HOW_IT_WORKS_MSG = (
        'The idea here is to compare the dependency of league settings on '
        'pre-ranks.  Essentially, why league settings are very important in '
        'ranking players.  There are a few people out there who have really '
        'understood this and even less who have actually written about this. '
        'The general concensus amoung this group is that players should be '
        'drated off of the cost they would pay to get the next-best-player at '
        'that position on their next turn.  For example if you were deciding '
        'between a RB and QB, then we have two options: (1) RB0 + QB1 or (2) '
        'QB0 + RB1.  The Net Cost = RB0 + QB1 - QB0 - RB1 where the polarity '
        'of the cost would indicate whom should be drafted first. This is '
        'called value based drafting (VBD).<br><br>'
        'While this philosophy is 100% correct, here we would like to answer '
        'the bigger question, How does one measure this cost iterativily '
        'throughout a draft?  What about default pre-rankgs? Here we have '
        'developed a very new way of deriving these optimal preranks.  The '
        'basic idea is to run search algorithms across each draft option for '
        'each team at their given turn in the draft and using machine '
        'learning techniques adapt or iteratively converge on the most '
        'optimal preranks. <br><br>'
        'This unique technique blends many of the latest cutting edge '
        'techniques from artificial intelligence and signal processing to '
        'give you a customized pre-ranks that is custom catered to fit your '
        'league. We hope that this helps give you an edge in your league as '
        'well as shed some light on the significance on league settings on '
        'pre-rankings and why the two are dependent on each other.')

    def _create_webpage_content(self, rost={}, pps={}):
        '''
        Convert Results info dictionary format to be displayed in webpages.
        To use the default (current) league settings do not pass a data frame.
        Otherwise pass in dataframes that are to be displayed

        This will get messy went we want to compare pps or different equations.
        '''

        # TODO: Need to check if pps is custom or database!
        if not rost:
            self.rost_df = pd.DataFrame(self.oLeague.roster, index=['Run'])
        else:
            self.rost_df = pd.DataFrame.from_dict(rost, orient='index')
            idx = ['LG' + str(i) for i in np.arange(self.rost_df.columns.size)]
            self.rost_df.columns = idx

        self.rost_df.index.name = 'Position'

        if not pps:
            self.pps_df = self.oPlayers.bio['data']
        else:
            self.pps_df = pd.DataFrame.from_dict(pps, orient='index')
            idx = ['LG' + str(i) for i in np.arange(self.pps_df.columns.size)]
            self.pps_df.columns = idx

        self.pps_df.index.name = 'Points'

        # Must do before ploting players
        self.oLeague.setup({'roster': self.rost_df.max(axis=1).to_dict()})
        # TODO: Add something for which stats to look at players or save all...

        self.ovrDict = {
                        'SEC1_TITLE': 'How it Works',
                        'SEC1_BODY1': self.HOW_IT_WORKS_MSG,
                        'SEC2_TITLE': 'League Roster(s)',
                        'SEC3_TITLE': 'Teams in League',
                        'roster': self.rost_df,
                        'team_df': self.oLeague.team_info,
                        }

        self.plyDict = {
                        'ovr_title': 'Player Overview',
                        'ovr_body': self.pps_df,
                        'details_title': 'Players Available to Draft',
                        'details_data': self.oPlayers.df.set_index('name'),
                        'obj': self.oPlayers,
                        'fig_by_pos': self.oPlayers.plot_position_points(),
                        }

        self.sumDict = {
                        'SEC1_TITLE': 'Projected Team Standings after Draft',
                        'SEC1_BODY1': self.FINAL_MSG,
                        'SEC2_TITLE': 'Player Pre Rank vs. League Settings'
                        }

    def pre_rank_page(self, page_name='PreRankCompare'):

        # 1. Run Simulation
        oSimulate = PreRank(self.oLeague, self.oPlayers)
        oSimulate.generate_preranks()

        # 2. Document results as webpage
        self._create_webpage_content()
        self.pages = pd.DataFrame(index=self.PAGES_INDEX)
        self.pages['brief'] = ['Overview', 'view', self.ovrDict]
        self.pages['ply'] = ['Player',  'ply', self.plyDict]
        self.pages['res'] = ['Results', 'pre', oSimulate.results]

        # 3, Document Results
        report = ffa.report.ReportGen(self.pages, page_name)
        report.update_pages()

    def roster_rank_page_tmp(self, page_name='TMP'):

        # 1. Set Roster Sweep Range
        roster = {
                  'QB': [0, 1, 0, 1],
                  'RB': [0, 0, 0, 0],
                  'WR': [0, 0, 0, 1],
                  'TE': [2, 1, 2, 0],
                  }
        self._create_webpage_content(roster)

        # 2. Create Simulator + Final_RanKDF w. index of ALL possible players
        oSimulate = PreRank(self.oLeague, self.oPlayers)
        self.oLeague.setup({'roster': self.rost_df.max(axis=1).to_dict()})
        self.oPlayers.set_to_draft()
        self.final = pd.DataFrame(index=self.oPlayers.df.name)

        # 3. Create Webpage and Data to Display
        self.pages = pd.DataFrame(index=self.PAGES_INDEX)
        self.pages['brief'] = ['Overview', 'view', self.ovrDict]
        self.pages['ply'] = ['Player',  'ply', self.plyDict]

        # 4. Sweep League Roster [update players based on league roster]
        for col in self.rost_df:
            self.oLeague.setup({'roster': self.rost_df[col].to_dict()})
            self.oPlayers.set_to_draft()
            oSimulate.generate_preranks()
            self.pages[col] = ['Results_' + col, 'pre', oSimulate.results]
            self.final[col] = oSimulate.results['final']

        # 5. Document Results
        self.document_results()

        # 6. Generate Report
        report = ffa.report.ReportGen(self.pages, page_name)
        report.update_pages()

    def document_results(self):
        'Generate a plot summarizing Sweep results'

        # Save Results Figure
        df_plt = self.final.convert_objects().dropna().sort('pre')
        df_plt['pre'] = np.arange(len(df_plt)) + 1
        df_plt = df_plt.set_index('pre')
        df_plt = df_plt.drop('pos', axis=1)

        # Get STD for Legend
        dtmp = df_plt.copy()
        for idx in dtmp.columns:
            dtmp[idx] = dtmp[idx] - np.arange(len(dtmp)) - 1

        dtmp = dtmp.std()
        l_std = [idx + ' SD: ' + str(dtmp[idx].round(1)) for idx in dtmp.index]

        plt.figure()
        df_plt.plot(style='o')
        plt.plot(df_plt.index, df_plt.index, 'k--')
        plt.tight_layout()
        plt.xlabel('Pre Rank Default')
        plt.ylabel('Pre Rank by League Settings')
        plt.title('Pre Rankings: Custom vs. Default')
        plt.legend(l_std, loc='best')

        self.sumDict['fig_summary'] = plt.gcf()
        self.sumDict['summary'] = self.final.sort('pre')
        self.pages['fin'] = ['Summary',  'fin', self.sumDict]

    def roster_rank_page(self, page_name='RST'):

        roster = {
          'QB': [1, 2, 1, 1],
          'RB': [3, 2, 3, 2],
          'WR': [3, 2, 2, 3],
          'TE': [1, 2, 2, 2],
          }

        self._create_webpage_content(rost=roster)
        self.sweep_rank_page('roster', self.rost_df, page_name)

    def pps_rank_page(self, page_name='RST'):

        points = {
                  'passYds': [0.0250, 0.0250, 0.0250, 0.0250, 0.0250],
                  'passTDs': [4.0000, 4.0000, 4.0000, 4.0000, 4.0000],
                  'int':     [-2.000, -2.000, -2.000, -2.000, -2.000],
                  'rushYds': [0.1000, 0.1000, 0.1000, 0.1000, 0.1000],
                  'rushTDs': [5.0000, 5.0000, 5.0000, 5.0000, 5.0000],
                  'recCmp':  [0.0000, 0.2500, 0.5000, 0.7500, 1.0000],
                  'recYds':  [0.0625, 0.0625, 0.0625, 0.0625, 0.0625],
                  'recTDs':  [5.0000, 5.0000, 5.0000, 5.0000, 5.0000],
                  'fumL':    [-2.000, -2.000, -2.000, -2.000, -2.000],
                  }

        self._create_webpage_content(pps=points)
        self.sweep_rank_page('stat_pts', self.pps_df, page_name)

    def sweep_rank_page(self, league_key, df, page_name):

        FIN_SAVE = ['pos', 'pre']

        # 2. Create Simulator + Final_RanKDF w. index of ALL possible players
        oSimulate = PreRank(self.oLeague, self.oPlayers)
        self.oPlayers.set_to_draft()
        self.final = pd.DataFrame(index=self.oPlayers.df.name)
        self.final[FIN_SAVE] = self.oPlayers.df.set_index('name')[FIN_SAVE]

        # 3. Create Webpage and Data to Display
        self.pages = pd.DataFrame(index=self.PAGES_INDEX)
        self.pages['brief'] = ['Overview', 'view', self.ovrDict]
        self.pages['ply'] = ['Player',  'ply', self.plyDict]

        # 4. Sweep League Roster [update players based on league roster]
        for col in df:
            self.oLeague.setup({league_key: df[col].to_dict()})
            self.oPlayers.set_to_draft()
            oSimulate.generate_preranks()
            self.pages[col] = ['Results_' + col, 'pre', oSimulate.results]
            self.final[col] = oSimulate.results['final']

        # 6. Generate Report
        self.document_results()
        report = ffa.report.ReportGen(self.pages, page_name)
        report.update_pages()
