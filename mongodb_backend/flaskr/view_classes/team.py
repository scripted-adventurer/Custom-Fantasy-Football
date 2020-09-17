# -*- coding: utf-8 -*-
from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models

class Team(CustomView):
  def get(self):
    if 'id' in self.request.args:
      team = models.Team.objects(team_id=self.request.args['id']).first()
      if not team:
        self.change_response_status(400)
        self.add_response_error(self.errors.bad_data('team ID'))
        return self.return_json()
      self.add_response_data('team', team.data_dict())
      return self.return_json()
    else:
      self.change_response_status(400)
      self.add_response_error(self.errors.http_400())
      return self.return_json()