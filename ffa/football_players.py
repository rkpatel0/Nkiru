'''
Player Generation - Grab, manipluate players from database or create custom
==============================================================================

Created on Jan 29, 2014
@author: rpatel

'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os.path


class Player(object):
    '''
    SubClass to Database and Artificial Player Classes.  In general, this class
    should never be directly called.  Let Database and Artificial Player
    Classes call this class and set any needed properties.
    '''

    def __init__(self, info):
        '''
        Pass object to setup Arificial and Database player generator.  Even if
        both are not being used both need to be set up.  Using 'info' default
        database will be passed so one need not directly initialize explicity.
        '''
        pass

        #self.custom = Artificial(info.league, info.profile.player_custom)
        #self.past = Database(info.league, info.profile.player_database)

    def _set_player_defaults(self):
        '''
        Set all player (general) default values here.  This must specifically
        be called by sub class!

        RKP: Could we make this be auto-called on initialization?
        '''

        self.PLAYER_DEFAULT = {}
        self.PLAYER_DEFAULT['draft'] = ['name', 'pos', 'preRank', 'pts']

    def _set_for_draft(self):
        '''
        Keeps all sub-player classes synced
        '''

        self.players.pts = self.players.pts.apply(np.round)
        self.players = self.players.sort(columns='preRank')

    def plot_position_points(self):

        '''
        Plot pts (keep default order) by positon.  Must be called AFTER players
        have been generated!
        '''

        try:
            all_pos = self.players.pos.unique()
        except NameError:
            raise NameError('Need to create players before plotting!')

        plt.figure()
        for pos in all_pos:
            plt.plot(self.players.pts[self.players.pos == pos])

        plt.legend(all_pos)
        plt.grid()
        plt.xlabel('player rank')
        plt.ylabel('fantasy pts')
        plt.title('Fantasy Pts by Position')
        plt.show()


class Artificial(Player):
    '''
    Create custom defined players by passing slopes and offet.  Can create
    players with (1) polynomial decay (2) exponential decay.
    '''
    def __init__(self, info):

        self.league = info.league
        self.player_equation = info.profile.player_custom
        self._set_player_defaults()
        self._setup()

    def _setup(self):
        '''
        Set general class initial conditions.
        '''
        self.SCALE_COEFF_2 = 0.1

    def _generate(self):
        '''
        Return a data frame with structure designed for draft-specific needs.
        '''

        players = pd.DataFrame(columns=self.PLAYER_DEFAULT['draft'],
                               index=np.arange(self.league.num_of_players))

        idx = 0
        for pos in self.league.roster.keys():

            num_of_pos = self.league.roster[pos] * self.league.num_of_teams
            pts_by_pos = self._get_points(num_of_pos,
                                          self.player_equation[pos])

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
        Returns a numpy array of pts as specified by profile-player-database.
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

        coeff[2] = self.SCALE_COEFF_2 * coeff[2]

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

    def players_to_draft(self):
        '''
        Returns custom-defined players as defined in league and profile objects
        '''

        self.players = self._generate()
        self._set_for_draft()

        return(self.players)


class Database(Player):
    '''
    Get player stats (or points) as defined database.  Either return players
    for fantasy specific purposes or projections.

    Use info.league and info.database to define desired database player stats.
    '''

    def __init__(self, info):
        '''
        Always pass database on initializtion, then use those objects to define
        desired player stats.
        '''

        self.league = info.league
        self.database = info.profile.player_database
        self._set_player_defaults()
        self._setup()

    def _setup(self):
        '''
        Set general class initial conditions.
        '''

        # RKP: Is this really the final structure for stat-pts??
        self.stat_col = [
                         'preRank', 'name', 'team', 'age', 'GP', 'GS',
                         'passCmp', 'passAtt', 'passYds', 'passTDs', 'int',
                         'rushAtt', 'rushYds', 'rushAvg', 'rushTDs', 'recCmp',
                         'recYds', 'recAvg', 'recTDs', 'fumL', 'pos', 'VBD',
                         'pts',
                         ]

    def _get_stats(self):
        '''
        Return player stats for (1) projection class or (2) draft pts
        - Careful about post processing here - impacts pts + draft classes
        '''

        stats = self._read_from_database()
        stats = self._clean_stats(stats)

        return(stats)

    def _get_fantasy_points(self, stats):
        '''
        Return dataframe that:
            (1) computets points form stats
            (2) converts stats frame to draft frame
            (3) Perhaps we (just) want to compute fantasy points and append
                then, under _draft_clean_up we only keep columns for draft
        '''

        for category in self.league.pts_per_stat.keys():
            stats.pts += (self.league.pts_per_stat[category] * stats[category])

        stats.sort(columns='pts', ascending=False, inplace=True)

        return(stats)

    def _stats_to_players(self, stats):

        players = pd.DataFrame(columns=self.PLAYER_DEFAULT['draft'])

        # Remove excess players at each position + keep only draft categories
        for pos in self.league.positions:
            num = self.league.roster[pos] * self.league.num_of_teams
            keep = stats[self.PLAYER_DEFAULT['draft']][stats.pos == pos][:num]

            if len(keep) < num:
                msg = 'ERROR NUMBER OF PLAYERS AT POS ARE NOT ENOUGHH!!'
                raise ValueError(msg, keep)
            else:
                players = players.append(keep)

        return(players)

    def _set_index(self, stats):
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

                # Raise if we can't create proper player IDs (should not occur)
                if ext > 10:
                    raise ValueError('Stuck inside infinite loop...')

            nick_name.append(abbr)

        stats.index = nick_name

        return(stats)

    def _clean_stats(self, stats_raw):
        '''
        Convert and clean raw database (.csv) file to readable stats file.
        - Maps raw database file to internally used format
        - This class will be the focal point of properly mapping new databases
        - Actions specified below
        '''

        # 1. Remove unnecessary database/raw columns
        stats_raw = stats_raw.drop(self.database['remove'], axis=1)

        # 2. Map database/raw header to internal names
        try:
            stats_raw.columns = self.database['header']
        except Exception as ex:
            msg = 'Cannot map internal column format to raw stats data frame\n'
            template = ('Exception of type: {0} occured.\nArguments: {1!r}\n')
            raise ValueError(msg + template.format(type(ex).__name__, ex.args))

        # 3. Create stats dataframe
        stats = pd.DataFrame(columns=self.stat_col, index=stats_raw.index)

        # 4. Add data from raw stats (there is no .add_column function)
        try:
            stats[stats_raw.columns] = stats_raw
        except Exception as ex:
            msg = 'Cannot copy raw stats data to intneral format\n'
            template = ('Exception of type: {0} occured.\nArguments: {1!r}\n')
            raise ValueError(msg + template.format(type(ex).__name__, ex.args))

        # 5. Clean up stats - Don't change Order
        #    - Nan names get filled with numbers then back to nan when stripped
        stats = stats.fillna(0)
        stats.name = stats.name.str.replace('[-+!@#$%^&*]', '')
        stats = stats.dropna()

        # 6. Generate id as index
        stats = self._set_index(stats)

        return(stats)

    def _read_from_database(self):
        '''
        Read file from data base and convert to generic data-frame
        '''

        file_name = self.database['file'][0] + self.database['year'] + \
                    self.database['file'][1]

        # RKP: Should we add a try here?
        file_path = os.path.join(self.database['path'], file_name)

        stats = pd.read_csv(file_path)

        return(stats)

    def players_to_draft(self):
        '''
        Get players from database
        '''
        stats = self._get_stats()
        stats = self._get_fantasy_points(stats)
        self.players = self._stats_to_players(stats)
        self._set_for_draft()
        plt.show()
        
        return(self.players)
