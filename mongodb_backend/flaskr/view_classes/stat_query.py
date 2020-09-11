# -*- coding: utf-8 -*-
from flaskr import models

class StatQuery:
  '''The primary engine for calculating player stats based on a League's scoring
  settings.'''
  def __init__(self, scoring_settings):
    self.scoring_settings = scoring_settings
    self.season_year, self.season_type, self.week = db_models.get_current_week()
    self.stats_data = {}
    self.season_week_cond = ''
    self.player_id = ''
    self.add_scores = False
    self.sort = ''
  def _build_season_week(self):
    self.season_week_cond = (f"data_game.season_type='{self.season_type}' AND "
    f"data_game.season_year={self.season_year} AND data_game.week={self.week} ")
  def _build_conditions(self, stat):
    conditions = []
    # if the stat has no specified conditions, add the default (stat != 0)
    if 'conditions' not in stat or not stat['conditions']:
      conditions.append(f"AND data_playplayer.{stat['field']} != 0")
    else:  
      for cond in stat['conditions']:
        conditions.append(f"AND data_playplayer.{cond['field']}"
        f"{cond['comparison']}{cond['value']}")
    if self.player_id:
      conditions.append(f"AND data_player.player_id = '{self.player_id}'")
    return ' '.join(conditions)
  def _get_stat(self, stat):
    conditions = self._build_conditions(stat)
    query = (f"SELECT data_player.player_id, data_player.name, data_player.team, "
    f"data_player.position, SUM(data_playplayer.{stat['field']}) "
    f"FROM data_playplayer "
    f"JOIN data_player ON data_playplayer.player_id = data_player.player_id "
    f"JOIN data_play ON data_playplayer.play_id = data_play.id "
    f"JOIN data_drive ON data_play.drive_id = data_drive.id "
    f"JOIN data_game ON data_drive.game_id = data_game.game_id "
    f"WHERE {self.season_week_cond} {conditions} "
    f"GROUP BY 1")
    with connection.cursor() as cursor:
      cursor.execute(query)
      for row in cursor.fetchall():
        if row[0] not in self.stats_data:
          # add player info
          self.stats_data[row[0]] = {}
          self.stats_data[row[0]]['id'] = row[0]
          self.stats_data[row[0]]['name'] = row[1]
          self.stats_data[row[0]]['team'] = row[2]
          self.stats_data[row[0]]['position'] = row[3]
        self.stats_data[row[0]][stat['name']] = row[4]   
  def _add_scores(self):
    stat_values = {}
    for stat in self.scoring_settings:
      stat_values[stat['name']] = stat['multiplier']
    for player_row in self.stats_data.values():
      player_row['total'] = 0
      for stat, value in stat_values.items():
        if stat in player_row:
          player_row['total'] += player_row[stat] * value
      player_row['total'] = round(player_row['total'], 2)    
  def _sort(self):
    if self.sort == 'asc':
      self.stats_data.sort(key=lambda row: row['total'])
    else:
      self.stats_data.sort(key=lambda row: row['total'], reverse=True)  
  def filter(self, **kwargs):
    if 'player_id' in kwargs.keys():
      self.player_id = kwargs['player_id']
    if 'season_type' in kwargs.keys():
      self.season_type = kwargs['season_type']
    if 'season_year' in kwargs.keys():
      self.season_year = kwargs['season_year']
    if 'week' in kwargs.keys():
      self.week = kwargs['week']
    if 'sort' in kwargs.keys():
      self.sort = kwargs['sort'].lower()
    return self  
  def get(self, as_list=True):
    self._build_season_week()
    for stat in self.scoring_settings:
      self._get_stat(stat)
    self._add_scores()
    if as_list:
      self.stats_data = list(self.stats_data.values())
      self._sort()  
    return self.stats_data