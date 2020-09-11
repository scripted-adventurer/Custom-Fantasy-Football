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
    connect(SETTINGS['MONGODB_SETTINGS']['db'], 
      host=SETTINGS['MONGODB_SETTINGS']['host'], 
      port=SETTINGS['MONGODB_SETTINGS']['port'], 
      username=SETTINGS['MONGODB_SETTINGS']['username'], 
      password=SETTINGS['MONGODB_SETTINGS']['password'])
  def update_players(self):
    print("Updating players collection in database...")
    with open(f"{self.base_path}/nfl_json/json/currentPlayers.json") as players_file:
      players = json.load(players_file)
    for player_info in players.values():
      player = models.Player().custom_json(player_info)
      player.save()
  def _update_game(self, game_info):
    game_path = f"{self.base_path}/nfl_json/json/games/{game_info['node']['gameDetailId']}.json.gz"
    with gzip.open(game_path) as game_json:
      game_detail = json.load(game_json)
    game = models.Game().custom_json(game_info, game_detail)
    print(f"Updating game {game_info['node']['gameDetailId']}...")
    game.save()
  def update_games(self):
    # for each season defined in the settings file, send the associated game
    # data (after transforming according to models.py) to MongoDB
    for year, phases in INCLUDED_SEASONS.items():
      print(f"Checking for updates in games collection in database for {year}...")
      with open(f"{self.base_path}/nfl_json/json/schedule/{year}.json") as schedule_file:
        schedule = json.load(schedule_file)
      games = schedule["data"]["viewer"]["league"]["games"]["edges"]
      for game in games:
        if game["node"]["gameDetailId"] and game["node"]["week"]["seasonType"] in phases:
          self._update_game(game)
  def main(self, update_players):
    if update_players:
      self.update_players()
    self.update_games()

def main():
  parser = argparse.ArgumentParser(description='Sync the JSON game data to the MongoDB database')
  parser.add_argument('--players', action='store_true', 
    help='Sync the JSON player data to the database')
  args = parser.parse_args()
  
  SyncDB().main(args.players)

if __name__ == '__main__':
  main()    