# -*- coding: utf-8 -*-
from mongoengine import *

import os
import datetime
import pytz

from .security import User, generate_hash, compare_hash

import importlib.util
# spec = importlib.util.spec_from_file_location("statmap", 
#   f"{os.environ['CUSTOM_FF_PATH']}/nfl_json/statmap.py")
# statmap = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(statmap)
from custom_FF.common import statmap 

spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
CurrentWeek = common.CurrentWeek

def get_safe(model_name, **kwargs):
  # a modified get() function that returns a single matching object if one exists
  # or None otherwise (doesn't raise an Exception)
  models = {'Game': Game, 'Player': Player, 'League': League, 'Member': Member}
  model = models[model_name]
  data = model.objects(**kwargs)
  if len(data) == 1:
    return data[0]
  else:
    return None

def convert_yard_line(yard_line, possession_team):
  # extract team ID and yardline ex. "GB 25" -> ['GB', 25]
  try:
    possession_team = possession_team.team_id
    yard_line = yard_line.split(' ')
    team = yard_line[0]
    yard_value = int(yard_line[1])
  except:
    return None 
  # team's own yard line is negative, opponent's is positive
  # ex. GB on the GB 25 = -25, GB on the CHI 25 = 25
  if team == possession_team:
    return -1 * yard_value
  else:
    return yard_value

def get_current_week():
  now = datetime.datetime.now(pytz.UTC)
  return (CurrentWeek().find(now))  

class Team(EmbeddedDocument):
  '''Represents an NFL team. Used for the possession team fields in Game, Drive, and Play.'''
  team_id = StringField(max_length=3, required=True)
  name = StringField(max_length=40, required=True)

  def __repr__(self):
    return f"{{'model': 'Team', 'team_id': '{self.team_id}'}}"
  def __str__(self):
    return f"{{{self.name}}}"
  def __eq__(self, other):
    if isinstance(other, Team):
      return (self.team_id == other.team_id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Team', self.team_id))

SEASON_TYPES = ('PRE', 'REG', 'PRO', 'POST')

class Week(EmbeddedDocument):
  '''Represents a single week in an NFL season. Used in the week fields in Game 
  and Lineup.'''
  season_type = StringField(max_length=4, choices=SEASON_TYPES)
  season_year = IntField(required=True)
  week = IntField(required=True)

  def __repr__(self):
    return (f"{{'model': 'Week', 'season_type': '{self.season_type}', "
      f"'season_year': {self.season_year}, 'week': {self.week}}}")
  def __str__(self):
    return f"{{Week #{self.week} in {self.season_year} {self.season_type}}}"
  def __eq__(self, other):
    if isinstance(other, Week):
      return (self.season_type == other.season_type and self.season_year == 
        other.season_year and self.week == other.week)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Week', self.season_type, self.season_year, self.week))
  def as_key(self):
    # represents the three fields in one formatted string
    return f"{self.season_year}{self.season_type}{self.week}"

class GameScore(EmbeddedDocument):
  '''A simple class for representing scores in an NFL game. Used only in Game.'''
  total = IntField(default=0, required=True)
  Q1 = IntField(default=0, required=True)
  Q2 = IntField(default=0, required=True)
  Q3 = IntField(default=0, required=True)
  Q4 = IntField(default=0, required=True)
  overtime = IntField(default=0, required=True)

  def __repr__(self):
    return (f"{{'model': 'GameScore', 'total': {self.total}, 'Q1': {self.Q1}, "
      f"'Q2': {self.Q2}, 'Q3': {self.Q3}, 'Q4': {self.Q4}, 'overtime': "
      f"{self.overtime}}}")
  def __str__(self):
    return f"{{Score with total {self.total}}}"
  def __eq__(self, other):
    if isinstance(other, GameScore):
      return (self.total == other.total and self.Q1 == other.Q1 and 
        self.Q2 == other.Q2 and self.Q3 == other.Q3 and self.Q4 == other.Q4 and 
        self.overtime == other.overtime)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('GameScore', self.total, self.Q1, self.Q2, self.Q3, self.Q4, 
      self.overtime))

class Drive(EmbeddedDocument):
  '''Represents a single drive in a given NFL game and provides a logical mapping
  between the fields found in the NFL API and the 'drives' field of the 'game'
  collection found in the MongoDB database. Note that drives are not written to
  or retrieved from the database on their own (only as part of a game).'''
  drive_id = IntField()
  start_quarter = IntField()
  start_transition = StringField(max_length=20)
  start_time = StringField(max_length=10)
  end_quarter = IntField()
  end_transition = StringField(max_length=20)
  end_time = StringField(max_length=10)
  possession_team = EmbeddedDocumentField(Team)
  possession_time = StringField(max_length=10)
  first_downs = IntField()
  penalty_yards = IntField()
  yards_gained = IntField()
  play_count = IntField()
  start_yardline = IntField()
  end_yardline = IntField()

  def __repr__(self):
    return (f"{{'model': 'Drive', 'game_id': '{self._instance.game_id}', "
      f"'drive_id': {self.drive_id}}}")
  def __str__(self):
    return f"{{Drive {self.drive_id} from Game '{self._instance.game_id}'}}"
  def __eq__(self, other):
    if isinstance(other, Drive):
      return (self._instance.game_id == other._instance.game_id and 
        self.drive_id == other.drive_id)
    else:
      return NotImplemented  
  def __hash__(self):  
    return hash((self._instance.game_id, self.drive_id))
  def custom_json(self, game, drive):
    self.game_id = game
    self.drive_id = drive["orderSequence"]
    self.start_quarter = drive["quarterStart"]
    self.start_transition = drive["startTransition"]
    self.start_time = drive["gameClockStart"]
    self.end_quarter = drive["quarterEnd"]
    self.end_transition = drive["endTransition"]
    self.end_time = drive["gameClockEnd"]
    self.possession_team = (Team(team_id=drive["possessionTeam"]["abbreviation"], 
      name=drive["possessionTeam"]["nickName"]) if drive["possessionTeam"] else None)
    self.possession_time = drive["timeOfPossession"]
    self.first_downs = drive["firstDowns"]
    self.penalty_yards = drive["yardsPenalized"]
    self.yards_gained = drive["yards"]
    self.play_count = drive["playCount"]
    self.start_yardline = convert_yard_line(drive["startYardLine"], 
      self.possession_team)
    self.end_yardline = convert_yard_line(drive["endYardLine"], 
      self.possession_team)
    return self

class Play(EmbeddedDocument):
  '''Represents a single play in a given NFL game and provides a logical mapping
  between the fields found in the NFL API and the 'plays' field of the 'game' 
  collection found in the MongoDB database. Note that plays are not written to 
  or retrieved from the database on their own (only as part of a game).'''
  drive_id = IntField()
  play_id = IntField()
  quarter = IntField()
  possession_team = EmbeddedDocumentField(Team)
  start_time = StringField(max_length=10)
  end_time = StringField(max_length=10)
  down = IntField()
  yards_to_go = IntField()
  yards_gained = IntField()
  description = StringField(max_length=1000)
  first_down = BooleanField()
  penalty = BooleanField()
  play_type = StringField(max_length=20)
  scoring_play_type = StringField(max_length=20)
  play_clock = IntField()
  time_of_day = StringField(max_length=10)
  start_yardline = IntField()
  end_yardline = IntField()
  aggregate = DictField()
  player_stats = ListField(DictField())

  def __repr__(self):
    return (f"{{'model': 'Play', 'game_id': '{self._instance.game_id}', "
      f"'drive_id': {self.drive_id}, 'play_id': {self.play_id}}}")
  def __str__(self):
    return (f"{{Play {self.play_id} from Drive {self.drive_id} from Game "
      f"'{self._instance.game_id}'}}")
  def __eq__(self, other):
    if isinstance(other, Play):
      return (self._instance.game_id == other._instance.game_id and 
        self.drive_id == other.drive_id and self.play_id == other.play_id)
    else:
      return NotImplemented 
  def __hash__(self):
    return hash((self._instance.game_id, self.drive_id, self.play_id))
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
        self.aggregate[stat_name] = self.aggregate.get(stat_name, 0) + stat_value
    for entry in temp_player_stats.values():
      self.player_stats.append(entry)
  def custom_json(self, game, play):
    self.game_id = game
    self.drive_id = play["driveSequenceNumber"]
    self.play_id = play["orderSequence"]
    self.quarter = play["quarter"]
    self.possession_team = (Team(team_id=play["possessionTeam"]["abbreviation"], 
      name=play["possessionTeam"]["nickName"]) if play["possessionTeam"] else None)
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
    self.play_clock = int(play["playClock"]) if play["playClock"] else None 
    self.time_of_day = play["timeOfDay"]
    self.start_yardline = convert_yard_line(play["yardLine"], 
      self.possession_team)
    self.end_yardline = convert_yard_line(play["endYardLine"], 
      self.possession_team)
    self._parse_play_stats(play["playStats"])
    return self  

class Game(Document):
  '''Represents a single NFL game in a season and provides a logical mapping 
  between fields found in the NFL API and fields used in the 'game' collection of
  the MongoDB database.'''
  game_id = StringField(max_length=36, required=True)
  week = EmbeddedDocumentField(Week, required=True)
  start_time = DateTimeField(required=True)
  phase = StringField(max_length=15, required=True)
  attendance = IntField()
  stadium = StringField(max_length=50)
  home_score = EmbeddedDocumentField(GameScore, required=True)
  away_score = EmbeddedDocumentField(GameScore, required=True)
  home_team = EmbeddedDocumentField(Team, required=True)
  away_team = EmbeddedDocumentField(Team, required=True)
  weather = StringField(max_length=500)
  drives = EmbeddedDocumentListField(Drive, required=True)
  plays = EmbeddedDocumentListField(Play, required=True)

  def __repr__(self):
    return f"{{'model': 'Game', 'game_id': '{self.game_id}'}}"
  def __str__(self):
    return f"{{Game '{self.game_id}'}}"
  def __eq__(self, other):
    if isinstance(other, Game):
      return (self.game_id == other.game_id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Game', self.game_id))
  def _get_drives(self, drives):
    return [Drive().custom_json(self, drive) for drive in drives]
  def _get_plays(self, plays):
    return [Play().custom_json(self, play) for play in plays]
  def custom_json(self, game_info, game_detail):
    game_info = game_info["node"]
    game_detail = game_detail["data"]["viewer"]["gameDetail"]
    self.game_id = game_detail["id"]
    self.week = Week(season_type=game_info["week"]["seasonType"], 
      season_year=game_info["week"]["seasonValue"], 
      week=game_info["week"]["weekValue"])
    self.start_time = game_detail["gameTime"]
    self.phase = game_detail["phase"]
    self.attendance = (int(game_detail["attendance"].replace(',', '')) if 
      game_detail["attendance"] else None)
    self.stadium = game_detail["stadium"]
    self.home_score = GameScore(total=game_detail["homePointsTotal"], 
      Q1=game_detail["homePointsQ1"], Q2=game_detail["homePointsQ2"], 
      Q3=game_detail["homePointsQ3"], Q4=game_detail["homePointsQ4"], 
      overtime=game_detail["homePointsOvertimeTotal"])
    self.away_score = GameScore(total=game_detail["visitorPointsTotal"], 
      Q1=game_detail["visitorPointsQ1"], Q2=game_detail["visitorPointsQ2"], 
      Q3=game_detail["visitorPointsQ3"], Q4=game_detail["visitorPointsQ4"], 
      overtime=game_detail["visitorPointsOvertimeTotal"])
    self.home_team = Team(team_id=game_detail["homeTeam"]["abbreviation"], 
      name=game_detail["homeTeam"]["nickName"])
    self.away_team = Team(team_id=game_detail["visitorTeam"]["abbreviation"], 
      name=game_detail["visitorTeam"]["nickName"])
    self.weather = (game_detail["weather"]["shortDescription"] if 
      game_detail["weather"] else None)
    self.drives = self._get_drives(game_detail["drives"])
    self.plays = self._get_plays(game_detail["plays"])
    return self 
  def data_dict(self):
    return {'id': self.game_id, 'start_time': 
      self.start_time.strftime("%Y-%m-%d %H:%M"), 
      'season_type': self.week['season_type'], 
      'season_year': self.week['season_year'], 'week': self.week['week'], 
      'home_team': self.home_team['team_id'], 'away_team': self.away_team['team_id'],
      'home_score': self.home_score['total'], 
      'away_score': self.away_score['total']}

class Player(Document):
  '''Represents a single NFL player and provides a logical mapping between 
  fields found in the NFL API and fields used in the 'player' collection of
  the MongoDB database.'''
  player_id = StringField(max_length=36, required=True)
  name = StringField(max_length=100, required=True)
  team = StringField(max_length=3)
  position = StringField(max_length=10)
  status = StringField(max_length=10)
  jersey_number = IntField()

  def __repr__(self):
    return f"{{'model': 'Player', 'player_id': '{self.player_id}'}}"
  def __str__(self):
    return f"{{{self.name} {self.position} {self.team}}}"
  def __eq__(self, other):
    if isinstance(other, Player):
      return (self.player_id == other.player_id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Player', self.player_id))
  def data_dict(self):
    return {'id': self.player_id, 'name': self.name, 'team': self.team, 
      'position': self.position, 'status': self.status}  
  def custom_json(self, player_info):
    self.player_id = player_info["id"]
    self.name = player_info["name"]
    self.team = player_info["team"]
    self.position = player_info["position"]
    self.status = player_info["status"]
    self.jersey_number = player_info["jerseyNumber"]
    return self
  def is_locked(self):
    season_year, season_type, week = get_current_week()
    week = Week(season_year=season_year, season_type=season_type, week=week)
    this_game = Game.objects(Q(week=week) & (Q(home_team__team_id=self.team) | 
      Q(away_team__team_id=self.team)))
    if len(this_game) == 1:
      game_start = this_game[0].start_time.replace(tzinfo=pytz.UTC)
      now = datetime.datetime.now(pytz.UTC)
      if game_start < now:
        return True
    return False  

POSITIONS = ['DB', 'DL', 'K', 'LB', 'OL', 'P', 'QB', 'RB', 'TE', 'WR']

class LineupSettings(EmbeddedDocument):
  '''Represents how a league's lineups are made, i.e. how many of each player 
  position group are included in a lineup for that league. Only used in League.'''
  DB = IntField()
  DL = IntField()
  K = IntField()
  LB = IntField()
  OL = IntField()
  P = IntField()
  QB = IntField()
  RB = IntField()
  TE = IntField()
  WR = IntField()

  def __repr__(self):
    settings = []
    for position in POSITIONS:
      if getattr(self, position):
        settings.append(f"'{position}': {getattr(self, position)}")
    return f"{{'model': 'LineupSettings', {', '.join(settings)}}}"
  def __str__(self):
    settings = []
    for position in POSITIONS:
      if getattr(self, position):
        settings.append(f"{getattr(self, position)} {position}")
    return f"{{Lineup Settings: {', '.join(settings)}}}"
  def __eq__(self, other):
    if isinstance(other, LineupSettings):
      return (self.DB == other.DB and self.DL == other.DL and self.K == other.K and 
        self.LB == other.LB and self.OL == other.OL and self.P == other.P and 
        self.QB == other.QB and self.RB == other.RB and self.TE == other.TE and 
        self.WR == other.WR)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('LineupSettings', self.DB, self.DL, self.K, self.LB, self.OL, 
      self.P, self.QB, self.RB, self.TE, self.WR))
  def data_dict(self):
    settings = {}
    for position in POSITIONS:
      if getattr(self, position):
        settings[position] = getattr(self, position)
    return settings    

STATFIELDS = ('defense_ast', 'defense_ffum', 'defense_fgblk', 'defense_frec', 
  'defense_frec_tds', 'defense_frec_yds', 'defense_int', 'defense_int_tds', 
  'defense_int_yds', 'defense_misc_tds', 'defense_misc_yds', 'defense_pass_def', 
  'defense_puntblk', 'defense_qbhit', 'defense_safe', 'defense_sk', 
  'defense_sk_yds', 'defense_tds', 'defense_tkl', 'defense_tkl_loss', 
  'defense_tkl_loss_yds', 'defense_tkl_primary', 'defense_xpblk', 'first_down', 
  'fourth_down_att', 'fourth_down_conv', 'fourth_down_failed', 'fumbles_forced', 
  'fumbles_lost', 'fumbles_notforced', 'fumbles_oob', 'fumbles_rec', 
  'fumbles_rec_tds', 'fumbles_rec_yds', 'fumbles_tot', 'kicking_all_yds', 
  'kicking_downed', 'kicking_fga', 'kicking_fgb', 'kicking_fgm', 'kicking_fgm_yds', 
  'kicking_fgmissed', 'kicking_fgmissed_yds', 'kicking_i20', 'kicking_rec', 
  'kicking_rec_tds', 'kicking_tot', 'kicking_touchback', 'kicking_xpa', 
  'kicking_xpb', 'kicking_xpmade', 'kicking_xpmissed', 'kicking_yds', 
  'kickret_fair', 'kickret_oob', 'kickret_ret', 'kickret_tds', 
  'kickret_touchback', 'kickret_yds', 'passing_att', 'passing_cmp', 
  'passing_cmp_air_yds', 'passing_first_down', 'passing_incmp', 
  'passing_incmp_air_yds', 'passing_int', 'passing_sk', 'passing_sk_yds', 
  'passing_tds', 'passing_twopta', 'passing_twoptm', 'passing_twoptmissed', 
  'passing_yds', 'penalty', 'penalty_first_down', 'penalty_yds', 'punting_blk', 
  'punting_i20', 'punting_tot', 'punting_touchback', 'punting_yds', 
  'puntret_downed', 'puntret_fair', 'puntret_oob', 'puntret_tds', 'puntret_tot', 
  'puntret_touchback', 'puntret_yds', 'receiving_rec', 'receiving_tar', 
  'receiving_tds', 'receiving_twopta', 'receiving_twoptm', 'receiving_twoptmissed', 
  'receiving_yac_yds', 'receiving_yds', 'rushing_att', 'rushing_first_down', 
  'rushing_loss', 'rushing_loss_yds', 'rushing_tds', 'rushing_twopta', 
  'rushing_twoptm', 'rushing_twoptmissed', 'rushing_yds', 'third_down_att', 
  'third_down_conv', 'third_down_failed', 'timeout', 'xp_aborted')

COMPARISON_VALS = ('=', '>', '<', '>=', '<=')

class StatCondition(EmbeddedDocument):
  '''Represents one condition in one custom defined stat in a league. Used only 
  in ScoreSetting.'''
  field = StringField(max_length=21, choices=STATFIELDS, required=True)
  comparison = StringField(max_length=2, choices=COMPARISON_VALS, 
    required=True)
  value = DecimalField(required=True)

  def __repr__(self):
    return (f"{{'model': 'StatCondition', 'field': '{self.field}', "
      f"'comparison': '{self.comparison}', 'value': {self.value}}}")
  def __str__(self):
    return (f"{{StatCondition {self.field}{self.comparison}{self.value}}}")
  def __eq__(self, other):
    if isinstance(other, StatCondition):
      return (self.field == other.field and self.comparison == other.comparison 
        and self.value == other.value)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('StatCondition', self.field, self.comparison, self.value))
  def data_dict(self):
    return {'field': self.field, 'comparison': self.comparison, 'value': 
      float(self.value)}  

class ScoreSetting(EmbeddedDocument):
  '''Represents one custom defined stat in a league. Used only in League.'''
  name = StringField(max_length=100, required=True)
  field = StringField(max_length=21, choices=STATFIELDS, required=True)
  conditions = EmbeddedDocumentListField(StatCondition)
  multiplier = DecimalField(required=True)

  def __repr__(self):
    return (f"{{'model': 'ScoreSetting', 'name': '{self.name}'}}")
  def __str__(self):
    return f"{{ScoreSetting {self.name}}}"
  def __eq__(self, other):
    if isinstance(other, ScoreSetting):
      return (self.name == other.name and self.field == other.field and 
        self.conditions == other.conditions and self.multiplier == other.multiplier)
    else:
      return NotImplemented   
  def __hash__(self):
    return hash(('ScoreSetting', self.name))
  def data_dict(self):
    conditions = [condition.data_dict() for condition in self.conditions]
    return {'name': self.name, 'field': self.field, 'conditions': 
      conditions, 'multiplier': float(self.multiplier)}  

class League(Document):
  '''Represents a user-created league, containing members (users in the league), 
  lineup settings, and scoring settings.'''
  name = StringField(max_length=200, required=True, unique=True)
  password = StringField(max_length=200, required=True)
  lineup_settings = EmbeddedDocumentField(LineupSettings)
  scoring_settings = EmbeddedDocumentListField(ScoreSetting)

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
  def correct_password(self, password):
    if compare_hash(self.password, password):
      return True
    else:
      return False
  def get_lineup_settings(self):
    return self.lineup_settings.data_dict() if self.lineup_settings else {}
  def set_lineup_settings(self, lineup_settings):
    self.lineup_settings = LineupSettings()
    for position in lineup_settings:
      setattr(self.lineup_settings, position, lineup_settings[position])
    self.save()
  def get_scoring_settings(self):
    return [setting.data_dict() for setting in self.scoring_settings]
  def set_scoring_settings(self, scoring_settings):
    self.scoring_settings = []
    for setting in scoring_settings:
      conditions = []
      for condition in setting['conditions']:
        conditions.append(StatCondition(field=condition['field'], 
          comparison=condition['comparison'], value=condition['value']))
      self.scoring_settings.append(ScoreSetting(name=setting['name'], 
        field=setting['field'], conditions=conditions, 
        multiplier=setting['multiplier']))
    self.save()
  def set_password(self, password):
    self.password = generate_hash(password)
    self.save()
  def get_members(self):
    return [member.user.username for member in Member.objects(league=self).order_by(
      'user')]  

class Member(Document):
  '''Represents one user's participation in a league.'''
  user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
  league = ReferenceField(League, reverse_delete_rule=CASCADE, required=True)
  admin = BooleanField(default=False)
  lineups = DictField()

  def __repr__(self):
    return (f"{{'model': 'Member', 'username': '{self.user.username}', 'league': "
      f"'{self.league.name}'}}")
  def __str__(self):
    return f"{{User '{self.user.username}' in League '{self.league.name}'}}"
  def __eq__(self, other):
    if isinstance(other, Member):
      return (self.user == other.user and self.league == other.league)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Member', self.user.username, self.league.name))
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
    self.save()
  def lineup_add(self, lineup, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    week_key = f"{season_year}{season_type}{week}"
    detailed_lineup = []
    for player_id in lineup:
      detailed_lineup.append(Player.objects.get(player_id=player_id).data_dict())
    self.lineups[week_key] = detailed_lineup
    self.save()