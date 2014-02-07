'''
Created on Feb 3, 2014

@author: rpatel
'''
import pandas as pd
import numpy as np
import random
import copy


class Simulator(object):
    '''
    Top level cass to simulate drafts given (1) Teams (2) Players (3) League
    Settings.  Results are saved into their own object, results for post
    processing at any given time.
    '''

    def __init__(self, league, players):
        '''
        Pass in (1) League Settings and (2) players for draft.  Player prerank
        for most drafts will be vital for meaningful results.
        '''
        self.setup(league, players)

    def setup(self, league, players):
        '''
        Use to set up intial Simulator settings.  Call/set this method to
        after initialization to run a modified draft.
        '''
        self.league = league
        self.players = players

        self._generate_draft_order()

    def _generate_draft_order(self):
        '''
        Generate Snake Draft Order based on number of teams and roster spots.
        '''

        names = self.league.team_info.keys()
        self._draft_order = []

        for i in np.arange(self.league.rounds):
            self._draft_order.extend(names)
            names.reverse()

    def live_draft(self):
        '''
        Kick-off draft, return draft results object to analyize draft.
        '''

        self.results = DraftResults(self.league.num_of_players)
        players = self.players  # local copy that will get altered thru draft

        for name in self._draft_order:
            select = self._select_player(name, players)
            self.results._update(name, players.ix[select])
            players = players.drop(select)

        self.results.get_results()

        return(self.results)

    def _select_player(self, name, players):
        '''
        Return player index's for potential players to draft based on strategy
        '''

        profile = self.league.team_info[name]
        playersAv = self._needed_players(name, players, self.results)

        if profile[self.league.PROFILE_MAP['strategy']] == 'max':
            options = playersAv.pts == playersAv.pts.max()
        elif profile[self.league.PROFILE_MAP['strategy']] == 'rank':
            options = playersAv.preRank == playersAv.preRank.min()
        elif profile[self.league.PROFILE_MAP['strategy']] == 'user':
            options = self._user_select_player(name, playersAv)
        elif profile[self.league.PROFILE_MAP['strategy']] == 'search':
            options = self._search_select_player(name, players)

        if profile[self.league.PROFILE_MAP['tie']] == 'rand':
            select = random.choice(options[options == True].index)
        elif profile[self.league.PROFILE_MAP['tie']] == 'first':
            select = options[options == True].index[0]
        elif profile[self.league.PROFILE_MAP['tie']] == 'last':
            select = options[options == True].index[-1]

        return(select)

    def _needed_positions(self, name, results):
        '''
        Return a dictionary of positons that team still needs to draft. Based
        off of league roster and teams previous draft picks
        '''

        # TODO: Need to factor in flex picks...
        keep = {}
        pos_count = results._count_positions(name, results)
        for pos in self.league.positions:
            if pos in pos_count:
                delta = self.league.roster[pos] - pos_count[pos]
                if delta > 0:
                    keep[pos] = delta
                elif delta < 0:
                    raise ValueError('Game Over')
            else:
                keep[pos] = self.league.roster[pos]

        return(keep)

    def _needed_players(self, name, players, results):
        '''
        Return players that team can draft based on team draft picks so far

        For each position check if team has reached max_available_at_pos. If so
        remove all players left for particular positon.
        '''

        pos_count = self._needed_positions(name, results)

        for pos in self.league.positions:
            if not pos in pos_count:
                players = players[players.pos != pos]

        return(players)

    def _user_select_player(self, name, players):
        '''
        Prompt user to select index of player to draft.
        '''
        MAX_DISPLAY = 20

        print '\nCurrent Team:\n', self.results._get_team(name)
        print '\nTotal Roster Spots\n:', self.league.roster
        print '\nAvailable Players for your to draft:\n', players[:MAX_DISPLAY]

        while True:
            try:
                msg = '\nTeam ' + name + ' Select Player by preRank column:\n'
                rnkIdx = np.int64(raw_input(msg))
                options = players.preRank == rnkIdx
                if not options.any():
                    print 'Player not available! Enter a valid preRank index!'
                else:
                    break
            except ValueError:
                print '\nInvalid option! Use the preRank column # to select'

        return(options)

    def _search_select_player(self, name, players):
        '''
        Where do I even start...
        '''

        # TMP:
        print 'Search Round:', self.results._get_team(name).team.count() + 1

        # Make a copy to initialze
        playerList = [players.copy()]
        resultList = [self.results.copy()]
        self.best_team = [self.results.copy()]
        nodes = [self._needed_positions(name, resultList[-1]).keys()]

        # Initialize search parameters
        self._search_copy_list(name, nodes, playerList, resultList)

        # Keep running until all nodes/branches are exhausted
        while nodes:
            self._search_player_nodes(name, nodes, playerList, resultList)

        options = self._search_get_best_options(players)

        return(options)

    def _search_get_best_options(self, players):
        '''
        Return the best draft options for a given round.
        '''

        player_names = []
        player_index = self.results.df.team.count()   # count any columns

        # Get player name(s) for from the appropriate round
        for best in self.best_team:
            player_names.append(best.df.name[player_index])

        # TODO: raise some type of warning that there was a tie between players
        options = players.name.isin(player_names)

        return(options)

    def _search_player_nodes(self, name, nodes, playerList, resultList):
        '''
        Even more complicated...
        TODO: Make dynamic for breath and depth - currently just depth
        '''

        try:
            pos = nodes[-1].pop()
        except Exception as ex:
            # FIX:  This is just so wrong...
            raise ValueError('No position to pop from nodes!\n')

        # Check for empty nodes after pop
        if nodes[-1] == []:
            nodes.pop()

        # Draft player with max points at given position
        players_av = playerList[-1][playerList[-1].pos == pos]
        options = players_av[players_av.pts == players_av.pts.max()]

        try:
            # TODO: Search Random or Deter
            select = random.choice(options.index)
        except Exception as ex:
            raise ValueError('No options available to make a selection from\n')

        # Add player to team
        resultList[-1]._update(name, players_av.ix[select])
        NEXT_ROUND = resultList[-1]._get_team(name).team.count()

        # Check if team is filled or if there are more nodes to search
        if NEXT_ROUND == self.league.rounds:

            # Sanity Check: # of players drafted match roster size
            if resultList[-1]._get_team(name).team.count() != NEXT_ROUND:
                raise ValueError('Did not Draft enought players!\n')

            # Remove results and players from lists
            results = resultList.pop()
            playerList.pop()

            # Check if latest team is best
            team_pts = results.get_team_pts(name)
            if team_pts > self.best_team[0].get_team_pts(name):
                self.best_team = [results]
                print results._get_team(name)
            elif team_pts == self.best_team[0].get_team_pts(name):
                self.best_team.append(results)

        else:
            # Only update playerList if branch not complete
            playerList[-1] = playerList[-1].drop(select)
            keep = self._needed_positions(name, resultList[-1])
            nodes.append(keep.keys())
            playerList[-1] = self._search_drop_projections(NEXT_ROUND,
                                                           name, keep,
                                                           playerList[-1])
            self._search_copy_list(name, nodes, playerList, resultList)

    def _search_copy_list(self, name, nodes, playerList, resultList):
        '''
        '''

        # Pop items from list and re-add (yes in-efficient) but clean...
        players = playerList.pop()
        results = resultList.pop()

        for pos in nodes[-1]:
            playerList.append(players.copy())
            resultList.append(results.copy())

    def _search_drop_projections(self, NEXT_ROUND, name, keep, players):
        '''
        Return players that are projected to be drafted by next turn.  Players
        are to be dropped based pre-ranks and number of turns until next pick.

        Important:
        In the likely event that all players from a needed position are
        dropped a check at the end re-adds those players which will be needed.

        This is a costly and time-consuming check.  Much of the optimal draft
        order may come down to this.  Hence more time may need to be spent to
        either optimize the speed or the accuracy for better AI predictions.
        '''

        # Efficient way to find # of players to be dropped between turns
        FIRST_WAIT = self._draft_order.index(name)
        if NEXT_ROUND % 2 == 0:  # Even
            players_to_drop = 2 * FIRST_WAIT
        else:
            players_to_drop = 2 * (self.league.num_of_teams - FIRST_WAIT - 1)

        playersLeft = players[players_to_drop:]

        # Check if sufficient players at each position in players list
        pos_count = playersLeft.groupby('pos').pos.count()
        for pos in keep.keys():
            if pos in pos_count:
                delta = pos_count[pos] - keep[pos]
            else:
                delta = -keep[pos]

            # If delta is negative need to add players back...
            if delta < 0:
                players_at_pos = players[players.pos == pos]
                if pos in pos_count:
                    add_players = players_at_pos.ix[-keep[pos]:-pos_count[pos]]
                else:
                    add_players = players_at_pos.ix[-keep[pos]:]

                # Check sufficient players were added
                if len(add_players) != -delta:
                    msg = 'INSUFFIEICENT PLAYERS TO ADD BACK!'
                    raise ValueError(msg)

                playersLeft = playersLeft.append(add_players)

        # TODO: Should players be re-sorted, no because we'll need to draft
        #       them either way, why add them to only cut them again?
        return(playersLeft)


class DraftResults:
    '''
    Manipulate Draft Results settings from here.  In general we'd like to keep
    this object 'active' through out process of analyzing draft results stored
    when generated due to extra methods stored here.

    But as this involves it maybe tider to just save a list/dict or results
    data frame as oppose to list/dict of objects.
    '''

    def __init__(self, num_of_players):
        '''
        Create an object that has access to draft results.  Use to get results
        by team. Or final results, i.e., who won.
        '''

        self._set_constants()
        self.setup(num_of_players)

    def _set_constants(self):
        '''
        Set any constants that should not be changed again here
        '''

        self._COLUMN_NAMES = ['rank', 'rnd', 'team', 'name', 'pos', 'pts']

    def setup(self, num_of_players):
        '''
        Not recommended but you can reset Draft Results conditions here
        '''

        self.df = pd.DataFrame(index=np.arange(num_of_players),
                               columns=self._COLUMN_NAMES)

    def _update(self, team_name, player):
        '''
        Add player to results data frame.  We have to calculate round and
        where to place them.
        '''

        rnd = self.df.team[self.df.team == team_name].count() + 1
        pick_num = self.df.team.count()

        self.df.ix[pick_num] = [
                                     player['preRank'], rnd, team_name,
                                     player['name'], player['pos'],
                                     player['pts'],
                                     ]

    def _get_team(self, name):
        '''
        Return results df with just results for a single team
        - replaces the need for a team df
        '''

        return(self.df[self.df.team == name])

    def _count_positions(self, name, pos):
        '''
        Return number of players at each position for a team.
        '''

        team = self._get_team(name)
        pos_count = team.groupby('pos').pos.count()

        return(pos_count.to_dict())

    def copy(self):
        '''
        Return a copy of the object created
        '''

        return(copy.deepcopy(self))

    def get_team_pts(self, name):
        '''
        Return team pts.
        '''

        pts = self.df.pts[self.df.team == name].sum()
        return(pts)

    def get_results(self):
        '''
        Analyze draft results once complete
        '''

        self.summary = self.df.groupby('team').pts.sum()
        self.summary.sort(ascending=False)