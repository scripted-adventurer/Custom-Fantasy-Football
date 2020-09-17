# -*- coding: utf-8 -*-
from mongodb_backend.flaskr.view_classes.league_base import LeagueBase
from mongodb_backend.flaskr.view_classes.validation import LineupValidation

class LeagueMemberLineup(LeagueBase):
  def get(self):
    if not self.check_member():
      return self.return_json()
    self.add_response_data('lineup', self.member.get_lineup())
    return self.return_json()
  def put(self):
    if not self.check_member():
      return self.return_json()
    required_params = ['lineup']
    if not self.check_required_params(required_params):
      return self.return_json()
    old_lineup = [player['id'] for player in self.member.get_lineup()]
    new_lineup = self.get_request_data('lineup')
    league_settings = self.league.get_lineup_settings()
    lineup_val = LineupValidation(old_lineup, new_lineup, league_settings).run()
    if not lineup_val['valid']:
      for error in lineup_val['errors']:
        self.add_response_error(error)
      self.change_response_status(400)
      return self.return_json()
    self.member.lineup_delete()
    self.member.lineup_add(new_lineup)
    return self.return_json()