# -*- coding: utf-8 -*-
from data.view_classes.custom_view import CustomView
import data.models as models

class Player(CustomView):
  def get(self):
    if 'id' in self.request.GET:
      player = models.get_safe('Player', player_id=self.request.GET['id'])
      if not player:
        self.change_response_status(400)
        self.add_response_error(self.errors.bad_data('player ID'))
        return self.return_json()
      self.add_response_data('player', player.data_dict())
      return self.return_json()
    else:
      self.change_response_status(400)
      self.add_response_error(self.errors.http_400())
      return self.return_json()