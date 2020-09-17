# -*- coding: utf-8 -*-
from data.view_classes.custom_view import CustomView
import data.models as models

class Teams(CustomView):
  def get(self):
    teams = [team.data_dict() for team in models.Team.objects.filter(
      active=True).order_by('team_id')]
    self.add_response_data('teams', teams)
    return self.return_json()