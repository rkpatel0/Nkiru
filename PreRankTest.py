import ffa.config
import ffa.football_players
import ffa.draft_rank
import cProfile as cp

oState = ffa.config.State(profile={'year': '2013'})
oCustom = ffa.football_players.Artificial(oState)
oDatabase = ffa.football_players.Database(oState)
rank_engine = ffa.draft_rank.RunRanks(oState, oCustom)

custom_players = oCustom.set_to_draft()
previous_players = oDatabase.set_to_draft()

#oCustom.plot_position_points()
#atabase.plot_position_points()

#rank_engine.roster_rank_page(page_name='RosterRankLinear2')
rank_engine = ffa.draft_rank.RunRanks(oState, oDatabase)
rank_engine.pps_rank_page(page_name='PPR2013')
#rank_engine.roster_rank_page(page_name='Roster2013')

print 'hello'