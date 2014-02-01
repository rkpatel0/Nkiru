'''
Set State - Provides common space to set object conditions - Strong Dependency
==============================================================================

Created on Jan 29, 2014

@author: rpatel
'''


class State(object):
    '''
    Use this object to update the state of all other objects this package.

    Contains objects that set the state of all other classes. It is very
    important to only use this class to set or initialize as all other
    classes use this to grab/set/creat/modify their own parameters.

    Example:
    Need player stats from database of players between a range of years.
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

    def __init__(self, LeagueSettings={}, ProfileSetup={}):
        '''
        Pass desired settings when initializing otherwise use internal default.
        '''

        self.league = League(LeagueSettings)
        self.profile = Profile(ProfileSetup)


class Profile:
    '''
    Sets conditions for the following classes:
    1. Player Profile
    2. More to come...
    '''

    def __init__(self, settings={}):
        '''
        Set up class defaults and base settings
        - USE SETUP method to update settings
        - OR modify individual settings (this maybe dangerous)
        '''

        self._set_player_default()
        self.setup(settings)

    def _set_player_default(self):
        '''
        Set Default settings in case no settings are provided
        '''

        # Project Players

        # Previous Players
        default_header = [
                          'preRank', 'name', 'team', 'age', 'GP', 'GS',
                          'passCmp', 'passAtt', 'passYds', 'passTDs', 'int',
                          'rushAtt', 'rushYds', 'rushAvg', 'rushTDs', 'recCmp',
                           'recYds', 'recAvg', 'recTDs', 'pos', 'VBD',
                          ]

        database = {
                    'year': '2010',
                    'path': r'../../Database/Football/PlayerStatsByYearPFB',
                    'file': ['FantasyStats', '.csv'],
                    'header': default_header,
                    'remove': ['FantPt', 'PosRank', 'OvRank'],
                    'add': ['FumL'],
                    }

        # Custom Players
        custom = {
                #  pos   os    m1  m2  type
                  'QB': [250, +4.5, .85, 'exp'],
                  'RB': [300, +5.2, .80, 'exp'],
                  'WR': [175, +5.0, .20, 'exp'],
                  'TE': [125, +4.5, .99, 'exp'],
                  'DE': [300, -6.0, .00, 'poly'],
                  'K':  [200, -6.0, .00, 'poly'],
                  }

        self.PLAYERS_DATABASE_DEFAULT = database
        self.PLAYERS_CUSTOM_DEFAULT = custom

    def setup(self, settings):
        '''
        Pass settings to update class here otherwise default are used
        '''

        # setup players
        # TODO: Need to throw an exception if struct are not set up correctly
        if not 'player_custom' in settings:
            self.player_custom = self.PLAYERS_CUSTOM_DEFAULT

        if not 'player_database' in settings:
            self.player_database = self.PLAYERS_DATABASE_DEFAULT


class League:
    '''
    General League Parameters are stored here.  Everything will reside here.
    To re-run a new draft after already initialized currently most modify
    parameters directly [need to change this]
    '''

    def __init__(self, settings={}):
        '''
        General object setup.
        '''

        self._set_default()
        self.setup(settings)

    def _set_default(self):
        '''
        Load default settings in case none are provided
        '''

        self.DEFAULT_SETTINGS = {}

        roster = {
                  'QB': 4,
                  'RB': 4,
                  'WR': 4,
                  'TE': 4,
                  }

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

        profile = {
                 # Team   Strat   Tie     Pre-Rank
                   'A': ['rank'  , 'rand', 'default'],
                   'B': ['rank'  , 'rand', 'default'],
                   'C': ['rank'  , 'rand', 'default'],
                   'D': ['breath', 'rand', 'default'],
                   'E': ['rank'  , 'rand', 'default'],
                   'F': ['rank'  , 'rand', 'default'],
                   'G': ['rank'  , 'rand', 'default'],
                   'H': ['rank'  , 'rand', 'default'],
                   }

        self.DEFAULT_SETTINGS['roster'] = roster
        self.DEFAULT_SETTINGS['stat_pts'] = points
        self.DEFAULT_SETTINGS['profile'] = profile

    def setup(self, settings):
        '''
        Defines some constant parameters based off of parameters for league.
        '''

        # TODO: FORCE method to update league parameters once initial settings
        #       are modified

        if not settings:
            settings = self.DEFAULT_SETTINGS

        # TODO: Below should all be caught by an exception...
        self.roster = settings['roster']
        self.pts_per_stat = settings['stat_pts']
        self.team_info = settings['profile']

        # League Dependent Variables
        self.num_of_teams = len(self.team_info)
        self.rounds = sum(self.roster.values())
        self.num_of_players = self.num_of_teams * self.rounds
        self.positions = self.roster.keys()