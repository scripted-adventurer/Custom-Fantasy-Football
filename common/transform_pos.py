# -*- coding: utf-8 -*-

'''Map each position found in the NFL.com stats player information to its 
position grouping. Ex. CB, DB, FS, SAF, and SS are all counted as defensive backs
(DB) for league lineup purposes.'''

POSITION_MAP = {'CB': 'DB', 'DB': 'DB', 'FS': 'DB', 'SAF': 'DB', 
  'SS': 'DB', 'DE': 'DL', 'DL': 'DL', 'DT': 'DL', 'NT': 'DL', 'ILB': 'LB', 
  'LB': 'LB', 'MLB': 'LB', 'OLB': 'LB', 'C': 'OL', 'LS': 'OL', 'OG': 'OL', 
  'OL': 'OL', 'OT': 'OL', 'QB': 'QB', 'FB': 'RB', 'RB': 'RB', 'WR': 'WR', 
  'TE': 'TE', 'K': 'K', 'P': 'P'}

def transform_pos(position):
  return POSITION_MAP.get(position, 'UNK')