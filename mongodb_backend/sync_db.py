from pymongo import MongoClient
import gzip
import json

import models
import settings

class SyncDB:
  '''Updates the MongoDB instance pointed to in settings.py with all the stats
  and player info found in the json folder (using the data models defined in models.py)'''
  def __init__(self):
    self.client = MongoClient(host=settings.database['host'], 
      port=settings.database['port'], username=settings.database['user'], 
      password=settings.database['password'], 
      authSource=settings.database['db'])
    self.db = self.client[settings.database['db']]
  def update_players(self):
    print("Updating players collection in database...")
    # send the data in the currentPlayers.json file directly to MongoDB
    with open('json/currentPlayers.json') as players_file:
      players = json.load(players_file)
    for player in players.values():
      self.db.player.find_one_and_replace({'id': player['id']}, player, 
        upsert=True)
  def _update_game(self, game_info):
    game_path = f'json/games/{game_info["node"]["gameDetailId"]}.json.gz'
    with gzip.open(game_path) as game_json:
      game_detail = json.load(game_json)
    game = models.Game(game_info, game_detail)
    existing = self.db.game.find_one({"_id": game._id})
    # add if missing
    if not existing:
      print(f"Adding {game._id} to database...")
      self.db.game.insert_one(game.as_dict())
    # update if out of date
    elif len(existing["plays"]) != len(game.plays): 
      print(f"Updating {game._id} in database...")
      self.db.game.replace_one({"_id": game._id}, game.as_dict())
  def update_games(self):
    # for each season defined in the settings file, send the associated game
    # data (after transforming according to models.py) to MongoDB
    for year, phases in settings.included_seasons.items():
      print(f"Checking for updates in games collection in database for {year}...")
      with open(f"json/schedule/{year}.json") as schedule_file:
        schedule = json.load(schedule_file)
      games = schedule["data"]["viewer"]["league"]["games"]["edges"]
      for game in games:
        if game["node"]["gameDetailId"] and game["node"]["week"]["seasonType"] in phases:
          self._update_game(game)
  def main(self, update_players):
    if update_players:
      self.update_players()
    self.update_games()