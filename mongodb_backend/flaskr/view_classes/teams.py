# -*- coding: utf-8 -*-
from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models

class Teams(CustomView):
  def get(self):
    teams = [team.data_dict() for team in models.Team.objects(
      active=True).order_by('team_id')]
    self.add_response_data('teams', teams)
    return self.return_json()