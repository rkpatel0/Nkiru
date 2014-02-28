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
    inherit this class and set any needed properties.
    '''

    def _set_player_defaults(self):
        '''
        Set all player (general) default values here.  This must specifically
        be called by sub class!
        '''

        # RKP: Clean Up Header!!
        self.PLAYER_DEFAULT = {}
        self.PLAYER_DEFAULT['draft'] = ['name', 'pos', 'pre', 'pts']
        self.DEFAILT_BIO_MSG = (
        '<br><br>Observe the positional slope/decay in the <strong>Points vs. '
        'Rank-by-Positon Plot</strong> below. This is one of the major '
        'factors in determining prerankings.  Most prerank generators assume '
        'a linear slope due to compuational or algorithmic limitations.  '
        'However our latest prerank engines embrace all the non-linearity '
        'that exists in these real-world applications.')

    def set_to_draft(self):
        '''
        Generates players based on current state settings.
        Must recall this function anytime state changes to update player stats
        '''

        # Call child generate function
        self.df = self._generate()

        # Apply standard configuration
        self.df.pts = self.df.pts.apply(np.round)
        self.df = self.df.sort(columns='pre')
        self._set_bio()

    def plot_position_points(self, save_path=''):

        '''
        Plot pts (keep default order) by positon.  Must be called AFTER players
        have been generated!
        '''

        try:
            all_pos = self.df.pos.unique()
        except NameError:
            raise NameError('Need to create players before plotting!')

        plt.figure()
        for pos in all_pos:
            players = self.df.pts[self.df.pos == pos].copy()
            players.sort(ascending=False)
            plt.plot(players, 'o-', linewidth=2.0)

        plt.legend(all_pos)
        plt.grid()
        plt.xlabel('Player Rank')
        plt.ylabel('Fantasy Points')
        plt.title('Fantasy Points by Position')
        plt.tight_layout()

        return(plt.gcf())


class Artificial(Player):
    '''
    Create custom defined players by passing slopes and offet.  Can create
    players with (1) polynomial decay (2) exponential decay.
    '''
    def __init__(self, oState):

        self.oLeague = oState.oLeague
        self.player_equation = oState.oProfile.player_custom
        self._set_player_defaults()
        self._setup()

    def _setup(self):
        'Set general class initial conditions.'

        self.SCALE_COEFF_2 = 0.1

    def _generate(self):
        '''
        Return a data frame with structure designed for draft-specific needs.
        '''

        players = pd.DataFrame(columns=self.PLAYER_DEFAULT['draft'],
                               index=np.arange(self.oLeague.num_of_players))

        idx = 0
        for pos in self.oLeague.roster.keys():

            num_of_pos = self.oLeague.roster[pos] * self.oLeague.num_of_teams
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
            raise ValueError('Invalid custom player equation type!\n')

        return(points)

    def _get_points_exp(self, arr, coeff):

        '''
        Returns array with an exponential decay. Provide array 'arr' and exp
        coefficients 'coeff'.

        Equation:
        pts = exp(-m2 * x + m1) + m0'
        m0' = m0 - exp(m1)
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

    def _set_bio(self):
        'Dictionary of player-related information for report/webpage'

        self.bio = {}

        df = pd.DataFrame(self.player_equation)
        info = (
        'Players for this simulation have been <strong>Artificially</strong> '
        'derived using the table below.  Each position fits either a <strong>'
        'Polynomial</strong> or an <strong>Exponential</strong> (decay) curve.'
        '  These curves model player role-off relative to each position. '
        'This helps to illustrate the impact of different slopes and decay '
        'curves and how they may impact the pre-rankings.' +
        self.DEFAILT_BIO_MSG)

        self.bio['data'] = df
        self.bio['header'] = 'Player Background'
        self.bio['msg'] = info


class Database(Player):
    '''
    Get player stats (or points) as defined database.  Either return players
    for fantasy specific purposes or projections.

    Use info.oLeague and info.database to define desired database player stats.
    '''

    def __init__(self, oState):
        '''
        Always pass database on initializtion, then use those objects to define
        desired player stats.
        '''

        self.oLeague = oState.oLeague
        self.oDatabase = oState.oProfile.player_database
        self._set_player_defaults()
        self._setup()

    def _setup(self):
        '''
        Set general class initial conditions.
        '''

        # Must sync/map STAT_COL and RAW_COL_MAP as only the columns that are
        # the same between the two are kept in the final stats df.
        self.STAT_COL = [
                         'preRank', 'name', 'team', 'age', 'GP', 'GS',
                         'passCmp', 'passAtt', 'passYds', 'passTDs', 'int',
                         'rushAtt', 'rushYds', 'rushAvg', 'rushTDs', 'recCmp',
                         'recYds', 'recAvg', 'recTDs', 'fumL', 'pos', 'VBD',
                         'pts',
                         ]

        # Order Matters! Each item below needs to line up with the raw stats
        # database.  Do not skip any items!
        self.RAW_COL_MAP = [
                            'pre', 'name', 'team', 'age', 'GP', 'GS',
                            'passCmp', 'passAtt', 'passYds', 'passTDs', 'int',
                            'rushAtt', 'rushYds', 'rushAvg', 'rushTDs',
                            'recCmp', 'recYds', 'recAvg', 'recTDs', 'pos',
                            'FantPt', 'VBD', 'PosRank', 'OvRank',
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

        for category in self.oLeague.pts_per_stat.keys():
            stats.pts += (self.oLeague.pts_per_stat[category] * stats[category])

        stats.sort(columns='pts', ascending=False, inplace=True)

        return(stats)

    def _stats_to_players(self, stats):

        players = pd.DataFrame(columns=self.PLAYER_DEFAULT['draft'])

        # Remove excess players at each position + keep only draft categories
        for pos in self.oLeague.positions:
            num = self.oLeague.roster[pos] * self.oLeague.num_of_teams
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
        stats_raw = stats_raw.drop(self.oDatabase['remove'], axis=1)

        # 2. Map database/raw header to internal names
        try:
            stats_raw.columns = self.RAW_COL_MAP
        except Exception as ex:
            msg = 'Cannot map internal column format to raw stats data frame\n'
            template = ('Exception of type: {0} occured.\nArguments: {1!r}\n')
            raise ValueError(msg + template.format(type(ex).__name__, ex.args))

        # 3. Create stats dataframe
        stats = pd.DataFrame(columns=self.STAT_COL, index=stats_raw.index)

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

        file_name = self.oDatabase['file'][0] + self.oDatabase['year'] + \
                    self.oDatabase['file'][1]

        self.file_path = os.path.join(self.oDatabase['path'], file_name)

        try:
            stats = pd.read_csv(self.file_path)
        except IOError:
            raise IOError('Cannot open file:\n' + self.file_path)

        return(stats)

    def _generate(self):
        '''
        Get players from database
        '''
        stats = self._get_stats()
        stats = self._get_fantasy_points(stats)
        players = self._stats_to_players(stats)

        return(players)

    def _set_bio(self):
        'Dictionary of player-related information for report/webpage'

        self.bio = {}

        df = pd.DataFrame(self.oLeague.pts_per_stat, index=['points'])
        info = ('Players for this simulation are from the <strong>{year}'
                '</strong> season and from the <strong>{path}</strong> '
                'database. Below are the Points per Stat used to derive '
                'players point totals.' + self.DEFAILT_BIO_MSG).format

        self.bio['data'] = df
        self.bio['header'] = 'Player Background'
        self.bio['msg'] = info(year=self.oDatabase['year'],
                               path=self.oDatabase['file'][0])