'''
Created on Feb 7, 2014

@author: rpatel
'''

import pandas as pd
import numpy as np
import ffa.draft


class PreRank(object):
    '''
    classdocs
    '''

    def __init__(self, info, player_obj):
        '''
        Constructor
        '''

        self.league = info.league
        self.player_obj = player_obj
        self.players = player_obj.players.sort('pts', ascending=False)

        self._setup()

    def _setup(self):

        self.RUN_TO_LEARN = 6
        self.DEFAULT_STRATEGY = 'search'
        self.PLAYER_COL = ['pos', 'name', 'pts', 'preRank']
        self.DRAFT_COL = ['rnd', 'team']
        self.draft = ffa.draft.Simulator(self.league, self.players)

    def get_pre_ranks(self, players=False):
        '''
        Returns optimal pre-ranks for players based off of (1) league settings
        (2) player intial pre-ranks (3) player-projected-points.
        '''

        if not players:
            players = self.players

        # 1. Sort Players and Draft Class for Initial Draft Conditions
        self._set_team_profile_for_pre_rank()
        self._set_summary(players.index)

        for i in np.arange(self.RUN_TO_LEARN):

            # 2. Update Draft Players
            self.draft.players = players

            # 3. Run Draft
            self.draft.live_draft()

            # 4. Update and Sort Players by Draft Results
            players.preRank = self.draft.results.df.pick.order()
            players = players.sort('preRank')

            # 5. Add coloumns to summary-to-save
            new_col = [x + str(i) for x in self.draft.results.SUMMARY_COL]
            self.summary['rnk' + str(i)] = self.draft.results.df['pick']
            self.outcome[new_col] = self.draft.results.get_results()

        # 6. Set league settings back to default
        self.league.team_info = self.team_info_default
        self.players_optimal = players

        self.summary[self.DRAFT_COL] = self.draft.results.df[self.DRAFT_COL]
        self.summary.set_index('name',  inplace=True)

        self.summary.sort('rnk' + str(i), inplace=True)
        self.outcome.sort('rnk' + str(i), inplace=True)

        # 7. Print Results
        print self.summary
        print self.outcome

    def _set_summary(self, summary_index):
        '''
        Set up summary data frame to store pre-rank generator results.
        '''

        self.summary = pd.DataFrame(index=summary_index)
        self.outcome = pd.DataFrame(index=self.league.team_names)
        self.summary[self.PLAYER_COL] = self.players[self.PLAYER_COL]
        self.summary['start'] = np.arange(self.league.num_of_players) + 1

    def _set_team_profile_for_pre_rank(self):
        '''
        Make a copy of league.team_profile and set each player strategy to
        'search' to find player pre-ranks.
        '''

        STRATEGY_TYPE = 'search'
        self.team_info_default = self.league.team_info.copy(deep=True)

        for team in self.league.team_names:
            self.league.team_info[team]['strategy'] = STRATEGY_TYPE
