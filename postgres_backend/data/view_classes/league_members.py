# -*- coding: utf-8 -*-
import os

from .league_base import LeagueBase
import data.models as db_models

class LeagueMembers(LeagueBase):
  def post(self):
    league = db_models.get_safe('League', name=self.league_name)
    if not league:
      self.change_response_status(400)
      self.add_response_error(self.errors.bad_data('league name'))
      return self.return_json()
    required_params = ['password']
    if not self.check_required_params(required_params):
      return self.return_json()
    password = self.get_request_data('password')
    if not db_models.compare_hash(league.password, password):
      self.add_response_error(self.errors.bad_data('password'))
      self.change_response_status(400)
      return self.return_json()
    else:
      db_models.Member.objects.create(user=self.user, league=league)
      return self.return_json()