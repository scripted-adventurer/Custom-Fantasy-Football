from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models
from mongodb_backend.flaskr.view_classes.validation import SeasonWeekValidation
from common.current_week import get_current_week

class LeagueBase(CustomView):
  def __init__(self, request, current_user, league_name):
    self.league_name = league_name
    super().__init__(request, current_user)
  def check_member(self):
    self.league = models.League.objects(name=self.league_name).first()
    self.member = models.Member.objects(league=self.league, user=self.user).first()
    if not self.league or not self.member:
      self.change_response_status(400)
      self.add_response_error(self.errors.bad_league())
      return False
    return True
  def check_season_week(self):
    # default to the current week but use user-provided values if they are present
    self.season_year, self.season_type, self.week = get_current_week()
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