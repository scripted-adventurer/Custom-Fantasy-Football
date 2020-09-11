# -*- coding: utf-8 -*-
import os

from .league_base import LeagueBase
from flaskr import models

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Utility = common.Utility

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
    password_hash = Utility().custom_hash(password)
    if password_hash != league.password:
      self.add_response_error(self.errors.bad_data('password'))
      self.change_response_status(400)
      return self.return_json()
    else:
      db_models.Member.objects.create(user=self.user, league=league)
      return self.return_json()