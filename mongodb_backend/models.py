from pymongo import MongoClient
import os
import datetime
import pytz

import settings 

import importlib.util
spec = importlib.util.spec_from_file_location("statmap", 
  f"{os.environ['CUSTOM_FF_PATH']}/nfl_json/statmap.py")
statmap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(statmap)
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
CurrentWeek = common.CurrentWeek
Utility = common.Utility

def convert_yard_line(yard_line, possession_team):
  # extract team ID and yardline ex. "GB 25" -> ['GB', 25]
  try:
    yard_line = yard_line.split(' ')
    team = yard_line[0]
    yard_value = int(yard_line[1])
  except:
    return "N/A"  
  # team's own yard line is negative, opponent's is positive
  # ex. GB on the GB 25 = -25, GB on the CHI 25 = 25
  if team == possession_team:
    return -1 * yard_value
  else:
    return yard_value

def get_current_week():
  now = datetime.datetime.now(pytz.UTC)
  return (CurrentWeek().find(now))    

class DB:
  '''Represents a connection to the MongoDB instance.'''
  def __init__(self, database='default'):
    self.client = MongoClient(host=settings.DATABASES[database]['host'], 
      port=settings.DATABASES[database]['port'], 
      username=settings.DATABASES[database]['user'], 
      password=settings.DATABASES[database]['password'], 
      authSource=settings.DATABASES[database]['db'])
    self.db = self.client[settings.DATABASES[database]['db']]

class Game:
  '''Represents a single NFL game in a season and provides a logical mapping 
  between fields found in the NFL API and fields used in the 'game' collection of
  the MongoDB database.'''
  def __init__(self):
    self._id = None
    self.week = {"season_type": None, "season_year": None, "week": None}
    self.start_time = None
    self.phase = None
    self.attendance = None
    self.stadium = None
    self.home_score = {
      "total": None, "Q1": None, "Q2": None, "Q3": None, "Q4": None, 
      "overtime": None
    }
    self.away_score = {
      "total": None, "Q1": None, "Q2": None, "Q3": None, "Q4": None, 
      "overtime": None
    }
    self.home_team = {
      "name": None,
      "id": None
    }
    self.away_team = {
      "name": None,
      "id": None
    }
    self.weather = None 
    self.drives = []
    self.plays = []
  def __repr__(self):
    return f"{{'model': 'Game', 'game_id': '{self._id}'}}"
  def __str__(self):
    return f"{{Game '{self._id}'}}"
  def __eq__(self, other):
    if isinstance(other, Game):
      return (self.__dict__ == other.__dict__)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Game', self.game_id))
  def _get_drives(self, drives):
    return [Drive(self._id, drive).as_dict() for drive in drives]
  def _get_plays(self, plays):
    return [Play(self._id, play).as_dict() for play in plays]
  def from_json(self, game_info, game_detail):
    game_info = game_info["node"]
    game_detail = game_detail["data"]["viewer"]["gameDetail"]
    self._id = game_detail["id"]
    self.week["season_type"] = game_info["week"]["seasonType"]
    self.week["season_year"] = game_info["week"]["seasonValue"]
    self.week["week"] = game_info["week"]["weekValue"]
    self.start_time = game_detail["gameTime"]
    self.phase = game_detail["phase"]
    self.attendance = game_detail["attendance"]
    self.stadium = game_detail["stadium"]
    self.home_score["total"] = game_detail["homePointsTotal"]
    self.home_score["Q1"] = game_detail["homePointsQ1"]
    self.home_score["Q2"] = game_detail["homePointsQ2"]
    self.home_score["Q3"] = game_detail["homePointsQ3"]
    self.home_score["Q4"] = game_detail["homePointsQ4"]
    self.home_score["overtime"] = game_detail["homePointsOvertimeTotal"]
    self.away_score["total"] = game_detail["visitorPointsTotal"]
    self.away_score["Q1"] = game_detail["visitorPointsQ1"]
    self.away_score["Q2"] = game_detail["visitorPointsQ2"]
    self.away_score["Q3"] = game_detail["visitorPointsQ3"]
    self.away_score["Q4"] = game_detail["visitorPointsQ4"]
    self.away_score["overtime"] = game_detail["visitorPointsOvertimeTotal"]
    self.home_team["name"] = game_detail["homeTeam"]["nickName"]
    self.home_team["id"] = game_detail["homeTeam"]["abbreviation"]
    self.away_team["name"] = game_detail["visitorTeam"]["nickName"]
    self.away_team["id"] = game_detail["visitorTeam"]["abbreviation"]
    if game_detail["weather"]:
      self.weather = game_detail["weather"]["shortDescription"]
    else:  
      self.weather = "N/A"  
    self.drives = self._get_drives(game_detail["drives"])
    self.plays = self._get_plays(game_detail["plays"])
    return self
  def write_to_db(self):
    # add the game only if it's valid and it's missing or not up to date in the db
    # return True if changes were made
    if not self._id:
      return False 
    existing = Game().get(self._id)
    db = DB().db
    if not existing:
      db.game.insert_one(self.as_dict())
      return True
    elif self.as_dict() != existing.as_dict():
      db.game.replace_one({"_id": self._id}, self.as_dict())
      return True 
    return False  
  def get(self, game_id):
    db = DB().db
    new = db.game.find_one({"_id": game_id})
    if new:
      self._id = new["_id"]
      self.week = new["week"]
      self.start_time = new["start_time"]
      self.phase = new["phase"]
      self.attendance = new["attendance"]
      self.stadium = new["stadium"]
      self.home_score = new["home_score"]
      self.away_score = new["away_score"]
      self.home_team = new["home_team"]
      self.away_team = new["away_team"]
      self.weather = new["weather"]
      self.drives = new["drives"]
      self.plays = new["plays"]
      return self
    else:
      return None   
  def data_dict(self):
    return {'id': self._id, 'start_time': 
      self.start_time.strftime("%Y-%m-%d %H:%M"), 
      'season_type': self.week['season_type'], 
      'season_year': self.week['season_year'], 'week': self.week['week'], 
      'home_team': self.home_team['id'], 'away_team': self.away_team['id'],
      'home_score': self.home_score['total'], 
      'away_score': self.away_score['total']}
  def as_dict(self):
    return self.__dict__ 

class Drive:
  '''Represents a single drive in a given NFL game and provides a logical mapping
  between the fields found in the NFL API and the 'drives' field of the 'game'
  collection found in the MongoDB database. Note that drives are not written to
  or retrieved from the database on their own (only as part of a game).'''
  def __init__(self, game_id, drive):
    self.game_id = game_id
    self.drive_id = drive["orderSequence"]
    self.start_quarter = drive["quarterStart"]
    self.start_transition = drive["startTransition"]
    self.start_time = drive["gameClockStart"]
    self.end_quarter = drive["quarterEnd"]
    self.end_transition = drive["endTransition"]
    self.end_time = drive["gameClockEnd"]
    self.possession_team = {
      "name": drive["possessionTeam"]["nickName"] if drive["possessionTeam"] else "",
      "id": drive["possessionTeam"]["abbreviation"] if drive["possessionTeam"] else ""
    }
    self.possession_time = drive["timeOfPossession"]
    self.first_downs = drive["firstDowns"]
    self.penalty_yards = drive["yardsPenalized"]
    self.yards_gained = drive["yards"]
    self.play_count = drive["playCount"]
    self.start_yardline = self._convert_yard_line(drive["startYardLine"], 
      self.possession_team['id'])
    self.end_yardline = self._convert_yard_line(drive["endYardLine"], 
      self.possession_team['id'])
  def __repr__(self):
    return (f"{{'model': 'Drive', 'game_id': '{self.game_id}', "
    f"'drive_id': {self.drive_id}}}")
  def __str__(self):
    return f"{{Drive {self.drive_id} from Game '{self.game_id}'}}"
  def __eq__(self, other):
    if isinstance(other, Drive):
      return (self.__dict__ == other.__dict__)
    else:
      return NotImplemented 
  def __hash__(self):
    values = []
    for value in self.__dict__.values():
      if isinstance(value, dict):
        for sub_value in value.values():
          values.append(sub_value)
      else:
        values.append(value)  
    return hash(tuple(values))
  def _convert_yard_line(self, yard_line, possession_team):
    return convert_yard_line(yard_line, possession_team) 
  def as_dict(self):
    return self.__dict__    

class Play:
  '''Represents a single play in a given NFL game and provides a logical mapping
  between the fields found in the NFL API and the 'plays' field of the 'game' 
  collection found in the MongoDB database. Note that plays are not written to 
  or retrieved from the database on their own (only as part of a game).'''
  def __init__(self, game_id, play):
    self.game_id = game_id
    self.drive_id = play["driveSequenceNumber"]
    self.play_id = play["orderSequence"]
    self.quarter = play["quarter"]
    self.possession_team = {
      "name": play["possessionTeam"]["nickName"] if play["possessionTeam"] else "",
      "id": play["possessionTeam"]["abbreviation"] if play["possessionTeam"] else ""
    }
    self.start_time = play["clockTime"]
    self.end_time = play["endClockTime"]
    self.down = play["down"]
    self.yards_to_go = play["yardsToGo"]
    self.yards_gained = play["yards"]
    self.description = play["playDescription"]
    self.first_down = play["firstDown"]
    self.penalty = play["penaltyOnPlay"]
    self.play_type = play["playType"]
    self.scoring_play_type = play["scoringPlayType"]
    self.play_clock = play["playClock"]
    self.time_of_day = play["timeOfDay"]
    self.start_yardline = self._convert_yard_line(play["yardLine"], 
      self.possession_team['id'])
    self.end_yardline = self._convert_yard_line(play["endYardLine"], 
      self.possession_team['id'])
    # contains a mapping of stat names to summed stat values for all stats in the play
    self.aggregate = {}
    # contains a list of objects with player IDs and stat names/values
    self.player_stats = []
    self._parse_play_stats(play["playStats"])
  def __repr__(self):
    return (f"{{'model': 'Play', 'game_id': '{self.game_id}', "
    f"'drive_id': {self.drive_id}, 'play_id': {self.play_id}}}")
  def __str__(self):
    return (f"{{Play {self.play_id} from Drive {self.drive_id} from Game "
    f"'{self.game_id}'}}")
  def __eq__(self, other):
    if isinstance(other, Play):
      return (self.__dict__ == other.__dict__)
    else:
      return NotImplemented 
  def __hash__(self):
    return hash((self.drive_id, self.quarter, self.possession_team["name"],
      self.possession_team["id"], self.start_yardline, self.start_time, 
      self.end_yardline, self.end_time, self.down, self.yards_to_go, 
      self.yards_gained, self.description, self.first_down, self.penalty, 
      self.play_type, self.scoring_play_type, self.play_clock, self.time_of_day))
  def _convert_yard_line(self, yard_line, possession_team):
    return convert_yard_line(yard_line, possession_team)
  def _parse_play_stats(self, play_stats):
    # turn the list of play stats with numeric IDs into player level and 
    # aggregate play level human readable stats  
    temp_player_stats = {}
    for raw_stat in play_stats:
      # convert the stat ID and yards to a dict of "stat_name": "stat_value"
      parsed_stats = statmap.values(raw_stat["statId"], raw_stat["yards"])
      for stat_name, stat_value in parsed_stats.items():
        # track combined stats for each player involved in the play
        try:
          player_id = raw_stat["gsisPlayer"]["person"]["id"]
          if player_id not in temp_player_stats:
            temp_player_stats[player_id] = {'id': player_id}
          temp_player_stats[player_id][stat_name] = stat_value
        except TypeError:
          pass
        # track aggregated stats for the entire play  
        if stat_name not in self.aggregate:
          self.aggregate[stat_name] = stat_value 
        else:
          self.aggregate[stat_name] += stat_value

    for entry in temp_player_stats.values():
      self.player_stats.append(entry)
  def as_dict(self):
    return self.__dict__

class Player:
  '''Represents a single NFL player and provides a logical mapping between 
  fields found in the NFL API and fields used in the 'player' collection of
  the MongoDB database.'''
  def __init__(self):
    self._id = None 
    self.name = None 
    self.team = None 
    self.position = None 
    self.status = None 
    self.jersey_number = None 
  def __repr__(self):
    return f"{{'model': 'Player', 'player_id': '{self.player_id}'}}"
  def __str__(self):
    return f"{{{self.name} {self.position} {self.team.team_id}}}"
  def __eq__(self, other):
    if isinstance(other, Player):
      return (self.player_id == other.player_id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Player', self.player_id))
  def from_json(self, player_info):
    self._id = player_info["id"]
    self.name = player_info["name"]
    self.team = player_info["team"]
    self.position = player_info["position"]
    self.status = player_info["status"]
    self.jersey_number = player_info["jerseyNumber"]
    return self
  def write_to_db(self):
    # add the player only if valid, replacing the old entry if it exists
    if self._id:
      db = DB().db
      db.player.find_one_and_replace({"_id": self._id}, self.as_dict(), upsert=True)
      return True 
    return False  
  def get(self, player_id):
    db = DB().db
    new = db.player.find_one({"_id": player_id})
    if new:
      self._id = new["_id"]
      self.name = new["name"]
      self.team = new["team"]
      self.position = new["position"]
      self.status = new["status"]
      self.jersey_number = new["jersey_number"]
      return self
    else:
      return None   
  def as_dict(self):
    return self.__dict__
  def is_locked(self):
    season_year, season_type, week = get_current_week()
    this_game = (Game.objects.filter(home_team=self.team, 
      season_type=season_type, season_year=season_year, week=week) | 
      (Game.objects.filter(away_team=self.team, season_type=season_type, 
      season_year=season_year, week=week)))
    game_start = this_game[0].start_time.replace(tzinfo=pytz.UTC)
    now = datetime.datetime.now(pytz.UTC)
    if len(this_game) == 1 and game_start < now:
      return True
    else:
      return False    

class League:
  '''Represents a user-created league, containing members (users in the league), 
  lineup settings, and scoring settings.'''
  def __init__(self):
    self.name = None
    self.password = None
    self.lineup_settings = {'DB': 0, 'DL': 0, 'K': 0, 'LB': 0, 'OL': 0, 'P': 0, 
      'QB': 0, 'RB': 0, 'TE': 0, 'WR': 0}
    self.scoring_settings = []
  def __repr__(self):
    return f"{{'model': 'League', 'name': '{self.name}'}}"
  def __str__(self):
    return f"{{League {self.name}}}"
  def __eq__(self, other):
    if isinstance(other, League):
      return (self.name == other.name)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('League', self.name))
  def get(self, league_name):
    db = DB().db
    new = db.league.find_one({"name": league_name})
    if new:
      self._id = new["_id"]
      self.name = new["name"]
      self.password = new["password"]
      self.lineup_settings = new["lineup_settings"]
      self.scoring_settings = new["scoring_settings"]
      return self
    else:
      return None 
  def create(self, name, password, lineup_settings, scoring_settings):
    self.name = name 
    self.password = Utility().custom_hash(password)
    self.lineup_settings = lineup_settings
    self.scoring_settings = scoring_settings
    db = DB().db
    db.league.insert_one(self.as_dict())
    return self
  def write_to_db(self):
    # add the league only if valid, replacing the old entry if it exists
    if self.name:
      db = DB().db
      db.league.find_one_and_replace({"name": self.name}, self.as_dict(), upsert=True)
      return True 
    return False     
  def correct_password(self, password):
    if not password:
      return False
    if (Utility().custom_hash(password) == self.password):
      return True
    else:
      return False
  def get_lineup_settings(self):
    return self.lineup_settings
  def set_lineup_settings(self, lineup_settings):
    self.lineup_settings = lineup_settings
    self.write_to_db()
  def get_scoring_settings(self):
    return self.scoring_settings     
  def set_scoring_settings(self, scoring_settings):
    self.scoring_settings = scoring_settings
    self.write_to_db()
  def set_password(self, password):
    self.password = Utility().custom_hash(password)
    self.write_to_db()
  def get_members(self):
    return sorted([member.username for member in models.Member().filter(
      league=self.name)])
  def as_dict(self):
    return self.__dict__

class Member:
  '''Represents one user's participation in a league.'''
  def __init__(self):
    self.username = None 
    self.league_name = None 
    self.admin = False
    # list of player objects keyed by {season_year}{season_type}{week} strings 
    self.lineups = {}
  def __repr__(self):
    return (f"{{'model': 'Member', 'username': '{self.username}', 'league': "
    f"'{self.league_name}'}}")
  def __str__(self):
    return f"{{User '{self.username}' in League '{self.league_name}'}}"
  def __eq__(self, other):
    if isinstance(other, Member):
      return (self.username == other.username and self.league_name == 
        other.league_name)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Member', self.username, self.league_name))
  def get(self, username, league_name):
    db = DB().db
    new = db.member.find_one({"username": username, "league_name": league_name})
    if new:
      self.username = new["username"]
      self.league_name = new["league_name"]
      self.admin = new["admin"]
      self.lineups = new["lineups"]
      return self
    else:
      return None 
  def create(self, username, league_name, admin=False):
    self.username = username
    self.league_name = league_name
    self.admin = admin
    db = DB().db
    db.member.insert_one(self.as_dict())
    return self
  def write_to_db(self):
    # add the member only if valid, replacing the old entry if it exists
    if self.username and self.league_name:
      db = DB().db
      db.member.find_one_and_replace({"username": username, "league_name": 
        league_name}, self.as_dict(), upsert=True)
      return True 
    return False
  def is_admin(self):
    return self.admin
  def get_lineup(self, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    week_key = f"{season_year}{season_type}{week}"
    return [player for player in self.lineups.get(week_key, [])]
  def lineup_delete(self, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    week_key = f"{season_year}{season_type}{week}"
    self.lineups.pop(week_key, None)
    self.write_to_db()
  def lineup_add(self, lineup, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    week_key = f"{season_year}{season_type}{week}"
    self.lineups[week_key] = lineup
    self.write_to_db()
  def as_dict(self):
    return self.__dict__  