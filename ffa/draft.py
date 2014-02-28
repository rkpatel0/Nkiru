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
    Inputs Constants: (1) League Settings (2) Players
    Outputs: (1) Results Object (creates a new copy each time draft is ran
    '''

    def __init__(self, oLeague, players):
        '''
        Note:
        (1) Inputs are classes hence if modified they need not be passed in
        again, instead update them and run setup() to update internal

        (2) Inputs are not locally modified - Careful about updating inputs
        '''

        self.oLeague = oLeague
        self.players = players

        self.setup()

    def setup(self):
        'Use to update internal parameters ANYTIME inputs need to be modified'

        self._generate_draft_order()

    def live_draft(self):
        '''
        Kick-off draft, return draft results object to analyize draft.

        Output: Results Object - store locally since regenerated for each draft
        '''

        players = self.players.copy()
        self.oResults = DraftResults(players.index)

        for name in self._draft_order:
            select = self._select_player(name, players)
            self.oResults._update(name, players.ix[select])
            players = players.drop(select)

        return(self.oResults.copy())

    def _generate_draft_order(self):
        '''
        Generate Snake Draft Order based on number of teams and roster spots.
        '''

        names = self.oLeague.team_names
        self._draft_order = []

        for i in np.arange(self.oLeague.rounds):
            self._draft_order.extend(names)
            names.reverse()

    def _select_player(self, name, players):
        '''
        Return player index's for potential players to draft based on strategy
        '''

        profile = self.oLeague.team_info[name]
        playersAv = self._needed_players(name, players, self.oResults)

        if profile['strategy'] == 'max':
            options = playersAv.pts == playersAv.pts.max()
        elif profile['strategy'] == 'rank':
            # TODO: then sory by desired rank (pre/vbd) --> Use a Try!!
            try:
                rank_type = profile['rank']
                options = playersAv[rank_type] == playersAv[rank_type].min()
            except KeyError:
                raise KeyError('Cannot find desired pre-rank!')
        elif profile['strategy'] == 'user':
            options = self._user_select_player(name, playersAv)
        elif profile['strategy'] == 'search':
            options = self._search_select_player(name, players)
        else:
            raise ValueError('Unknown type of team strategy selected!\n')

        if profile['tie'] == 'rand':
            select = random.choice(options[options == True].index)
        elif profile['tie'] == 'first':
            select = options[options == True].index[0]
        elif profile['tie'] == 'last':
            select = options[options == True].index[-1]
        else:
            raise ValueError('Unknown type of team tie-breaker selected!\n')

        return(select)

    def _needed_positions(self, name, oResults):
        '''
        Return a dictionary of positons that team still needs to draft. Based
        off of league roster and teams previous draft picks

        Note:
        Only save positons that NEED TO BE DRAFTED, dictionary should not
        contain ANY positions that need zero more players.  Because search
        functions just look at keys of keep dictionary hence we're blind to
        zero-valued positions.
        '''

        # TODO: Need to factor in flex picks...
        pos_count = oResults._count_positions(name, oResults)

        # Keep cannot store any zer-valued positons
        keep = {}
        for pos in self.oLeague.positions:
            if pos in pos_count:
                delta = self.oLeague.roster[pos] - pos_count[pos]
                if delta > 0:
                    keep[pos] = delta
                elif delta < 0:
                    raise ValueError('Game Over')
            elif self.oLeague.roster[pos] != 0:
                keep[pos] = self.oLeague.roster[pos]

        return(keep)

    def _needed_players(self, name, players, oResults):
        '''
        Return players that team can draft based on team draft picks so far

        For each position check if team has reached max_available_at_pos. If so
        remove all players left for particular positon.
        '''

        pos_count = self._needed_positions(name, oResults)

        for pos in self.oLeague.positions:
            if not pos in pos_count:
                players = players[players.pos != pos]

        return(players)

    def _user_select_player(self, name, players):
        '''
        Prompt user to select index of player to draft.
        '''
        MAX_DISPLAY = 20

        print '\nCurrent Team:\n', self.oResults._get_team(name)
        print '\nTotal Roster Spots\n:', self.oLeague.roster
        print '\nAvailable Players for your to draft:\n', players[:MAX_DISPLAY]

        while True:
            try:
                msg = '\nTeam ' + name + ' Select Player by preRank column:\n'
                rnkIdx = np.int64(raw_input(msg))
                options = players.pre == rnkIdx
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

        # Make a copy to initialze
        playerList = [players.copy()]
        resultList = [self.oResults.copy()]
        self.best_team = [self.oResults.copy()]

        # Initialize search parameters
        nodes = [self._needed_positions(name, resultList[-1]).keys()]
        self._search_copy_list(name, nodes, playerList, resultList)

        # Keep running until all nodes/branches are exhausted
        while nodes:
            self._search_player_nodes(name, nodes, playerList, resultList)

        options = self._search_get_best_options(players, name)

        return(options)

    def _search_get_best_options(self, players, name):
        '''
        Return the best draft options for a given round.
        '''

        player_names = []
        team = self.oResults._get_team(name)
        ROUND_INDEX = team.name.count() + 1

        # Get player name(s) for from the appropriate round
        for best in self.best_team:
            team = best._get_team(name)
            keep_idx = team.rnd == ROUND_INDEX
            player_names.append(team.name[keep_idx].ix[0])

        # TODO: raise some type of warning that there was a tie between players
        options = players.name.isin(player_names)

        if not options.any():
            raise ValueError('No options available from Best Teams!\n')

        return(options)

    def _search_player_nodes(self, name, nodes, playerList, resultList):
        '''
        Run through each draft choice for each round to find which draft pick
        would potentially return the maximum points.  The high-water-mark
        algorithm is used to save the best draft selection(s).

        Key-to-Success:
        Being able to project which players will be dropped between turns.
        Conviently it turns out that pre-ranks give a very good estimation.

        TODO:
        Make dynamic for breath and depth - currently just depth
        '''

        try:
            pos = nodes[-1].pop()
        except Exception:
            raise ValueError('No position to pop from nodes!\n')

        # Check for empty nodes after pop
        if nodes[-1] == []:
            nodes.pop()

        # Draft player with max points at given position
        players_av = playerList[-1][playerList[-1].pos == pos]
        options = players_av[players_av.pts == players_av.pts.max()]

        try:
            # TODO: Search Random or Deterministic
            select = random.choice(options.index)
        except Exception:
            print players_av
            raise ValueError('No options available to make a selection from\n')

        # Add player to team
        resultList[-1]._update(name, players_av.ix[select])
        NEXT_ROUND = resultList[-1]._get_team(name).team.count()

        # Check if team is filled or if there are more nodes to search
        if NEXT_ROUND == self.oLeague.rounds:

            # Sanity Check: # of players drafted match roster size
            if resultList[-1]._get_team(name).team.count() != NEXT_ROUND:
                raise ValueError('Did not Draft enought players!\n')

            # Remove results and players from lists
            oResults = resultList.pop()
            playerList.pop()

            # Check if latest team is best
            team_pts = oResults.get_team_pts(name)
            if team_pts > self.best_team[0].get_team_pts(name):
                self.best_team = [oResults]
                print oResults._get_team(name)
            elif team_pts == self.best_team[0].get_team_pts(name):
                self.best_team.append(oResults)

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
        oResults = resultList.pop()

        for pos in nodes[-1]:
            playerList.append(players.copy())
            resultList.append(oResults.copy())

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
            players_to_drop = 2 * (self.oLeague.num_of_teams - FIRST_WAIT - 1)

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

    def __init__(self, result_index):
        '''
        Create an object that has access to draft results.  Use to get results
        by team. Or final results, i.e., who won.
        '''

        self._set_child_constants()
        self.setup(result_index)

    def _set_child_constants(self):
        '''
        Set any constants that should not be changed again here
        '''
        self.SUMMARY_COL = ['pts', 'rnk']
        self.RESULT_COL = ['pick', 'rank', 'rnd', 'team', 'name', 'pos', 'pts']

    def setup(self, result_index):
        '''
        Not recommended but you can reset Draft Results conditions here
        '''

        self.df = pd.DataFrame(index=result_index, columns=self.RESULT_COL)

    def _update(self, team_name, player):
        '''
        Add player to results data frame.  We have to calculate round and
        where to place them.
        '''

        rnd = self.df.team[self.df.team == team_name].count() + 1
        pick_num = self.df.team.count() + 1

        self.df.ix[player.name] = [
                                   pick_num, player['pre'], rnd, team_name,
                                   player['name'], player['pos'], player['pts']
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

    def summarize(self):
        '''
        Analyze draft results once complete
        '''
        self.summary = pd.DataFrame(
                                    index=self.df.team.unique(),
                                    columns=self.SUMMARY_COL
                                   )

        self.summary['pts'] = self.df.groupby('team').pts.sum()
        self.summary.sort(ascending=False)
        self.summary['rnk'] = self.summary.pts.rank(ascending=False)

        return(self.summary)