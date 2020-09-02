# -*- coding: utf-8 -*-
from .league_base import LeagueBase
import data.models as db_models
from .validation import LineupValidation

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
    for player_id in old_lineup:
      if player_id not in new_lineup:
        self.member.lineup_delete(player_id)
    for player_id in new_lineup:
      if player_id not in old_lineup:
        self.member.lineup_add(player_id)
    return self.return_json()