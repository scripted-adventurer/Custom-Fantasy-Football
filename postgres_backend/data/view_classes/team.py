# -*- coding: utf-8 -*-
from data.view_classes.custom_view import CustomView
import data.models as models

class Team(CustomView):
  def get(self):
    if 'id' in self.request.GET:
      team = models.get_safe('Team', team_id=self.request.GET['id'])
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