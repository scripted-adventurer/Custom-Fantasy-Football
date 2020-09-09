from django.core.management import BaseCommand
import data.models as db_models
import postgres_backend.settings as settings 

import json
import os
import datetime
import gzip

import importlib.util
spec = importlib.util.spec_from_file_location("statmap", 
  f"{os.environ['CUSTOM_FF_PATH']}/nfl_json/statmap.py")
statmap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(statmap)

class SyncDB:
  '''Contains all logic to transform the JSON data into the appropriate 
  relational form and write it to the database.'''
  def __init__(self):
    self.base_path = os.environ['CUSTOM_FF_PATH']
  def update_teams(self):
    # sync teams.json to the database
    with open(f"{self.base_path}/nfl_json/json/teams.json") as teams_file:
      teams = json.load(teams_file)
    for team in teams["teams"]:
      db_models.Team.objects.get_or_create(team_id=team["id"], name=team["name"], 
        active=team["active"])
  def update_players(self):
    # sync currentPlayers.json to the database
    with open(f"{self.base_path}/nfl_json/json/currentPlayers.json") as players_file:
      players = json.load(players_file)
    for player in players.values():
      try:
        jersey_number = int(player["jerseyNumber"])
      except TypeError:
        jersey_number = None  
      # skip players with missing data
      if player["id"] and player["name"] and player["team"] and player["position"]:
        team = db_models.Team.objects.get(team_id=player["team"])
        db_models.Player.objects.get_or_create(player_id=player["id"], 
          name=player["name"], defaults={'team': team, 
          'position': player["position"], 'status': player["status"], 
          'jersey_number': jersey_number})
  def _update_play_player(self, play, play_player):
    # skip rows without player info
    if (not play_player["gsisPlayer"] or not play_player["gsisPlayer"]["person"] 
      or not play_player["gsisPlayer"]["position"]):
      return 1
    player = db_models.Player.objects.get_or_create(
      player_id=play_player["gsisPlayer"]["person"]["id"], defaults={
      'name': play_player["gsisPlayer"]["person"]["displayName"], 
      'position': play_player["gsisPlayer"]["position"]})[0] 
    play_player_row = db_models.PlayPlayer.objects.get_or_create(play=play, 
      player=player, team=play.pos_team)[0]
    # skip unknown stat values
    if play_player["statId"] not in statmap.idmap:
      return 1
    # update the stat categories and yardage
    stat_info = statmap.idmap[play_player["statId"]]
    if stat_info['yds']:
      setattr(play_player_row, stat_info['yds'], play_player["yards"])
    for field in stat_info['fields']:
      # half tackles and sacks use a value field, all others are 1
      setattr(play_player_row, field, stat_info.get('value', 1))
    play_player_row.save()  
  def _update_play(self, game, play):
    # skip plays without an associated drive or team
    if not play["driveSequenceNumber"] or not play["possessionTeam"]:
      return 1
    drive = db_models.Drive.objects.get(game=game, drive_id=play["driveSequenceNumber"])  
    pos_team = db_models.Team.objects.get(team_id=play["possessionTeam"]
      ["abbreviation"])
    play_row = db_models.Play.objects.get_or_create(drive=drive, 
      play_id=play["orderSequence"], defaults={'time': play["clockTime"], 
      'down': play["down"], 'start_yardline': play["yardLine"], 
      'end_yardline': play["endYardLine"], 'first_down': play["firstDown"], 
      'penalty': play["penaltyOnPlay"], 
      'description': play["playDescriptionWithJerseyNumbers"], 
      'play_type': play["playType"], 
      'pos_team': pos_team, 'quarter': play["quarter"], 
      'yards_to_go': play["yardsToGo"]})[0]
    for play_player in play["playStats"]:
      self._update_play_player(play_row, play_player)
  def _update_drive(self, game, drive):
    pos_team = db_models.Team.objects.get(team_id=drive["possessionTeam"]
      ["abbreviation"])
    drive_row = db_models.Drive.objects.get_or_create(game=game, 
      drive_id=drive["orderSequence"], defaults={
      'start_quarter': drive["quarterStart"], 'end_quarter': drive["quarterEnd"],
      'start_transition': drive["startTransition"], 
      'end_transition': drive["endTransition"], 
      'start_field': drive["startYardLine"], 'end_field': drive["endYardLine"], 
      'start_time': drive["gameClockStart"], 'end_time': drive["gameClockEnd"], 
      'pos_team': pos_team, 'first_downs': drive["firstDowns"], 
      'penalty_yards': drive["yardsPenalized"], 'yards_gained': drive["yards"], 
      'play_count': drive["playCount"]})
  def _game_is_updated(self, game_id):
    # check if the database has been updated since the last time the JSON file was
    json_game_path = f'{self.base_path}/nfl_json/json/games/{game_id}.json.gz'
    json_update_time = datetime.datetime.utcfromtimestamp(
      os.path.getmtime(json_game_path))
    db_row = db_models.Game.objects.filter(game_id=game_id)
    if not len(db_row):
      return False
    db_update_time = db_row[0].modified_at
    if db_update_time > json_update_time:
      return True 
    else:
      return False   
  def _update_game(self, game_info):
    print(f'Updating {game_info["gameDetailId"]}')
    game_path = f'{self.base_path}/nfl_json/json/games/{game_info["gameDetailId"]}.json.gz'
    with gzip.open(game_path) as game_json:
      game_detail = json.load(game_json)
    game_detail = game_detail["data"]["viewer"]["gameDetail"]
    attendance = (int(game_detail["attendance"].replace(',','')) if 
      game_detail["attendance"] else None)
    stadium = game_detail["stadium"] if game_detail["stadium"] else None
    weather = (game_detail["weather"].get("shortDescription", None) if 
      game_detail["weather"] else None)
    home_team = db_models.Team.objects.get(team_id=game_detail["homeTeam"]
      ["abbreviation"])
    away_team = db_models.Team.objects.get(team_id=game_detail["visitorTeam"]
        ["abbreviation"])
    game = db_models.Game.objects.get_or_create(game_id=game_info["gameDetailId"], 
      defaults={'season_type': game_info["week"]["seasonType"], 
      'season_year': game_info["week"]["seasonValue"], 
      'week': game_info["week"]["weekValue"], 'start_time': game_detail["gameTime"], 
      'phase': game_detail["phase"], 
      'attendance': attendance, 'stadium': stadium, 
      'home_score': game_detail["homePointsTotal"], 
      'home_score_q1': game_detail["homePointsQ1"], 
      'home_score_q2': game_detail["homePointsQ2"], 
      'home_score_q3': game_detail["homePointsQ3"], 
      'home_score_q4': game_detail["homePointsQ4"], 
      'home_score_ot': game_detail["homePointsOvertimeTotal"],
      'away_score': game_detail["visitorPointsTotal"],
      'away_score_q1': game_detail["visitorPointsQ1"], 
      'away_score_q2': game_detail["visitorPointsQ2"], 
      'away_score_q3': game_detail["visitorPointsQ3"], 
      'away_score_q4': game_detail["visitorPointsQ4"], 
      'away_score_ot': game_detail["visitorPointsOvertimeTotal"], 
      'home_team': home_team, 'away_team': away_team, 'weather': weather})[0]
    for drive in game_detail["drives"]:
      self._update_drive(game, drive)
    for play in game_detail["plays"]:
      self._update_play(game, play)
  def update_games(self, season_year, season_type):
    # find each associated game for this season year and type and sync to the db
    schedule_path = f"{self.base_path}/nfl_json/json/schedule/{season_year}.json"
    with open(schedule_path) as schedule_file:
      schedule = json.load(schedule_file)
    games = schedule["data"]["viewer"]["league"]["games"]["edges"]
    for game in games:
      game = game["node"]
      if (game["gameDetailId"] and game["week"]["seasonType"] == season_type):
        self._update_game(game)           


class Command(BaseCommand):

  help = "Syncs the database with NFL.com JSON stats data"

  def add_arguments(self, parser):
    # Named (optional) arguments
    parser.add_argument(
      '--initial',
      action='store_true',
      help='Sets up the db for the first time (syncs all data)',
    )
    parser.add_argument(
      '--teams',
      action='store_true',
      help='Force an update on the teams table',
    )
    parser.add_argument(
      '--players',
      action='store_true',
      help='Force an update on the players table',
    )

  def handle(self, *args, **options):
    sync = SyncDB()
    if options['initial'] or options['teams']:
      print("Updating teams...")
      sync.update_teams()
    if options['initial'] or options['players']:
      print("Updating players...")
      sync.update_players()

    if options['initial']:
      # update all the seasons specified in settings
      for season_year, season_types in settings.INCLUDED_SEASONS.items():
        print(f"Updating games for {season_year}")
        for season_type in season_types:
          sync.update_games(season_year, season_type)
    else:
      # update the current year's data (new league year starts in March after Super Bowl)
      now = datetime.datetime.now()
      season_year = (now.year if now.month > 2 else now.year - 1)
      print(f"Updating games for {season_year}")
      for season_type in settings.INCLUDED_SEASONS.get(season_year, []):
        sync.update_games(season_year, season_type)