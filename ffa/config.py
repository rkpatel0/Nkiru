'''
Created on Jan 29, 2014

@author: rpatel
'''


class State(object):
    '''
    classdocs
    '''

    def __init__(self, LeagueSettings={}, ProfileSetup={}):
        '''
        Constructor
        '''

        self.league = League(LeagueSettings)
        self.profile = Profile(ProfileSetup)


class Profile:
    '''
    asfaf
    '''

    def __init__(self, settings={}):
        self._set_player_default()
        self.setup(settings)

    def _set_player_default(self):

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
                  'QB': [500,  6,  1, 'exp'],
                  'RB': [400, -30, 0, 'poly'],
                  'WR': [300, -20, 0, 'poly'],
                  'TE': [250, -10, 0, 'poly'],
                  'DE': [300, -10, 0, 'poly'],
                  'K':  [200, -5,  0, 'poly'],
                  }

        self.PLAYERS_DATABASE_DEFAULT = database
        self.PLAYERS_CUSTOM_DEFAULT = custom

    def setup(self, settings):

        # setup players
        if not 'player_custom' in settings:
            self.player_custom = self.PLAYERS_CUSTOM_DEFAULT

        if not 'player_database' in settings:
            self.player_database = self.PLAYERS_DATABASE_DEFAULT


class League:
    '''
    classdocs
    '''

    def __init__(self, settings={}):
        '''
        Constructor
        '''

        self._set_default()
        self.setup(settings)

    def _set_default(self):

        self.DEFAULT_SETTINGS = {}

        roster = {
                  'QB': 1,
                  'RB': 2,
                  'WR': 2,
                  'TE': 1,
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
        asfasf
        '''

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