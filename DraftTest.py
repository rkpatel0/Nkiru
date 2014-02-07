'''
Simple Tester for Bring Up
===============================================================================
'''

#import numpy as np;
#import pandas as pd;
import ffa.config
import ffa.find_players
import ffa.draft
import cProfile as cp

info = ffa.config.State()
players = ffa.find_players.SetPlayers(info)

custom_players = players.get_customDraft()
#players.plotPtsByPos()
previous_players = players.get_databaseDraft()
#players.plotPtsByPos()

draft = ffa.draft.Simulator(info.league, previous_players)
#cp.run('draft.live_draft()')
draft.live_draft()

#print 'do i get here?\n', custom_players
print draft.results.df
print draft.results.summary
print draft.results._get_team('G')