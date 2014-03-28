'''
Created on Feb 7, 2014

@author: rpatel
'''

import pandas as pd
import numpy as np
import ffa.draft
import webgen.web_report as web
import matplotlib.pyplot as plt


class PreRank(object):
    '''
    classdocs
    '''

    def __init__(self, oLeague, oPlayers, settings={}):
        '''
        Constructor
        '''

        self.oLeague = oLeague
        self.oPlayers = oPlayers

        self._load_defaults()
        self._setup(settings)

    def _load_defaults(self):
        'Basic Default Settings - must be set when class is created'

        self.DEFAULT = {
                        'RUNS_TO_LEARN': 4,         # Runs to Learn new Ranks
                        'PROJECTION': 'pre',        # AI ranks to use for proj
                        'STRATEGY_TYPE': 'search',  # AI Strategy Type
                        'COMPARE_STRAT': 'rank',    # AI Strategy Type
                        }

    def _setup(self, settings):
        'Check for custom settings if not load default'

        self.config = self.DEFAULT

        for key in self.DEFAULT.keys():
            if key in settings:
                self.config[key] = settings[key]

    def generate_preranks(self):
        '''
        Returns optimal pre-ranks for players based off of (1) league settings
        (2) player intial pre-ranks (3) player-projected-points.
        '''

        oLeagueLocal = self.oLeague.copy()
        results = self._setup_preranks(oLeagueLocal)
        oDraft = ffa.draft.Simulator(oLeagueLocal, self.oPlayers.df.copy())

        # 1. Sort Players and Draft Class for Initial Draft Conditions
        compare = pd.DataFrame(index=oLeagueLocal.team_names)

        for i in np.arange(self.config['RUNS_TO_LEARN']):

            # 3. Run Draft
            oDraft.live_draft()

            # 4. Update Players and Sort by Draft Results
            new_rank = oDraft.oResults.df.pick.order()
            oDraft.players[self.config['PROJECTION']] = new_rank

            # Safe way to add new columns (w new ext) in case sub names change
            compare_tmp = self.compare_pre_ranks(player_rank=new_rank)
            col_names = [col + str(i) for col in compare_tmp.columns]
            compare[col_names] = compare_tmp

            # 5. Add coloumns to summary-to-save
            new_col = [x + str(i) for x in oDraft.oResults.SUMMARY_COL]
            results['team'][new_col] = oDraft.oResults.summarize()
            results['pick']['rnk' + str(i)] = oDraft.oResults.df['pick']

        # Order Matters Below!
        DRAFT_COL = ['rnd', 'team']                 # Draft Cols to keep
        compare.ix['AVG'] = compare.mean()
        results['compare'] = compare.transpose().sort_index()
        results['pick'][DRAFT_COL] = oDraft.oResults.df[DRAFT_COL]
        results['pick'].set_index('name',  inplace=True)
        results['team'] = results['team'].transpose()
        results['final'] = results['pick']['rnk' + str(i)]

        return results

    def compare_pre_ranks(self,  player_rank):
        '''
        Test a prerank against a default/static type:
        - This is a self-contained function
        - Do not alter any outside enviornmental settings
        '''

        NEW_RANK = 'rank_cmp'

        oLeagueLocal = self.oLeague.copy()
        players = self.oPlayers.df.copy()
        players[NEW_RANK] = player_rank
        oDraft = ffa.draft.Simulator(oLeagueLocal, players)

        # Set all teams to draft-by-default-ranks
        oLeagueLocal.team_info.ix['strategy'] = self.config['COMPARE_STRAT']
        oLeagueLocal.team_info.ix['rank'] = self.config['PROJECTION']
        res_pre = oDraft.live_draft()
        by_team = pd.DataFrame(index=[res_pre.SUMMARY_COL])

        for name in oLeagueLocal.team_names:
            oLeagueLocal.team_info[name]['rank'] = NEW_RANK
            res_new = oDraft.live_draft()
            oLeagueLocal.team_info[name]['rank'] = self.config['PROJECTION']
            by_team[name] = res_new.summarize().ix[name]

        # Normailze New Rank Results by default Rank Results
        compare = by_team - res_pre.summarize().transpose()

        return compare.transpose()  # Transpose to add more runs as columns

    def _setup_preranks(self, oLeague):
        '''
        Make a copy of league.team_profile and set each player strategy to
        'search' to find player pre-ranks.
        '''

        # Load League Defaults
        oLeague.team_info.ix['strategy'] = self.config['STRATEGY_TYPE']
        oLeague.team_info.ix['rank'] = self.config['PROJECTION']

        # Create team results df
        by_team = pd.DataFrame(index=oLeague.team_names)
        by_team.index.name = 'Team'

        # Create pick-by-pick results df
        SUMMARY_COL = ['pos', 'name', 'pts', self.config['PROJECTION']]
        by_pick = self.oPlayers.df[SUMMARY_COL]     # TODO: Check if col exists
        rank_col = by_pick[self.config['PROJECTION']]   # pulled col to clean
        if self.config['PROJECTION'] == 'pts':
            by_pick['start'] = rank_col.rank(ascending=False)
        else:
            by_pick['start'] = rank_col.rank(ascending=True)

        return {'pick': by_pick, 'team': by_team}


class RunRanks(object):
    'Run any PreRank Tests here if they are to be saved'

    def __init__(self, state, oPlayers):

        self.oState = state
        self.oLeague = state.oLeague
        self.oPlayers = oPlayers

        self._load_webpage_text()
        self._load_constants()

    def _load_constants(self):
        'Load general constants'

        self.PAGES_INDEX = ['pg_name', 'pg_type', 'pg_data']  # DEL: after new
        self.PAGES_COL = ['name', 'type', 'title', 'data']

    def _load_webpage_text(self):
        'Load Constants from here'

        self.SUMMARY_MSG = (
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

        self.OVR_MSG = (
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

    def _summary_plot(self, final):
        'Generate a plot summarizing Sweep results'

        # Save Results Figure
        df_plt = final.convert_objects().dropna().sort('pre')
        df_plt['pre'] = np.arange(len(df_plt)) + 1
        df_plt = df_plt.set_index('pre')
        df_plt = df_plt.drop('pos', axis=1)

        # Add STD to Legend
        dtmp = df_plt.copy()
        for idx in dtmp.columns:
            dtmp[idx] = dtmp[idx] - np.arange(len(dtmp)) - 1
        dtmp = dtmp.std()

        # Check for empty df if none of the df columns have common indexs
        if df_plt.empty:
            plt.figure()
        else:
            df_plt.plot(style='o')

        plt.plot(df_plt.index, df_plt.index, 'k--')
        plt.tight_layout()
        plt.xlabel('Pre Rank Default')
        plt.ylabel('Pre Rank by League Settings')
        plt.title('Pre Rankings: Custom vs. Default')
        l_std = [idx + ' SD: ' + str(dtmp[idx].round(1)) for idx in dtmp.index]
        plt.legend(l_std, loc='best')

        return(plt.gcf())

    def _add_page(self, page):
        '''
        Add rows to pages dataframe
        - Issue with df inside df (careful)
        - Make sure self.pages is set/reset before coming here!
        - Page must follow standard format!
        '''

        # Add a DF row by string index else it thinks it already exists
        idx = str(len(self.pages.index))
        self.pages.ix[idx, 'name'] = page[0]
        self.pages.ix[idx, 'type'] = page[1]
        self.pages.ix[idx, 'title'] = page[2]
        self.pages['data'][idx] = page[3]

    def _summarize_to_page(self,  summary, sweep, frame_key, sweep_key):
        'Add rows to dataframe Run after PreRank Sweeps'

        if sweep_key == 'roster':
            roster_frame = sweep.transpose()
        else:
            roster_frame = pd.DataFrame(self.oLeague.roster, index=['LG0'])
        roster_frame.index.name = 'Positon'

        if sweep_key == 'stat_pps':
            pps_frame = sweep.transpose()
        else:
            pps_frame = self.oPlayers.bio['data']
            pps_frame.index = ['LG0']
        pps_frame.index.name = 'Points'

        # Overview
        teams = self.oLeague.team_info
        self._add_page(['Overview', 'TEXT', 'How it Works', self.OVR_MSG])
        self._add_page(['Overview', 'DATA', 'League Rosters(s)', roster_frame])
        self._add_page(['Overview', 'DATA', 'Team Summary', teams])

        # Players
        self.oLeague.setup({'roster': roster_frame.max(axis=0).to_dict()})
        self.oPlayers.set_to_draft()
        ply_oFig = self.oPlayers.plot_position_points()
        ply_head = self.oPlayers.bio['header']
        ply_body = self.oPlayers.bio['body']
        ply_draft = self.oPlayers.df.set_index('name')
        self._add_page(['Players', 'TEXT', ply_head, ply_body])
        self._add_page(['Players', 'DATA', 'Player Overview', pps_frame])
        self._add_page(['Players', 'FIG', 'Player Points Plot', ply_oFig])
        self._add_page(['Players', 'DATA', 'Players for Draft', ply_draft])

        # Summary
        SUM1_TITLE = 'Comparing PreRanks vs. League Settings'
        SUM2_TITLE = 'League Optimized PreRank vs. Default PreRanks'
        SUM3_TITLE = 'League Optimized PreRank Resu;ts'
        self._add_page(['Summary', 'TEXT', SUM1_TITLE, self.SUMMARY_MSG])
        self._add_page(['Summary', 'FIG', SUM2_TITLE, self._summary_plot(summary)])
        self._add_page(['Summary', 'DATA', SUM3_TITLE, summary.sort('pre')])

    def get_rank_page(self, page_name='DFT'):
        'Run a one time sweep with default settings'

        self.sweep_rank_page(self.oLeague.roster, 'league', 'roster', page_name)

    def roster_report(self, page_name='RST'):
        'Compare different Rosters vs. Optimal Preranks'

        roster = {
                  'QB': [0, 0, 1, 0],
                  'RB': [0, 0, 0, 1],
                  'WR': [0, 0, 0, 0],
                  'TE': [1, 1, 0, 0],
                  }

        rost_df = pd.DataFrame.from_dict(roster, orient='index')
        self.sweep_rank_page(rost_df, 'league', 'roster', page_name)

    def pps_report(self, page_name='RST'):
        'Compare different Points per State vs. Optimal PreRanks'

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

        pps_df = pd.DataFrame.from_dict(points, orient='index')
        self.sweep_rank_page(pps_df, 'league', 'stat_pts', page_name)

    def year_report(self, page_name='YEAR'):
        'Sweep through multiple years - probably not too useful'

        # This doesn't really work - index for players needs to be thought out
        years = {'year': ['2011', '2012', '2013']}

        df = pd.DataFrame.from_dict(years, orient='index')
        self.sweep_rank_page(df, 'database', 'year', page_name)

    def sweep_rank_page(self, sweep_df, frame='', sweep='',  name=''):
        '''
        Sweep arbitrarily through oState settings
        - Can only sweep through on parameter at a time curretnly
        - Switch to a more all-inclusive df method
          o Sweep based off of index in column - with multiple league settings
        - Need more teesting still
        '''

        # Summary DF (TODO: think we need to set index to all POSSIBLE players)
        FIN_SAVE = ['pos', 'pre']
        summary_df = pd.DataFrame(index=self.oPlayers.df.name)
        summary_df[FIN_SAVE] = self.oPlayers.df.set_index('name')[FIN_SAVE]

        # 2. Create Simulator + Final_RanK DF w. index of ALL possible players
        self.pages = pd.DataFrame(columns=self.PAGES_COL)
        oSimulate = PreRank(self.oLeague, self.oPlayers)

        # 4. Sweep League Roster [update players based on league roster]
        RES1_TITLE = 'Sumulated Draft Results: Pick-by-Pick'
        RES2_TITLE = 'Simulated Draft Results: Team-by-Team '
        RES3_TITLE = 'Team Peformance using AI with others using default rank'
        sweep_df.columns = ['LG' + str(i) for i in sweep_df.columns]

        for col in sweep_df:
            page_name = 'Results ' + col
            self.oState.setup(**{frame: {sweep: sweep_df[col].to_dict()}})
            self.oPlayers.set_to_draft()
            results = oSimulate.generate_preranks()
            results['final'].name = col
            summary_df = summary_df.join(results['final'], how='outer')
            self._add_page([page_name, 'DATA', RES1_TITLE, results['pick']])
            self._add_page([page_name, 'DATA', RES2_TITLE, results['team']])
            self._add_page([page_name, 'DATA', RES3_TITLE, results['compare']])

        # 6. Generate Report
        self._summarize_to_page(summary_df, sweep_df, frame, sweep)
        report = web.ReportGen()
        report.web_report(self.pages, name=name)
