import ffa.config
import ffa.football_players
import ffa.draft_rank
import cProfile as cp

info = ffa.config.State()
oCustom = ffa.football_players.Artificial(info)
oDatabase = ffa.football_players.Database(info)
rank_engine = ffa.draft_rank.RunRanks(info, oCustom)

custom_players = oCustom.set_to_draft()
oCustom.plot_position_points()
previous_players = oDatabase.set_to_draft()
rank_engine.roster_rank_page(page_name='RosterRankLinear')

#rank_engine = ffa.draft_rank.RunRanks(info, oDatabase)
#rank_engine.roster_rank_page(page_name='RosterRankDatabase')
print 'hello'
