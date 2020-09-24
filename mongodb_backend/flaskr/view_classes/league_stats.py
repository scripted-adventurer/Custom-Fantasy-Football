# -*- coding: utf-8 -*-
from mongodb_backend.flaskr.view_classes.league_base import LeagueBase
from mongodb_backend.flaskr import models
from mongodb_backend.flaskr.view_classes.stat_query import StatQuery

class LeagueStats(LeagueBase):
  def get(self):
    if not self.check_member():
      return self.return_json()
    # default to the current week but use user-provided values if they are present
    if not self.check_season_week():
      return self.return_json()
    scoring_settings = self.league.get_scoring_settings()
    stats = StatQuery(scoring_settings=scoring_settings)
    stats.filter(season_type=self.season_type, season_year=self.season_year, 
      week=self.week)
    if 'playerId' in self.request.args:
      stats.filter(player_id=self.request.args['playerId'])
    if 'sort' in self.request.args:
      stats.filter(sort=self.request.args['sort'])
    self.add_response_data('stats', stats.get())
    return self.return_json()