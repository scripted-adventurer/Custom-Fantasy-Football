# -*- coding: utf-8 -*-
import os

from mongodb_backend.flaskr.view_classes.league_base import LeagueBase
from mongodb_backend.flaskr import models
from common.hashing import generate_hash

class LeagueMembers(LeagueBase):
  def post(self):
    league = models.League.objects(name=self.league_name).first()
    if not league:
      self.change_response_status(400)
      self.add_response_error(self.errors.bad_data('league name'))
      return self.return_json()
    required_params = ['password']
    if not self.check_required_params(required_params):
      return self.return_json()
    password = self.get_request_data('password')
    password_hash = generate_hash(password)
    print(password)
    print(password_hash)
    print(league.password)
    if password_hash != league.password:
      self.add_response_error(self.errors.bad_data('password'))
      self.change_response_status(400)
      return self.return_json()
    else:
      models.Member.objects(user=self.user, league=league).save()
      return self.return_json()