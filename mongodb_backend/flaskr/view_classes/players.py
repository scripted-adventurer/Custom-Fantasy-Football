# -*- coding: utf-8 -*-
import datetime
import pytz
import os

from .custom_view import CustomView
from flaskr import models

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Utility = common.Utility

class Players(CustomView):
  def get(self):
    if 'query' in self.request.args:
      player_name = self.request.args['query']
      players = []
      # lookup players by double metaphone matches 
      self.add_response_data('players', players)
      return self.return_json()
    elif 'available' in self.request.args:
      season_year, season_type, week = models.get_current_week()
      now = datetime.datetime.now(pytz.utc)
      teams = []
      for game in models.Game.objects(season_type=season_type, 
        season_year=season_year, week=week, start_time__gt=now):
        teams.append(game.home_team)
        teams.append(game.away_team)
      players = {}
      for player in models.Player.objects(team__in=teams).order_by(
        'name'):
        pos = Utility().transform_pos(player.position)
        if pos not in players:
          players[pos] = []
        players[pos].append(player.data_dict())
      self.add_response_data('players', players)
      return self.return_json()
    else:
      self.change_response_status(400)
      self.add_response_error(self.errors.http_400())
      return self.return_json()    