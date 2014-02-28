'''
Set State - Provides common space to set object conditions - Strong Dependency
==============================================================================

Created on Jan 29, 2014

@author: rpatel
'''
import collections          # ordered dictionary for teams
import copy
import pandas as pd


class State(object):
    '''
    Use this object to update the state of all other objects this package.

    Contains objects that set the state of all other classes. It is very
    important to only use this class to set or initialize as all other
    classes use this to grab/set/creat/modify their own parameters.

    Example:
    Need player stats from oDatabase of players between a range of years.
    (1) Create a method (in Projections Class) that will...
    (1) Set the profile struct in State.profile to point to the desired year
    (2) Grab the player stats using Player Class
    (3) Set the profile to the next year and Grab (again) player stats
    (4) Projection Class can now manipulate the player struct as pleases

    Note:
    This is the best way I could think of of having a single entity that can
    control all other objects cleanly from one location.  At another time when
    several instances of objects (derived from the same class) need to go exist
    this method may no longer suffice.
    '''

    def __init__(self, league={}, profile={}):
        '''
        Pass desired oDatabase when initializing otherwise use internal default.
        '''

        self.oLeague = League(league)
        self.oProfile = Profile(profile)


class Profile:
    '''
    Sets conditions for the following classes:
    1. Player Profile
    2. More to come...
    '''

    def __init__(self, oDatabase={}, oCustom={}):
        '''
        Set up class defaults and base oDatabase
        - USE SETUP method to update oDatabase
        - OR modify individual oDatabase (this maybe dangerous)
        '''

        self._set_player_default()
        self.setup(oDatabase, oCustom)

    def _set_player_default(self):
        'Set Default oDatabase in case no oDatabase are provided'

        # Previous Players
        oDatabase = {
                    'year': '2013',
                    'path': r'../../Database/Football/PlayerStatsByYearPFB',
                    'file': ['FantasyStats', '.csv'],
                    'remove': [],
                    }

        # Custom Players
        customLin = {
                    #  pos   os    m1    m2  type
                      'QB': [450, -10,  .00, 'poly'],
                      'RB': [450, -8,  .00, 'poly'],
                      'WR': [275, -5,  .00, 'poly'],
                      'TE': [225, -6,  .00, 'poly'],
                      'DE': [300, -6.0, .00, 'poly'],
                      'K':  [200, -6.0, .00, 'poly'],
                      }

        customExp = {
                    #  pos   os    m1    m2  type
                      'QB': [250, +4.5, .85, 'exp'],
                      'RB': [300, +5.2, .80, 'exp'],
                      'WR': [175, +5.0, .20, 'exp'],
                      'TE': [125, +4.5, .99, 'exp'],
                      'DE': [300, -6.0, .00, 'poly'],
                      'K':  [200, -6.0, .00, 'poly'],
                      }

        self.PLAYERS_DATABASE_DEFAULT = oDatabase
        self.PLAYERS_CUSTOM_DEFAULT = customExp

    def setup(self, oDatabase, oCustom):
        '''
        Pass oDatabase to update class here otherwise default are used
        '''

        self.player_database = oDatabase
        self.player_custom = oCustom

        for key in self.PLAYERS_DATABASE_DEFAULT.keys():
            if key not in oDatabase:
                self.player_database[key] = self.PLAYERS_DATABASE_DEFAULT[key]

        for key in self.PLAYERS_CUSTOM_DEFAULT.keys():
            if key not in oDatabase:
                self.player_custom[key] = self.PLAYERS_CUSTOM_DEFAULT[key]


class League:
    '''
    General League Parameters are stored here.  Everything will reside here.
    To re-run a new draft after already initialized currently most modify
    parameters directly [need to change this]
    '''

    def __init__(self, oDatabase={}):
        '''
        General object setup.
        '''

        self._set_default()
        self.setup(oDatabase)

    def _set_default(self):
        '''
        Load default oDatabase in case none are provided
        '''

        self.DEFAULT_SETTINGS = {}

        roster = {
                  'QB': 1,
                  'RB': 3,
                  'WR': 3,
                  'TE': 1,
                  }

        # RKP: Should we move this to profile?
        points = {
                  'passYds': 0.025,     # =  1 pts / 40 yards
                  'passTDs': 4,         # =  4 pts /  1 TD
                  'int':     -2,        # = -2 pts /  1 INT
                  'rushYds': 0.1,       # =  1 pts / 10 yard
                  'rushTDs': 5,         # =  5 pts /  1 TD
                  'recCmp':  0.25,      # =  1 pts /  4 comp
                  'recYds':  0.0625,    # =  1 pts / 16 yard
                  'recTDs':  5,         # =  5 pts /  1 TD
                  'fumL':    -2,        # = -2 pts / Fum Lost
                  }

        # This becomes a dataframe
        pro_idx = ['strategy', 'tie', 'rank']
        profile = collections.OrderedDict([
                   # Team   Strat      Tie     Pre-Rank
                   ('A0', ['rank'  , 'rand', 'default']),
                   ('B1', ['search', 'rand', 'default']),
                   ('C2', ['rank'  , 'rand', 'default']),
                   ('D3', ['rank'  , 'rand', 'default']),
                   ('E4', ['rank'  , 'rand', 'default']),
                   ('F5', ['rank'  , 'rand', 'default']),
                   ('G6', ['rank'  , 'rand', 'default']),
                   ('H7', ['rank'  , 'rand', 'default']),
                   ('I8', ['rank'  , 'rand', 'default']),
                   ('J9', ['rank'  , 'rand', 'default']),
                   #('K10', ['rank'  , 'rand', 'default']),
                   #('L11', ['rank'  , 'rand', 'default']),
                   ])

        self.DEFAULT_SETTINGS['roster'] = roster
        self.DEFAULT_SETTINGS['stat_pts'] = points
        self.DEFAULT_SETTINGS['profile'] = pd.DataFrame(profile, index=pro_idx)
        self.DEFAULT_SETTINGS['profile'].index.name = 'Info'

    def setup(self, oDatabase={}):
        '''
        Defines some constant parameters based off of parameters for league.
        '''

        for key in self.DEFAULT_SETTINGS.keys():
            if key not in oDatabase:
                oDatabase[key] = self.DEFAULT_SETTINGS[key]

        # TODO: Below should all be caught by an exception...
        self.roster = oDatabase['roster']
        self.pts_per_stat = oDatabase['stat_pts']
        self.team_info = oDatabase['profile']

        # League Dependent Variables
        self.num_of_teams = len(self.team_info.columns)
        self.rounds = sum(self.roster.values())
        self.num_of_players = self.num_of_teams * self.rounds
        self.positions = self.roster.keys()
        self.team_names = self.team_info.columns.tolist()

    def copy_team_info(self):
        '''
        Return a deep copy of teams info.  Could just do this inside each
        module but this feels cleaner if this function is used frequently.
        '''

        return(copy.deepcopy(self.team_info))
