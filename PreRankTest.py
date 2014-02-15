import ffa.config
import ffa.football_players
import ffa.draft
import ffa.draft_rank
import ffa.report
import cProfile as cp

info = ffa.config.State()
custom = ffa.football_players.Artificial(info)
database = ffa.football_players.Database(info)
custom_players = custom.players_to_draft()
previous_players = database.players_to_draft()

draft = ffa.draft.Simulator(info.league, previous_players)
rank_engine = ffa.draft_rank.PreRank(info, previous_players)
rank_engine.get_pre_ranks()

tmp = ffa.report.ReportGen(info, previous_players, rank_engine)
tmp.update_pages()
tmp.close_pages()

print 'hello'
