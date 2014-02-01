'''
Simple Tester for Bring Up
===============================================================================
'''

#import numpy as np;
#import pandas as pd;
import ffa.config
import ffa.find_players

info = ffa.config.State()
players = ffa.find_players.SetPlayers(info)

custom_players = players.get_customDraft()
players.plotPtsByPos()
previous_players = players.get_databaseDraft()
players.plotPtsByPos()


print 'do i get here?\n', custom_players
print 'do i t here?'