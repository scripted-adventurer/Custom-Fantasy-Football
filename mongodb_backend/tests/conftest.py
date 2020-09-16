import pytest
import json 
import os
import gzip

from mongoengine import connect
from flask import current_app

from flaskr.app import create_app
from flaskr import models 
from flaskr import security 

@pytest.fixture
def app():
  app = create_app(testing=True)

  with app.app_context():
    db = connect('test', 
      host=current_app.config['MONGODB_SETTINGS']['host'], 
      port=current_app.config['MONGODB_SETTINGS']['port'], 
      username=current_app.config['MONGODB_SETTINGS']['username'], 
      password=current_app.config['MONGODB_SETTINGS']['password'])

  # seed the test database with player data (as of the start of the 2020 season)
  with open('tests/players_fixture.json') as players_file:
    players = json.load(players_file)
  for player_info in players.values():
    player = models.Player().custom_json(player_info)
    player.save()
  # and all the game data from 2019 REG 17
  base_path = os.environ['CUSTOM_FF_PATH']
  with open(f"{base_path}/nfl_json/json/schedule/2019.json") as schedule_file:
    schedule = json.load(schedule_file)
  games = schedule["data"]["viewer"]["league"]["games"]["edges"]
  for game_info in games:
    if (game_info["node"]["week"]["seasonType"] == 'REG' and 
      game_info["node"]["week"]["weekValue"] == 17):
      game_path = f"{base_path}/nfl_json/json/games/{game_info['node']['gameDetailId']}.json.gz"
      with gzip.open(game_path) as game_json:
        game_detail = json.load(game_json)
      game = models.Game().custom_json(game_info, game_detail)
      game.save()

  yield app

  db.drop_database('test')

@pytest.fixture
def client(app):
  return app.test_client()    