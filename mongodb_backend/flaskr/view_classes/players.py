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
    if 'query' in self.request.GET:
      player_name = self.request.GET['query']
      players = []
      with connection.cursor() as cursor:
        cursor.execute('''SELECT player_id, name, team, position, difference(name, %s)
        FROM data_player
        WHERE difference(name, %s) > 3 AND status='ACT'
        ORDER BY 5 DESC''', [player_name, player_name])
        for row in cursor.fetchall():
          player_dict = {'id': row[0], 'name': row[1], 'team': row[2], 
            'position': row[3]}
          players.append(player_dict)
      self.add_response_data('players', players)
      return self.return_json()
    elif 'available' in self.request.GET:
      season_year, season_type, week = db_models.get_current_week()
      now = datetime.datetime.now(pytz.utc)
      teams = []
      for game in db_models.Game.objects.filter(season_type=season_type, 
        season_year=season_year, week=week, start_time__gt=now):
        teams.append(game.home_team)
        teams.append(game.away_team)
      players = {}
      for player in db_models.Player.objects.filter(team__in=teams).order_by(
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