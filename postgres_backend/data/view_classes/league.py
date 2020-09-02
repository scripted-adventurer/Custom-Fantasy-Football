# -*- coding: utf-8 -*-
from .league_base import LeagueBase
import data.models as db_models
from .validation import LineupSettingsValidation, ScoringSettingsValidation

class League(LeagueBase): 
  def get(self):
    if not self.check_member():
      return self.return_json()
    else:
      self.add_response_data('members', self.league.get_members())
      self.add_response_data('lineup_settings', self.league.get_lineup_settings())
      self.add_response_data('scoring_settings', self.league.get_scoring_settings())
      return self.return_json()  
  def patch(self):
    if not self.check_member():
      return self.return_json()
    if not self.member.is_admin():
      self.add_response_error(self.errors.not_admin())
      self.change_response_status(403)
      return self.return_json()  
    league_property = self.get_request_data('property')
    data = self.get_request_data('data')
    if league_property == 'password':
      required_params = ['password1', 'password2']
      if not self.check_required_params(required_params, data):
        return self.return_json()
      password1 = data['password1']
      password2 = data['password2']
      if password1 != password2:
        self.add_response_error(self.errors.unmatched_passwords())
        self.change_response_status(400)
        return self.return_json()
      else:  
        self.league.set_password(password1)
        return self.return_json()
    elif league_property == 'lineup_settings':  
      if not isinstance(data, dict):
        self.add_response_error(self.errors.bad_data('data'))
        self.change_response_status(400)
        return self.return_json()
      input_val = LineupSettingsValidation().check(data)
      if not input_val['valid']:
        for error in input_val['errors']:
          self.add_response_error(error)
        self.change_response_status(400)
        return self.return_json() 
      else:
        self.league.set_lineup_settings(data)
        return self.return_json() 
    elif league_property == 'scoring_settings': 
      if not isinstance(data, list):
        self.add_response_error(self.errors.bad_data('data'))
        self.change_response_status(400)
        return self.return_json()
      input_val = ScoringSettingsValidation().check(data)
      if not input_val['valid']:
        for error in input_val['errors']:
          self.add_response_error(error)
        self.change_response_status(400)
        return self.return_json()
      else:
        self.league.set_scoring_settings(data)
        return self.return_json()
    else:
      self.add_response_error(self.errors.bad_data('property'))
      self.change_response_status(400)
      return self.return_json()