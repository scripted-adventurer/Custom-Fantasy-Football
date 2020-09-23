# -*- coding: utf-8 -*-
from mongoengine import connect

import gzip
import json
import argparse
import os

import models
from config import SETTINGS, INCLUDED_SEASONS

class SyncDB:
  '''Updates the MongoDB instance pointed to in settings.py with all the stats
  and player info found in the nfl_json folder (using the data models defined in 
  models.py).'''
  def __init__(self):
    self.base_path = os.environ['CUSTOM_FF_PATH']
    self.teams_path = f"{self.base_path}/nfl_json/json/teams.json"
    self.players_path_main = f"{self.base_path}/nfl_json/json/currentPlayers.json"
    self.players_path_test = f"{self.base_path}/mongodb_backend/tests/players_fixture.json"
    connect(SETTINGS['MONGODB_SETTINGS']['db'], 
      host=SETTINGS['MONGODB_SETTINGS']['host'], 
      port=SETTINGS['MONGODB_SETTINGS']['port'], 
      username=SETTINGS['MONGODB_SETTINGS']['username'], 
      password=SETTINGS['MONGODB_SETTINGS']['password'])
  def update_teams_from_file(self, teams_path):
    with open(teams_path) as teams_file:
      teams = json.load(teams_file)
    for team_info in teams["teams"]:
      team = models.Team().custom_json(team_info)
      team.save()
  def update_players_from_file(self, players_path):
    with open(players_path) as players_file:
      players = json.load(players_file)
    for player_info in players.values():
      player = models.Player().custom_json(player_info)
      player.save()
  def _game_is_updated(self, game_path):
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
  def _update_game(self, game_path):
    with gzip.open(game_path) as game_json:
      game_detail = json.load(game_json)
    game = models.Game().custom_json(game_info, game_detail)
    game.save()
  def update_games_test(self):
    # send all the data in the games test fixture to the test database
    games_fixtures = os.listdir(f"{self.base_path}/mongodb_backend/tests/fixtures/games")
    for game in games_fixtures:
      self._update_game(game)
  def update_games_main(self):
    # check for updates for any games falling into the seasons specified in settings
    # and push updates as needed
    for year, phases in INCLUDED_SEASONS.items():
      print(f"Checking for updates in games collection in database for {year}...")
      with open(f"{self.base_path}/nfl_json/json/schedule/{year}.json") as schedule_file:
        schedule = json.load(schedule_file)
      games = schedule["data"]["viewer"]["league"]["games"]["edges"]
      for game in games:
        if (game["node"]["gameDetailId"] and game["node"]["week"]["seasonType"] in phases):
          game_id = game["node"]["gameDetailId"]
          game_path = f"{self.base_path}/nfl_json/json/games/{game_id}.json.gz"
          if not self._game_is_updated(game_path):
            print(f'Updating {game_id}')
            self._update_game(game_path)
  def command_line_update(self, update_players):
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
  parser = argparse.ArgumentParser(description='Sync the JSON game data to the MongoDB database')
  parser.add_argument('--players', action='store_true', 
    help='Sync the JSON player data to the database')
  args = parser.parse_args()
  
  SyncDB().command_line_update(args.players)

if __name__ == '__main__':
  main()    