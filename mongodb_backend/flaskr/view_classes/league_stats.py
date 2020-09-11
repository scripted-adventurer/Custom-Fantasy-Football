# -*- coding: utf-8 -*-
from .league_base import LeagueBase
from flaskr import models
from .validation import SeasonWeekValidation
from .stat_query import StatQuery

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
    if 'playerId' in self.request.GET:
      stats.filter(player_id=self.request.GET['playerId'])
    if 'sort' in self.request.GET:
      stats.filter(sort=self.request.GET['sort'])
    self.add_response_data('stats', stats.get())
    return self.return_json()