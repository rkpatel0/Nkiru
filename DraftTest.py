#import numpy as np;
#import pandas as pd;
import ffa.config
import ffa.find_players

info = ffa.config.State()
players = ffa.find_players.SetPlayers(info)

custom_players = players.get_customDraft()
previous_players = players.get_databaseDraft()

print 'do i get here?\n', previous_players
print 'do i t here?'