'''
Simple Tester for Bring Up
===============================================================================
'''

#import numpy as np;
#import pandas as pd;
import ffa.config
import ffa.football_players
import ffa.draft
import ffa.draft_rank
import cProfile as cp

info = ffa.config.State()
oCustom = ffa.football_players.Artificial(info)
oDatabase = ffa.football_players.Database(info)
custom_players = oCustom.set_to_draft()
previous_players = oDatabase.set_to_draft()

draft = ffa.draft.Simulator(info.league, previous_players)
#draft.live_draft()

rank_engine = ffa.draft_rank.PreRank(info, previous_players)
rank_engine.generate_preranks()

print 'hello'
#cp.run('draft.live_draft()')


#print 'do i get here?\n', custom_players
#print draft.results.df
#print draft.results.summary
#print draft.results._get_team('G')
'''
name                                                                    
Adrian Peterson     RB  298        1      1    1    1    1    1   1    A
Aaron Rodgers       QB  283       11      2    2    2    2    2   1    B
Arian Foster        RB  251        3      7    3    3    3    3   1    C
Doug Martin         RB  247        2      8    8    4    4    4   1    D
Marshawn Lynch      RB  237        4     11   10    9    5    5   1    E
Alfred Morris       RB  234        5     12   11   10    8    6   1    Z
Drew Brees          QB  269       10      3    4    5    6    7   1    G
Robert Griffin III  QB  266       23      4    5    6    7    8   1    H
Ray Rice            RB  209        6     14   12   11   10    9   2    H
Jamaal Charles      RB  204       14     15   15   15   15   10   2    G
Tom Brady           QB  264       12      5    6    7    9   11   2    Z
Cam Newton          QB  263       20      6    7    8   12   12   2    E
Peyton Manning      QB  243       27      9    9   13   13   13   2    D
Matt Ryan           QB  237       32     10   14   14   14   14   2    C
C.J. Spiller        RB  204        9     16   13   12   11   15   2    B
Russell Wilson      QB  231       52     13   16   16   16   16   2    A
'''