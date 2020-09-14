# -*- coding: utf-8 -*-
import datetime
import os

import data.models as db_models

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Errors = common.Errors
Utility = common.Utility

class LineupValidation:
  '''Contains all the logic to validate a user's submitted lineup, including
  checking all players are valid, all league settings were met, and no locked 
  players were changed.'''
  def __init__(self, old_lineup, new_lineup, league_positions):
    # maps each nfldb position to its position group (used in League)
    self.position_map = {'CB': 'DB', 'DB': 'DB', 'FS': 'DB', 'SAF': 'DB', 'SS': 
      'DB', 'DE': 'DL', 'DT': 'DL', 'NT': 'DL', 'ILB': 'LB', 'LB': 'LB', 'MLB': 
      'LB', 'OLB': 'LB', 'C': 'OL', 'LS': 'OL', 'OG': 'OL', 'OT': 'OL', 'QB': 
      'QB', 'FB': 'RB', 'RB': 'RB', 'WR': 'WR', 'TE': 'TE', 'K': 'K', 'P': 'P'}
    self.old_lineup = old_lineup
    self.new_lineup = new_lineup
    self.league_positions = league_positions
    self.new_player_objects = []
    self.changed = []
    self.errors = []
  def get_changes(self):
    for player_id in self.old_lineup:
      if player_id not in self.new_lineup:
        self.changed.append(player_id)
    for player_id in self.new_lineup:
      if player_id not in self.old_lineup:
        self.changed.append(player_id)
  def check_players(self):      
    for player_id in self.new_lineup:
      player = db_models.get_safe('Player', player_id=player_id)
      if not player:
        self.errors.append(Errors().unrecognized(player_id))
      else:
        self.new_player_objects.append(player)
  def check_positions(self):
    self.lineup_positions = {}
    for player in self.new_player_objects:
      pos = Utility().transform_pos(player.position)
      if pos in self.lineup_positions:
        self.lineup_positions[pos] += 1
      else:
        self.lineup_positions[pos] = 1
    if self.league_positions != self.lineup_positions:
      self.errors.append(f"Lineup does not match league's lineup settings. " +
      f"Submitted: {self.lineup_positions}. League settings: {self.league_positions}")
  def check_locked(self):
    for player_id in self.changed:
      player = db_models.get_safe('Player', player_id=player_id)
      if player.is_locked():
        self.errors.append(Errors().locked_player(player_id))
  def run(self): 
    self.get_changes()
    self.check_players()
    # no need to run further tests if errors are already present
    if not self.errors:
      self.check_positions()
    if not self.errors:
      self.check_locked()
    return {'valid': True if not self.errors else False, 'errors': self.errors}     

class ScoringSettingsValidation:
  '''Validation for the league update scoring settings request. Ensures the 
  various submitted parameters conform to the enumerated types defined in 
  models.py.'''
  def __init__(self):
    self.errors = []
    self.param_map = {'name': {'type': 'str', 'enum': None}, 
      'field': {'type': 'str', 'enum': db_models.StatField.values}, 
      'comparison': {'type': 'str', 'enum': db_models.StatCondition.Comparison.values}, 
      'value': {'type': 'int', 'enum': None}, 
      'multiplier': {'type': 'float', 'enum': None}}
  def _correct_type(self, param, value):
    param_type = self.param_map[param]['type']
    if param_type == 'str':
      return True
    elif param_type == 'int':
      try:
        int(value)
        return True
      except ValueError:
        return False 
    elif param_type == 'float':
      try:
        float(value)
        return True
      except ValueError:
        return False
  def _correct_value(self, param, value):
    param_enum = self.param_map[param]['enum']
    if param_enum and value not in param_enum:
      return False
    else:
      return True
  def _check_stat_object(self, param, stat_object):
    if (param not in stat_object or not self._correct_type(param, stat_object[param]) 
      or not self._correct_value(param, stat_object[param])):
      self.errors.append(Errors().bad_data(param))
  def check(self, scoring_settings):
    for stat in scoring_settings:
      for param in ['name', 'field', 'multiplier']:
        self._check_stat_object(param, stat)
      if 'conditions' in stat and stat['conditions']:
        for condition in stat['conditions']: 
          for param in ['field', 'comparison', 'value']:
            self._check_stat_object(param, condition)
    return {'valid': True if not self.errors else False, 'errors': self.errors}  

class LineupSettingsValidation:
  '''Validation for the user supplied parameters in the league update
  lineup settings request. Ensures positions are valid nfldb positions and 
  each position has a valid integer count.'''
  def __init__(self):
    self.errors = []
  def check(self, lineup_settings):
    positions = {'DB', 'DL', 'K', 'LB', 'OL', 'P', 'QB', 'RB', 'TE', 'WR'}
    for position, count in lineup_settings.items():
      if position in positions:
        try:
          int(count)
        except ValueError:
          self.errors.append(Errors().unrecognized(position))
      else:
        self.errors.append(Errors().unrecognized(position))
    return {'valid': True if not self.errors else False, 'errors': self.errors}

class SeasonWeekValidation:
  def __init__(self):
    self.param_bounds = {'season_type': db_models.SeasonType.values,
      'season_year': range(2011, datetime.datetime.now().year + 1),
      'week': range(0, 18)}
  def check_season_type(self, season_type):
    if str(season_type) not in self.param_bounds['season_type']:
      return False
    return True  
  def check_season_year(self, season_year):
    try:
      int(season_year)
      if int(season_year) not in self.param_bounds['season_year']:
        return False
      return True  
    except ValueError:
      return False
  def check_week(self, week):
    try:
      int(week)
      if int(week) not in self.param_bounds['week']:
        return False
      return True  
    except ValueError:
      return False        