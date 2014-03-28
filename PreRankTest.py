import ffa.config
import ffa.football_players
import ffa.draft_rank
import cProfile as cp

oState = ffa.config.State(database={'year': '2013'})
oCustom = ffa.football_players.Artificial(oState)
oDatabase = ffa.football_players.Database(oState)
rank_engine = ffa.draft_rank.RunRanks(oState, oCustom)

custom_players = oCustom.set_to_draft()
previous_players = oDatabase.set_to_draft()

#oCustom.plot_position_points()
#database.plot_position_points()

rank_engine = ffa.draft_rank.RunRanks(oState, oDatabase)

#rank_engine.get_rank_page(page_name='tmp')
rank_engine.pps_report(page_name='tmp2')

print 'hello'