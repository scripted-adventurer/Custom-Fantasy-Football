# -*- coding: utf-8 -*-
import datetime
import pytz
import os

from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models
from common.current_week import get_current_week
from common.transform_pos import transform_pos
from common.fuzzy_string import encode_name

class Players(CustomView):
  def get(self):
    if 'query' in self.request.args:
      player_name = self.request.args['query']
      phonetic_name = encode_name(player_name)
      # lookup players by phonetic match
      players = [player.data_dict() for player in models.Player.objects(
        phonetic_name__contains=phonetic_name)]
      self.add_response_data('players', players)
      return self.return_json()
    elif 'available' in self.request.args:
      season_year, season_type, week = get_current_week()
      week_field = models.Week(season_type=season_type, season_year=season_year, 
        week=week)
      now = datetime.datetime.now(pytz.utc)
      teams = []
      for game in models.Game.objects(week=week_field, start_time__gt=now):
        teams.append(game.home_team)
        teams.append(game.away_team)
      players = {}
      for player in models.Player.objects(team__in=teams).order_by(
        'name'):
        pos = transform_pos(player.position)
        if pos not in players:
          players[pos] = []
        players[pos].append(player.data_dict())
      self.add_response_data('players', players)
      return self.return_json()
    else:
      self.change_response_status(400)
      self.add_response_error(self.errors.http_400())
      return self.return_json()    