# -*- coding: utf-8 -*-
import gzip
import json
import argparse
import os
import datetime

from mongoengine import connect

from mongodb_backend.flaskr import models
from mongodb_backend.flaskr.config import SETTINGS, INCLUDED_SEASONS

class SyncDB:
  '''Updates the MongoDB instance pointed to in settings.py with all the stats
  and player info found in the nfl_json folder (using the data models defined in 
  models.py).'''
  def __init__(self):
    self.base_path = os.environ['CUSTOM_FF_PATH']
    self.teams_path = f"{self.base_path}/nfl_json/json/teams.json"
    self.players_path_main = f"{self.base_path}/nfl_json/json/currentPlayers.json"
    self.players_path_test = (f"{self.base_path}/mongodb_backend/tests/fixtures/"
      f"players.json")
    connect(SETTINGS['MONGODB_SETTINGS']['db'], 
      host=SETTINGS['MONGODB_SETTINGS']['host'], 
      port=SETTINGS['MONGODB_SETTINGS']['port'], 
      username=SETTINGS['MONGODB_SETTINGS']['username'], 
      password=SETTINGS['MONGODB_SETTINGS']['password'])
  def update_teams_from_file(self, teams_path):
    with open(teams_path) as teams_file:
      teams = json.load(teams_file)
    for team_info in teams["teams"]:
      if not models.Team.objects(team_id=team_info["id"]).first():
        team = models.Team().custom_json(team_info)
        team.save()
  def update_players_from_file(self, players_path):
    with open(players_path) as players_file:
      players = json.load(players_file)
    for player_info in players.values():
      if not models.Player.objects(player_id=player_info["id"]).first():
        player = models.Player().custom_json(player_info)
        player.save()
  def _game_is_updated(self, game_id, game_path):
    # check if the database has been updated since the last time the JSON file was
    json_update_time = datetime.datetime.utcfromtimestamp(
      os.path.getmtime(game_path))
    db_row = models.Game.objects(game_id=game_id).first()
    if not db_row:
      return False
    if db_row.modified_at > json_update_time:
      return True 
    else:
      return False
  def _update_game(self, game_info, game_path):
    with gzip.open(game_path) as game_json:
      game_detail = json.load(game_json)
    game = models.Game().custom_json(game_info, game_detail)
    game.save()
  def update_games_test(self):
    # send all the data in the games test fixture to the test database
    with open(f"{self.base_path}/mongodb_backend/tests/fixtures/2019.json") as schedule_file:
      schedule = json.load(schedule_file)
    games = schedule["data"]["viewer"]["league"]["games"]["edges"]
    for game_info in games:
      game_id = game_info["node"]["gameDetailId"]
      game_path = f"{self.base_path}/mongodb_backend/tests/fixtures/{game_id}.json.gz"
      self._update_game(game_info, game_path)
  def update_games_main(self):
    # check for updates for any games falling into the seasons specified in settings
    # and push updates as needed
    for year, phases in INCLUDED_SEASONS.items():
      print(f"Checking for updates in games collection in database for {year}...")
      with open(f"{self.base_path}/nfl_json/json/schedule/{year}.json") as schedule_file:
        schedule = json.load(schedule_file)
      games = schedule["data"]["viewer"]["league"]["games"]["edges"]
      for game_info in games:
        if (game_info["node"]["gameDetailId"] and game_info["node"]["week"]
          ["seasonType"] in phases):
          game_id = game_info["node"]["gameDetailId"]
          game_path = f"{self.base_path}/nfl_json/json/games/{game_id}.json.gz"
          if not self._game_is_updated(game_id, game_path):
            print(f'Updating {game_id}')
            self._update_game(game_info, game_path)
  def command_line_update(self, update_teams, update_players):
    if update_teams:
      print("Updating teams collection in database...")
      self.update_teams_from_file(self.teams_path)
    if update_players:
      print("Updating players collection in database...")
      self.update_players_from_file(self.players_path_main)
    self.update_games_main()
  def test_db_setup(self):
    self.update_teams_from_file(self.teams_path)
    self.update_players_from_file(self.players_path_test)
    self.update_games_test()

def main():
  parser = argparse.ArgumentParser(
    description='Sync the JSON game data to the MongoDB database')
  parser.add_argument('--teams', action='store_true', 
    help='Sync the JSON team data to the database')
  parser.add_argument('--players', action='store_true', 
    help='Sync the JSON player data to the database')
  args = parser.parse_args()
  
  SyncDB().command_line_update(args.teams, args.players)

if __name__ == '__main__':
  main()    