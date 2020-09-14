# -*- coding: utf-8 -*-
from .custom_view import CustomView
from flaskr import models
from .validation import SeasonWeekValidation

class Games(CustomView):
  def get(self):
    # default to the current week but use user-provided values if they are present
    season_year, season_type, week = models.get_current_week()
    custom_week = False
    if 'seasonType' in self.request.args:
      season_type = self.request.args['seasonType']
      custom_week = True
    if 'seasonYear' in self.request.args:
      season_year = self.request.args['seasonYear']
      custom_week = True
    if 'week' in self.request.args:  
      week = self.request.args['week']
      custom_week = True
    if custom_week:
      valid = True
      if not SeasonWeekValidation().check_season_type(season_type):
        self.add_response_error(self.errors.bad_data('season type'))
        valid = False
      if not SeasonWeekValidation().check_season_year(season_year):
        self.add_response_error(self.errors.bad_data('season year'))
        valid = False
      if not SeasonWeekValidation().check_week(week):
        self.add_response_error(self.errors.bad_data('week'))
        valid = False
      if not valid:
        self.change_response_status(400)
        return self.return_json()
    week = models.Week(season_type=season_type, season_year=int(season_year), 
      week=int(week))
    games = [game.data_dict() for game in models.Game.objects(week=week)] 
    self.add_response_data('games', games)
    return self.return_json()