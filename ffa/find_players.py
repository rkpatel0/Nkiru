'''
Player Generation - Grab, manipluate players from database or create custom
==============================================================================

Created on Jan 29, 2014
@author: rpatel

'''

import pandas as pd
import numpy as np
import os.path

PLAYER_DEFAULT = {}
PLAYER_DEFAULT['fant_col'] = ['name', 'pos', 'preRank', 'pts']


class SetPlayers(object):
    '''
    Top level (wrapper) class to define different types of players. Must pass
    the 'info' object (1) league (2) player settings to set player generation.

    This should be the only class required to grab players.

    TODO: Work on a clean/simple UI for setting (1) DataBase (2) Articial
          palyers up.
    '''

    def __init__(self, info):
        '''
        Pass object to setup Arificial and Database player generator.  Even if
        both are not being used both need to be set up.  Using 'info' default
        settings will be passed so one need not directly initialize explicity.

        '''

        self.info = info
        self.custom = Artificial(info.league, info.profile.player_custom)
        self.past = Database(info.league, info.profile.player_database)

    def get_customDraft(self):
        '''
        Returns custom-defined players as defined in league and profile objects

        '''

        self.players = self.custom._getPlayersDraft()

        return(self.players)

    def get_databaseDraft(self):
        '''
        Returns player from database for draft as defined in league and profile
        '''

        self.players = self.past._getPlayersDraft()

        return(self.players)

    def plotPlayerStats(self, columns=[], players=pd.DataFrame()):
        '''
        Plot specified columns for player dataframe.
        '''

        pass


class Artificial:
    '''
    Create custom defined players by passing slopes and offet.  Can create
    players with (1) polynomial decay (2) exponential decay.


    '''

    def __init__(self, league, profile_coeff):
        '''
        Set class on initialziation for simple one-time-use or use setup to
        reset object for grabbing differnt player profiles.

        Remember:
        If you modify league settings you modify player profile info.  This is
        the recommended way to update player profile to grab a different
        player profile.

        '''

        self.league = league
        self.profile_coeff = profile_coeff
        self._setup()

    def _setup(self):
        '''
        Set general class initial conditions.
        '''

        global PLAYER_DEFAULT

    def _getPlayersDraft(self):
        '''
        Return a data frame with structure designed for draft-specific needs.
        '''

        players = pd.DataFrame(columns=PLAYER_DEFAULT['fant_col'],
                               index=np.arange(self.league.num_of_players))

        idx = 0
        for pos in self.league.roster.keys():

            num_of_pos = self.league.roster[pos] * self.league.num_of_teams
            pts_by_pos = self._get_points(num_of_pos, self.profile_coeff[pos])

            for j, pts in enumerate(pts_by_pos):

                name = pos + str(j)
                                # [name, pos, rank, pts]
                players.ix[idx] = [name, pos, idx, pts]
                idx += 1

            players = players.set_index('name', drop=False)
            players.index.name = 'id'

        return(players)

    def _get_points(self, num_of_pos, coeff):
        '''
        Returns a numpy array of pts as specified by profile-player-settings.
        '''

        arr_of_pos = np.arange(num_of_pos)

        if coeff[-1] == 'poly':
            points = self._get_points_poly(arr_of_pos, coeff[:-1])

        elif coeff[-1] == 'exp':
            points = self._get_points_exp(arr_of_pos, coeff[:-1])

        else:
            print 'You entered an invalid custom player equation type!\n'

        return(points)

    def _get_points_exp(self, arr, coeff):

        '''
        Returns array with an exponential decay. Provide array 'arr' and exp
        coefficients 'coeff'.

        Equation:
        pts = exp(-m2 * x + m1) + m0'
        m0' = m0 - exp(m1)

        Note:
        Player drop-off most fits an exp decay.  This will be the most eligant
        way to evaluate artificial player performance.

        Careful with Log Fitting:
        (1) random noise and (2) amplification at high values (3) matlab code

        '''

        pts = np.exp(-coeff[2] * arr + coeff[1]) + coeff[0] - np.exp(coeff[1])

        return(pts)

    def _get_points_poly(self, arr, coeff):
        '''
        Returns array with a polynomial decay. Provide array 'arr' and
        polynomial coeff'.

        Equation:
        pts = m2 * x^2 + m1 * x + m0
        '''

        pts = coeff[2] * arr * arr + coeff[1] * arr + coeff[0]

        return(pts)


class Database:
    '''
    Get player stats (or points) as defined settings.  Either return players
    for fantasy specific purposes or projections.

    Use info.league and info.settings to define desired database player stats.
    '''

    def __init__(self, league, settings):
        '''
        Always pass settings on initializtion, then use those objects to define
        desired player stats.
        '''

        self.league = league
        self.settings = settings
        self._setup()

    def _setup(self):
        '''
        Set general class initial conditions.
        '''

        global PLAYER_DEFAULT

        # RKP: Is this really the final structure for stat-pts??
        self.stat_col = [
                         'preRank', 'name', 'team', 'age', 'GP', 'GS',
                         'passCmp', 'passAtt', 'passYds', 'passTDs', 'int',
                         'rushAtt', 'rushYds', 'rushAvg', 'rushTDs', 'recCmp',
                         'recYds', 'recAvg', 'recTDs', 'fumL', 'pos', 'VBD',
                         'pts',
                         ]

    def _getPlayerStats(self):
        '''
        Return player stats for (1) projection class or (2) draft pts
        - Careful about post processing here - impacts pts + draft classes
        '''

        stats = self._getStatsRaw()
        stats = self._cleanStats(stats)

        return(stats)

    def _getPlayersDraft(self):

        '''
        Returns player dataframe for drafted-related analysis
        '''
        stats = self._getPlayerStats()
        players = self._get_fantasy_points(stats)

        return(players)

    def _get_fantasy_points(self, stats):
        '''
        Return dataframe new data frame that:
            (1) computets points form stats
            (2) converts stats frame to draft frame
        '''

        for category in self.league.pts_per_stat.keys():
            stats.pts += (self.league.pts_per_stat[category] * stats[category])

        stats.sort(columns='pts', ascending=False, inplace=True)
        players = pd.DataFrame(columns=PLAYER_DEFAULT['fant_col'])

        # Remove excess players at each position + keep only draft categories
        for pos in self.league.positions:
            num = self.league.roster[pos] * self.league.num_of_teams
            keep = stats[PLAYER_DEFAULT['fant_col']][stats.pos == pos][:num]

            # TODO: Raise exception here instead...
            if len(keep) < num:
                print 'ERROR NUMBER OF PLAYERS AT POS ARE NOT ENOUGHH!!!!'
            else:
                players = players.append(keep)

        players.pts = players.pts.apply(np.round)
        return(players)

    def _cleanStats(self, stats_raw):
        '''
        Convert and clean raw database (.csv) file to readable stats file.
        - Maps raw database file to internally used format
        - This class will be the focal point of properly mapping new databases
        - Actions specified below
        '''

        # 1. Remove columns
        stats_raw = stats_raw.drop(self.settings['remove'], axis=1)

        # 2. Apply mapping header
        # TODO: Add a warning if a columnn is empty in stats_raw
        #       - i,e. fumL
        stats_raw.columns = self.settings['header']

        # 3. Create new stats header
        stats = pd.DataFrame(columns=self.stat_col, index=stats_raw.index)

        # 4. Map raw stats to new stats data
        # TODO: Add an exception - this is risky and will cause errors if not
        #       mapped properly
        stats[stats_raw.columns] = stats_raw

        # 3. fill na with 0
        stats = stats.fillna(0)

        # 4. Clean up names
        stats.name = stats.name.str.replace('[-+!@#$%^&*]', '')

        # 5. Generate id as index
        stats = self._setIndexFromName(stats)

        return(stats)

    def _setIndexFromName(self, stats):
        '''
        Create a unique ID from player name.
        *Caution: Need to add an exception for infinite while loop...
        '''

        FIRST_NAME = 1
        LAST_NAME = 6
        nick_name = []

        for idx_old in stats.index:

            ext = 0
            name = stats.name[idx_old].split()
            abbr = name[0][:FIRST_NAME] + name[-1][:LAST_NAME]

            check = abbr in nick_name
            while check:
                ext += 1
                abbr += str(ext)
                check = abbr in nick_name

                # TODO: make an exceptioon
                if ext > 10:
                    print 'ERROR SEEM TO BE STUCK....'
                    break

            nick_name.append(abbr)

        stats.index = nick_name

        return(stats)

    def _getStatsRaw(self):
        '''
        Read file from data base and convert to generic data-frame
        '''

        file_name = self.settings['file'][0] + self.settings['year'] + \
                    self.settings['file'][1]

        file_path = os.path.join(self.settings['path'], file_name)

        stats = pd.read_csv(file_path)

        return(stats)
