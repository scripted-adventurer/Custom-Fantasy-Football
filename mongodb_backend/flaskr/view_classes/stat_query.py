# -*- coding: utf-8 -*-
from mongodb_backend.flaskr import models
from common.current_week import get_current_week

class StatQuery:
  '''The primary engine for calculating player stats based on a League's scoring
  settings.'''
  def __init__(self, scoring_settings, season_year, season_type, week=None):
    self.scoring_settings = scoring_settings
    self.season_year = int(season_year)
    self.season_type = season_type
    self.week = int(week) if week else None
    self.pipeline = []
    self.stats_data = {}
    self.player_id = None
    self.sort = ''
  def _set_week_filter(self):
    if self.week:
      week_filter = {"$match": {"week.season_type": self.season_type, 
        "week.season_year": self.season_year, "week.week": self.week}}
    else:
      week_filter = {"$match": {"week.season_type": self.season_type, 
        "week.season_year": self.season_year}}
    self.pipeline.append(week_filter)
  def _filter_to_player_stats(self):
    self.pipeline.append({"$project": {"plays": 1, "_id": 0}})
    self.pipeline.append({"$unwind": "$plays"})
    self.pipeline.append({"$project": {"aggregate": "$plays.aggregate", 
      "player_stats": "$plays.player_stats"}})
    self.pipeline.append({"$unwind": "$player_stats"})
  def _build_conditions(self, stat_conditions):
    condition_map = {'=': "$eq", '>': "$gt", '<': "$lt", '>=': "$gte", '<=': 
      "$lte"}
    conditions = []
    for condition in stat_conditions:
      this_condition = {}
      comparison = condition_map[condition['comparison']]
      this_condition[comparison] = [f"$aggregate.{condition['field']}", 
        condition['value']]
      conditions.append(this_condition)
    return conditions    
  def _calculate_stats(self):
    scoring_filter = {"$project": {"id": "$player_stats.id"}}
    for stat in self.scoring_settings:
      if stat['conditions']:
        conditions = self._build_conditions(stat['conditions'])
        stat_filter = {"$cond": {"if": {"$and": conditions}, "then": 
          f"$player_stats.{stat['field']}", "else": "$$REMOVE"}}
      else:
        stat_filter = f"$player_stats.{stat['field']}" 
      scoring_filter["$project"][stat["name"]] = stat_filter
    self.pipeline.append(scoring_filter)  
  def _filter_to_single_player(self):
    self.pipeline.append({"$match": {"id": f"{self.player_id}"}})
  def _remove_unmatched_stat_rows(self):
    stat_filters = []
    for stat in self.scoring_settings:
      stat_filters.append({f"{stat['name']}": {"$exists": True}})
    self.pipeline.append({"$match": {"$or": stat_filters}})
  def _aggregate_stats_by_player(self):
    stat_filters = {"_id": "$id"}
    for stat in self.scoring_settings:
      stat_filters[f"{stat['name']}"] = {"$sum": f"${stat['name']}"}
    self.pipeline.append({"$group": stat_filters})
  def _remove_empty_stats(self):
    stat_filters = {"_id": 0, "id": "$_id"}
    for stat in self.scoring_settings:
      stat_filters[f"{stat['name']}"] = {"$cond": {"if": {"$ne": 
        [f"${stat['name']}", 0]}, "then": f"${stat['name']}", "else": "$$REMOVE"}}
    self.pipeline.append({"$project": stat_filters})    
  def _run_pipeline(self):
    for row in models.Game.objects().aggregate(self.pipeline):
      self.stats_data[row['id']] = row
  def _add_player_data(self):
    for player_row in self.stats_data.values():
      this_player = models.Player.objects(player_id=player_row['id']).first()
      if this_player:
        player_row['name'] = this_player.name 
        player_row['team'] = this_player.team.team_id
        player_row['position'] = this_player.position
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
    if 'sort' in kwargs.keys():
      self.sort = kwargs['sort'].lower()
    return self  
  def get(self, as_list=True):
    self._set_week_filter()
    self._filter_to_player_stats()
    self._calculate_stats()
    if self.player_id:
      self._filter_to_single_player()
    self._remove_unmatched_stat_rows()
    self._aggregate_stats_by_player()
    self._remove_empty_stats()
    self._run_pipeline()
    self._add_player_data()
    self._add_scores()
    if as_list:
      self.stats_data = list(self.stats_data.values())
      self._sort()  
    return self.stats_data