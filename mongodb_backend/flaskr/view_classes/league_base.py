from .custom_view import CustomView
from flaskr import models
from .validation import SeasonWeekValidation

class LeagueBase(CustomView):
  def __init__(self, request, current_user, league_name):
    self.league_name = league_name
    super().__init__(request, current_user)
  def check_member(self):
    self.league = models.get_safe('League', name=self.league_name)
    self.member = models.get_safe('Member', league=self.league, user=self.user)
    if not self.league or not self.member:
      self.change_response_status(400)
      self.add_response_error(self.errors.bad_league())
      return False
    return True
  def check_season_week(self):
    # default to the current week but use user-provided values if they are present
    self.season_year, self.season_type, self.week = models.get_current_week()
    custom_week = False
    if 'seasonType' in self.request.args:
      self.season_type = self.request.args['seasonType']
      custom_week = True
    if 'seasonYear' in self.request.args:
      self.season_year = self.request.args['seasonYear']
      custom_week = True
    if 'week' in self.request.args:  
      self.week = self.request.args['week']
      custom_week = True
    if custom_week:
      valid = True
      if not SeasonWeekValidation().check_season_type(self.season_type):
        self.add_response_error(self.errors.bad_data('season type'))
        valid = False
      if not SeasonWeekValidation().check_season_year(self.season_year):
        self.add_response_error(self.errors.bad_data('season year'))
        valid = False
      if not SeasonWeekValidation().check_week(self.week):
        self.add_response_error(self.errors.bad_data('week'))
        valid = False
      if not valid:
        self.change_response_status(400)
        return False 
    return True    