import urllib.request
import urllib.parse
import argparse
import json
import os
import gzip
import datetime
import time

import settings

class NflApiRequest:
  '''Makes a request to the NFL.com API with the given input parameters and returns
  the response (either raw or as JSON).'''
  def __init__(self, query_filter, result_fields):
    self.filter = query_filter
    self.result_fields = ' '.join(result_fields)
    self.query = f"query{{viewer{{{self.filter}{self.result_fields}}}}}"
    self.variables = 'null'
    self.base_url = "https://api.nfl.com/v3/shield/?"
    self.params = urllib.parse.urlencode({'query': self.query, 'variables': 
      self.variables})
    self.full_url = self.base_url + self.params
    self.headers = {"Authorization": settings.nfl_api_key}
    self.request = urllib.request.Request(self.full_url, headers=self.headers)
    self.response = urllib.request.urlopen(self.request)
  def raw(self):
    return self.response.read()
  def json(self):
    return json.loads(self.response.read().decode(self.response.info().get_param(
      'charset') or 'utf-8'))

class Schedule:
  '''Update the NFL.com schedule JSON data.'''
  def __init__(self, current_nfl_year):
    self.current_nfl_year = current_nfl_year
  def _download_year(self, year):
    query_filter = f"league{{games(first:400,week_seasonValue:{year})"
    result_fields = ["{edges", "{node", "{id", "esbId", "gameDetailId", "week", 
      "{seasonValue", "seasonType", "weekValue}", "gameTime}}}}"]
    api_request = NflApiRequest(query_filter, result_fields)
    response = api_request.json() 
    with open(f"json/schedule/{year}.json", 'w') as output_file:
      output_file.write(json.dumps(response, indent=2))
  def previous(self):
    # check past years for missing data
    start_year = 2011
    for year in range(start_year, self.current_nfl_year):
      if not os.path.isfile(f"json/schedule/{year}.json"):
        print(f"Downloading schedule for {year}...")
        self._download_year(year)
  def current(self):
    print("Downloading current schedule...")
    self._download_year(self.current_nfl_year)
  def main(self):
    self.previous()
    self.current()  

class Players:
  '''Update the NFL.com player JSON data.'''
  def __init__(self):
    self.teams = {}
    self.players = {}
  def _download_teams(self):
    # get the current list of team IDs (team IDs change each year)
    query_filter = 'teams(first:100,seasonValue:0)'
    result_fields = ["{edges", "{cursor", "node", "{id", "abbreviation}}}"]
    api_request = NflApiRequest(query_filter, result_fields)
    response = api_request.json()
    for team_node in response["data"]["viewer"]["teams"]["edges"]:
      self.teams[team_node["node"]["abbreviation"]] = team_node["node"]["id"] 
  def _write_player(self, player):
    # write an entry from a team's roster to the players dict
    # transform slightly so all fields are top level
    player_id = player["node"]["person"]["id"]
    name = player["node"]["person"]["displayName"]
    team = player["node"]["currentTeam"]["abbreviation"]
    position = player["node"]["position"]
    status = player["node"]["status"]
    jersey_num = player["node"]["jerseyNumber"]
    self.players[player_id] = {'id': player_id, 'name': name, 'team': team, 
      'position': position, 'status': status, 'jerseyNumber': jersey_num}
  def _download_roster(self, team_id):
    query_filter = f'players(first:830,season_season:0,currentTeam_id:\"{team_id}\")'
    result_fields = ["{edges", "{node", "{person", "{id", "displayName}", 
      "currentTeam", "{abbreviation}", "position", "status", "jerseyNumber}}}"]
    api_request = NflApiRequest(query_filter, result_fields)
    response = api_request.json()  
    for player in response["data"]["viewer"]["players"]["edges"]:
      self._write_player(player)
  def main(self):
    print("Downloading players...")
    self._download_teams()
    for team_id in self.teams.values():
      self._download_roster(team_id)
    with open("json/currentPlayers.json", 'w') as output_file:
      output_file.write(json.dumps(self.players, indent=2))

class Games:
  '''Update the NFL.com game JSON data.'''
  def __init__(self, year):
    self.year = year
  def _download_game(self, game_id):
    print(f"Downloading game data for {game_id}")
    query_filter = f'gameDetail(id:"{game_id}")'
    result_fields = ["{id","gameTime","attendance","stadium","homePointsOvertime",
    "homePointsOvertimeTotal","homePointsTotal","homePointsQ1","homePointsQ2",
    "homePointsQ3","homePointsQ4","homeTeam{nickName","id",
    "abbreviation}","homeTimeoutsUsed","period","phase","visitorPointsOvertime",
    "visitorPointsOvertimeTotal","visitorPointsQ1","visitorPointsQ2",
    "visitorPointsQ3","visitorPointsQ4","visitorPointsTotal",
    "visitorTeam{nickName","id","abbreviation}","visitorTimeoutsUsed",
    "weather{location","longDescription","shortDescription}",
    "scoringSummaries{playId","playDescription","patPlayId","homeScore",
    "visitorScore}","drives{quarterStart","endTransition","endYardLine",
    "endedWithScore","firstDowns","gameClockEnd","gameClockStart",
    "howEndedDescription","howStartedDescription","inside20","orderSequence",
    "playCount","playIdEnded","playIdStarted","playSeqEnded","playSeqStarted",
    "possessionTeam{abbreviation","nickName}" ,"quarterEnd","realStartTime",
    "startTransition","startYardLine","timeOfPossession","yards",
    "yardsPenalized}","plays{clockTime","down","driveSequenceNumber",
    "endClockTime","endYardLine","firstDown","goalToGo","nextPlayIsGoalToGo",
    "nextPlayType","orderSequence","penaltyOnPlay","playClock","playDeleted",
    "playDescription","playDescriptionWithJerseyNumbers","playId",
    "playReviewStatus","isBigPlay","playType","playStats{statId","yards",
    "team{id","abbreviation}","gsisPlayer{person{id","displayName}",
    "position}}","possessionTeam{abbreviation","nickName}prePlayByPlay",
    "quarter","scoringPlay","scoringPlayType","scoringTeam{id","abbreviation",
    "nickName}shortDescription","specialTeamsPlay","stPlayType","timeOfDay",
    "yardLine","yards","yardsToGo","latestPlay}}"]
    api_request = NflApiRequest(query_filter, result_fields)
    with gzip.open(f"json/games/{game_id}.json.gz", 'wb') as output_file:
      output_file.write(api_request.raw())
  def is_update_needed(self, game):
    # return True if the gameDetailId exists (game has started) but the JSON file doesn't
    # or if the JSON file exists, but the game is not yet final
    if game["gameDetailId"] and not os.path.isfile(
      f'json/games/{game["gameDetailId"]}.json.gz'):
      return True
    game_path = f'json/games/{game["gameDetailId"]}.json.gz'
    with gzip.open(game_path) as game_json:
      game_detail = json.load(game_json)
    game_status = game_detail["data"]["viewer"]["gameDetail"]["phase"]
    if game_status != 'FINAL' and game_status != 'FINAL_OVERTIME':
      return True
    return False  
  def main(self):
    with open(f"json/schedule/{self.year}.json") as schedule_file:
      schedule = json.load(schedule_file)
    for game in schedule["data"]["viewer"]["league"]["games"]["edges"]:
      game = game["node"]
      if game['gameDetailId'] and self.is_update_needed(game):
        self._download_game(game['gameDetailId'])

class Download:
  '''Controls downloading activity for each of the NFL API classes above.'''
  def __init__(self):
    # a new NFL league year starts in March (after the Feb Super Bowl)
    self.now = datetime.datetime.now()
    self.current_nfl_year = (self.now.year if self.now.month > 2 else 
      self.now.year - 1)
    self.players_update = False
  def _check_players_update(self):
    # return True if its been at least 24 hours since the last players update
    yesterday = time.time() - (24 * 60 * 60)
    players_update_time = os.path.getmtime("json/currentPlayers.json")
    if players_update_time < yesterday:
      self.players_update = True
  def main(self, year=None, force_players_update=False):
    if force_players_update:
      self.players_update = True
    else:  
      self._check_players_update()
    if not year:
      Schedule(self.current_nfl_year).main()
      if self.players_update:
        Players().main()
      Games(self.current_nfl_year).main()
    else:
      Games(year).main()