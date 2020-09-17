# -*- coding: utf-8 -*-
from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models

class Player(CustomView):
  def get(self):
    if 'id' in self.request.args:
      player = models.Player.objects(player_id=self.request.args['id']).first()
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