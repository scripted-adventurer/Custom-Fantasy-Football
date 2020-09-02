# -*- coding: utf-8 -*-
from .custom_view import CustomView
import data.models as db_models

class Teams(CustomView):
  def get(self):
    teams = [team.data_dict() for team in db_models.Team.objects.filter(
      active=True).order_by('team_id')]
    self.add_response_data('teams', teams)
    return self.return_json()