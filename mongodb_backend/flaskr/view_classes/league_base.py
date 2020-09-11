from .custom_view import CustomView
from flaskr import models
from .validation import SeasonWeekValidation

class LeagueBase(CustomView):
  def __init__(self, request, login_required, league_name):
    self.league_name = league_name
    super().__init__(request, login_required)
  def check_member(self):
    self.league = db_models.get_safe('League', name=self.league_name)
    self.member = db_models.get_safe('Member', league=self.league, user=self.user)
    if not self.league or not self.member:
      self.change_response_status(400)
      self.add_response_error(self.errors.bad_league())
      return False
    return True
  def check_season_week(self):
    # default to the current week but use user-provided values if they are present
    self.season_year, self.season_type, self.week = db_models.get_current_week()
    custom_week = False
    if 'seasonType' in self.request.GET:
      self.season_type = self.request.GET['seasonType']
      custom_week = True
    if 'seasonYear' in self.request.GET:
      self.season_year = self.request.GET['seasonYear']
      custom_week = True
    if 'week' in self.request.GET:  
      self.week = self.request.GET['week']
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