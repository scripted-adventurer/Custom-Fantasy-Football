# -*- coding: utf-8 -*-
import os
import datetime
import pytz

from django.db import models
from django.contrib.auth.models import User

from common.current_week import get_current_week
from common.hashing import generate_hash, compare_hash

def get_safe(model_name, **kwargs):
  # a modified get() function that returns a single matching object if one exists
  # or None otherwise (doesn't raise an Exception)
  models = {'Game': Game, 'Player': Player, 'Team': Team, 'League': League, 
    'LeagueStat': LeagueStat, 'Lineup': Lineup, 'Member': Member, 
    'StatCondition': StatCondition, 'User': User}
  model = models[model_name]
  data = model.objects.filter(**kwargs)
  if len(data) == 1:
    return data[0]
  else:
    return None 

class SeasonType(models.TextChoices):
  PRE = 'PRE'
  REG = 'REG'
  PRO = 'PRO'
  POST = 'POST'

class Game(models.Model):
  game_id = models.CharField(primary_key=True, max_length=36)
  start_time = models.DateTimeField()
  season_type = models.CharField(max_length=4, choices=SeasonType.choices)
  season_year = models.SmallIntegerField()
  week = models.SmallIntegerField()
  phase = models.TextField(null=True)
  attendance = models.IntegerField(null=True)
  stadium = models.TextField(null=True)
  home_score = models.SmallIntegerField(null=True, default=0)
  home_score_q1 = models.SmallIntegerField(null=True, default=0)
  home_score_q2 = models.SmallIntegerField(null=True, default=0)
  home_score_q3 = models.SmallIntegerField(null=True, default=0)
  home_score_q4 = models.SmallIntegerField(null=True, default=0)
  home_score_ot = models.SmallIntegerField(null=True, default=0)
  away_score = models.SmallIntegerField(null=True, default=0)
  away_score_q1 = models.SmallIntegerField(null=True, default=0)
  away_score_q2 = models.SmallIntegerField(null=True, default=0)
  away_score_q3 = models.SmallIntegerField(null=True, default=0)
  away_score_q4 = models.SmallIntegerField(null=True, default=0)
  away_score_ot = models.SmallIntegerField(null=True, default=0)
  home_team = models.ForeignKey('Team', models.DO_NOTHING, db_column='home_team', 
    related_name='home_team')
  away_team = models.ForeignKey('Team', models.DO_NOTHING, db_column='away_team', 
    related_name='away_team')
  weather = models.TextField(null=True)
  modified_at = models.DateTimeField(auto_now=True)

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
  def data_dict(self):
    return {'id': self.game_id, 'start_time': 
      self.start_time.strftime("%Y-%m-%d %H:%M"), 'season_type': self.season_type, 
      'season_year': self.season_year, 'week': self.week, 
      'home_team': self.home_team.team_id, 'away_team': self.away_team.team_id,
      'home_score': self.home_score, 'away_score': self.away_score}

class Drive(models.Model):
  game = models.ForeignKey('Game', models.CASCADE)
  drive_id = models.SmallIntegerField()
  start_quarter = models.SmallIntegerField(null=True)
  end_quarter = models.SmallIntegerField(null=True)
  start_transition = models.TextField(null=True)
  end_transition = models.TextField(null=True)
  start_field = models.TextField(null=True)
  end_field = models.TextField(null=True)
  start_time = models.TextField(null=True)
  end_time = models.TextField(null=True)
  pos_team = models.ForeignKey('Team', models.DO_NOTHING)
  pos_time = models.TextField(null=True)
  first_downs = models.SmallIntegerField(null=True)
  penalty_yards = models.SmallIntegerField(null=True)
  yards_gained = models.SmallIntegerField(null=True)
  play_count = models.SmallIntegerField(null=True)

  def __repr__(self):
    return (f"{{'model': 'Drive', 'game_id': '{self.game.game_id}', "
    f"'drive_id': {self.drive_id}}}")
  def __str__(self):
    return f"{{Drive {self.drive_id} from Game '{self.game.game_id}'}}"
  def __eq__(self, other):
    if isinstance(other, Drive):
      return (self.id == other.id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Drive', self.id))

class Play(models.Model):
  drive = models.ForeignKey('Drive', models.CASCADE)
  play_id = models.SmallIntegerField()
  time = models.TextField(null=True)
  down = models.SmallIntegerField(null=True)
  start_yardline = models.TextField(null=True)
  end_yardline = models.TextField(null=True)
  first_down = models.BooleanField(null=True)
  penalty = models.BooleanField(null=True)
  description = models.TextField(null=True)
  play_type = models.TextField(null=True)
  pos_team = models.ForeignKey('Team', models.DO_NOTHING, db_column='pos_team')
  quarter = models.SmallIntegerField(null=True)
  yards_to_go = models.SmallIntegerField(null=True)

  def __repr__(self):
    return (f"{{'model': 'Play', 'game_id': '{self.drive.game.game_id}', "
    f"'drive_id': {self.drive.drive_id}, 'play_id': {self.play_id}}}")
  def __str__(self):
    return (f"{{Play {self.play_id} from Drive {self.drive.drive_id} from Game "
    f"'{self.drive.game.game_id}'}}")
  def __eq__(self, other):
    if isinstance(other, Play):
      return (self.id == other.id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Play', self.id))

class PlayPlayer(models.Model):
  play = models.ForeignKey('Play', models.CASCADE)
  player = models.ForeignKey('Player', models.DO_NOTHING)
  team = models.ForeignKey('Team', models.DO_NOTHING, db_column='team')
  defense_ast = models.SmallIntegerField(default=0)
  defense_ffum = models.SmallIntegerField(default=0)
  defense_fgblk = models.SmallIntegerField(default=0)
  defense_frec = models.SmallIntegerField(default=0)
  defense_frec_tds = models.SmallIntegerField(default=0)
  defense_frec_yds = models.SmallIntegerField(default=0)
  defense_int = models.SmallIntegerField(default=0)
  defense_int_tds = models.SmallIntegerField(default=0)
  defense_int_yds = models.SmallIntegerField(default=0)
  defense_misc_tds = models.SmallIntegerField(default=0)
  defense_misc_yds = models.SmallIntegerField(default=0)
  defense_pass_def = models.SmallIntegerField(default=0)
  defense_puntblk = models.SmallIntegerField(default=0)
  defense_qbhit = models.SmallIntegerField(default=0)
  defense_safe = models.SmallIntegerField(default=0)
  defense_sk = models.FloatField(default=0)
  defense_sk_yds = models.SmallIntegerField(default=0)
  defense_tds = models.SmallIntegerField(default=0)
  defense_tkl = models.SmallIntegerField(default=0)
  defense_tkl_loss = models.SmallIntegerField(default=0)
  defense_tkl_loss_yds = models.SmallIntegerField(default=0)
  defense_tkl_primary = models.SmallIntegerField(default=0)
  defense_xpblk = models.SmallIntegerField(default=0)
  first_down = models.SmallIntegerField(default=0)
  fourth_down_att = models.SmallIntegerField(default=0)
  fourth_down_conv = models.SmallIntegerField(default=0)
  fourth_down_failed = models.SmallIntegerField(default=0)
  fumbles_forced = models.SmallIntegerField(default=0)
  fumbles_lost = models.SmallIntegerField(default=0)
  fumbles_notforced = models.SmallIntegerField(default=0)
  fumbles_oob = models.SmallIntegerField(default=0)
  fumbles_rec = models.SmallIntegerField(default=0)
  fumbles_rec_tds = models.SmallIntegerField(default=0)
  fumbles_rec_yds = models.SmallIntegerField(default=0)
  fumbles_tot = models.SmallIntegerField(default=0)
  kicking_all_yds = models.SmallIntegerField(default=0)
  kicking_downed = models.SmallIntegerField(default=0)
  kicking_fga = models.SmallIntegerField(default=0)
  kicking_fgb = models.SmallIntegerField(default=0)
  kicking_fgm = models.SmallIntegerField(default=0)
  kicking_fgm_yds = models.SmallIntegerField(default=0)
  kicking_fgmissed = models.SmallIntegerField(default=0)
  kicking_fgmissed_yds = models.SmallIntegerField(default=0)
  kicking_i20 = models.SmallIntegerField(default=0)
  kicking_rec = models.SmallIntegerField(default=0)
  kicking_rec_tds = models.SmallIntegerField(default=0)
  kicking_tot = models.SmallIntegerField(default=0)
  kicking_touchback = models.SmallIntegerField(default=0)
  kicking_xpa = models.SmallIntegerField(default=0)
  kicking_xpb = models.SmallIntegerField(default=0)
  kicking_xpmade = models.SmallIntegerField(default=0)
  kicking_xpmissed = models.SmallIntegerField(default=0)
  kicking_yds = models.SmallIntegerField(default=0)
  kickret_fair = models.SmallIntegerField(default=0)
  kickret_oob = models.SmallIntegerField(default=0)
  kickret_ret = models.SmallIntegerField(default=0)
  kickret_tds = models.SmallIntegerField(default=0)
  kickret_touchback = models.SmallIntegerField(default=0)
  kickret_yds = models.SmallIntegerField(default=0)
  passing_att = models.SmallIntegerField(default=0)
  passing_cmp = models.SmallIntegerField(default=0)
  passing_cmp_air_yds = models.SmallIntegerField(default=0)
  passing_incmp = models.SmallIntegerField(default=0)
  passing_incmp_air_yds = models.SmallIntegerField(default=0)
  passing_int = models.SmallIntegerField(default=0)
  passing_sk = models.SmallIntegerField(default=0)
  passing_sk_yds = models.SmallIntegerField(default=0)
  passing_tds = models.SmallIntegerField(default=0)
  passing_twopta = models.SmallIntegerField(default=0)
  passing_twoptm = models.SmallIntegerField(default=0)
  passing_twoptmissed = models.SmallIntegerField(default=0)
  passing_yds = models.SmallIntegerField(default=0)
  penalty = models.SmallIntegerField(default=0)
  penalty_first_down = models.SmallIntegerField(default=0)
  penalty_yds = models.SmallIntegerField(default=0)
  punting_blk = models.SmallIntegerField(default=0)
  punting_i20 = models.SmallIntegerField(default=0)
  punting_tot = models.SmallIntegerField(default=0)
  punting_touchback = models.SmallIntegerField(default=0)
  punting_yds = models.SmallIntegerField(default=0)
  puntret_downed = models.SmallIntegerField(default=0)
  puntret_fair = models.SmallIntegerField(default=0)
  puntret_oob = models.SmallIntegerField(default=0)
  puntret_tds = models.SmallIntegerField(default=0)
  puntret_tot = models.SmallIntegerField(default=0)
  puntret_touchback = models.SmallIntegerField(default=0)
  puntret_yds = models.SmallIntegerField(default=0)
  receiving_rec = models.SmallIntegerField(default=0)
  receiving_tar = models.SmallIntegerField(default=0)
  receiving_tds = models.SmallIntegerField(default=0)
  receiving_twopta = models.SmallIntegerField(default=0)
  receiving_twoptm = models.SmallIntegerField(default=0)
  receiving_twoptmissed = models.SmallIntegerField(default=0)
  receiving_yac_yds = models.SmallIntegerField(default=0)
  receiving_yds = models.SmallIntegerField(default=0)
  rushing_att = models.SmallIntegerField(default=0)
  rushing_first_down = models.SmallIntegerField(default=0)
  rushing_loss = models.SmallIntegerField(default=0)
  rushing_loss_yds = models.SmallIntegerField(default=0)
  rushing_tds = models.SmallIntegerField(default=0)
  rushing_twopta = models.SmallIntegerField(default=0)
  rushing_twoptm = models.SmallIntegerField(default=0)
  rushing_twoptmissed = models.SmallIntegerField(default=0)
  rushing_yds = models.SmallIntegerField(default=0)
  third_down_att = models.SmallIntegerField(default=0)
  third_down_conv = models.SmallIntegerField(default=0)
  third_down_failed = models.SmallIntegerField(default=0)
  timeout = models.SmallIntegerField(default=0)
  xp_aborted = models.SmallIntegerField(default=0)

  def __repr__(self):
    return (f"{{'model': 'PlayPlayer', 'player': '{self.player.player_id}', "
      f"'game_id': '{self.play.drive.game.game_id}', 'drive_id': "
      f"{self.play.drive.drive_id}, 'play_id': {self.play.play_id}}}")
  def __str__(self):
    return (f"{{Player '{self.player.player_id}' from Play {self.play.play_id} "
      f"from Drive {self.play.drive.drive_id} from Game "
      f"'{self.play.drive.game.game_id}'}}")
  def __eq__(self, other):
    if isinstance(other, PlayPlayer):
      return (self.id == other.id)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('PlayPlayer', self.id))

class Player(models.Model):
  player_id = models.CharField(primary_key=True, max_length=36)
  name = models.TextField()
  team = models.ForeignKey('Team', models.DO_NOTHING, db_column='team', null=True)
  position = models.TextField()
  status = models.TextField(null=True)
  jersey_number = models.SmallIntegerField(null=True)

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
  def data_dict(self):
    return {'id': self.player_id, 'name': self.name, 'team': 
      self.team.team_id, 'position': self.position, 'status': self.status}
  def is_locked(self):
    season_year, season_type, week = get_current_week()
    this_game = (Game.objects.filter(home_team=self.team, 
      season_type=season_type, season_year=season_year, week=week) | 
      (Game.objects.filter(away_team=self.team, season_type=season_type, 
      season_year=season_year, week=week)))
    if len(this_game) == 1:
      game_start = this_game[0].start_time.replace(tzinfo=pytz.UTC)
      now = datetime.datetime.now(pytz.UTC)
      if game_start < now:
        return True
    return False

class Team(models.Model):
  team_id = models.CharField(primary_key=True, max_length=3)
  name = models.TextField()
  active = models.BooleanField()

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
  def data_dict(self):
    return {'id': self.team_id, 'name': self.name}

class League(models.Model):
  name = models.TextField()
  # league password is stored as SHA256 hash
  password = models.TextField()
  # below are the number of positions included in a league's lineup
  db = models.SmallIntegerField(default=0)
  dl = models.SmallIntegerField(default=0)
  k = models.SmallIntegerField(default=0)
  lb = models.SmallIntegerField(default=0)
  ol = models.SmallIntegerField(default=0)
  p = models.SmallIntegerField(default=0)
  qb = models.SmallIntegerField(default=0)
  rb = models.SmallIntegerField(default=0)
  te = models.SmallIntegerField(default=0)
  wr = models.SmallIntegerField(default=0)
  # pre built position list for convenience
  positions = ['db', 'dl', 'k', 'lb', 'ol', 'p', 'qb', 'rb', 'te', 'wr']

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
    lineup = {}
    for pos in self.positions:
      if getattr(self, pos):
        lineup[pos.upper()] = getattr(self, pos)
    return lineup
  def set_lineup_settings(self, lineup_settings):
    for pos in self.positions:
      if pos.upper() in lineup_settings:
        setattr(self, pos, lineup_settings[pos.upper()])
      else:
        setattr(self, pos, 0)
    self.save()  
  def get_scoring_settings(self):
    scoring = []
    for stat in LeagueStat.objects.filter(league=self):
      scoring.append({'name': stat.name, 'field': stat.field,
        'conditions': [], 'multiplier': float(stat.multiplier)})
      if stat.conditions:
        for condition in StatCondition.objects.filter(league_stat=stat):
          scoring[-1]['conditions'].append({'field': condition.field, 
            'comparison': condition.comparison, 'value': condition.value})
    return scoring      
  def set_scoring_settings(self, scoring):
    # remove any stats that aren't in the new settings
    all_names = [stat['name'] for stat in scoring]
    for stat in LeagueStat.objects.filter(league=self):
      if stat.name not in all_names:
        stat.delete()
    # add the new stats 
    for stat in scoring:
      stat_row = LeagueStat.objects.get_or_create(league=self, 
        name=stat['name'])[0]
      stat_row.field = stat['field']
      stat_row.multiplier = stat['multiplier']
      stat_row.save()
      if stat['conditions']:
        stat_row.conditions = True
        stat_row.save()
        # remove the old conditions 
        for condition in StatCondition.objects.filter(league_stat=stat_row):
          condition.delete()
        # add the new ones   
        for condition in stat['conditions']:
          cond_row = StatCondition.objects.get_or_create(league_stat=stat_row, 
            field=condition['field'], comparison=condition['comparison'], 
            value=condition['value'])
  def set_password(self, password):
    self.password = generate_hash(password)
    self.save()
  def get_members(self):
    return [member.user.username for member in 
      Member.objects.filter(league=self).order_by('user__username')]

class StatField(models.TextChoices):
  DEFENSE_AST = 'defense_ast'
  DEFENSE_FFUM = 'defense_ffum'
  DEFENSE_FGBLK = 'defense_fgblk'
  DEFENSE_FREC = 'defense_frec'
  DEFENSE_FREC_TDS = 'defense_frec_tds'
  DEFENSE_FREC_YDS = 'defense_frec_yds'
  DEFENSE_INT = 'defense_int'
  DEFENSE_INT_TDS = 'defense_int_tds'
  DEFENSE_INT_YDS = 'defense_int_yds'
  DEFENSE_MISC_TDS = 'defense_misc_tds'
  DEFENSE_MISC_YDS = 'defense_misc_yds'
  DEFENSE_PASS_DEF = 'defense_pass_def'
  DEFENSE_PUNTBLK = 'defense_puntblk'
  DEFENSE_QBHIT = 'defense_qbhit'
  DEFENSE_SAFE = 'defense_safe'
  DEFENSE_SK = 'defense_sk'
  DEFENSE_SK_YDS = 'defense_sk_yds'
  DEFENSE_TDS = 'defense_tds'
  DEFENSE_TKL = 'defense_tkl'
  DEFENSE_TKL_LOSS = 'defense_tkl_loss'
  DEFENSE_TKL_LOSS_YDS = 'defense_tkl_loss_yds'
  DEFENSE_TKL_PRIMARY = 'defense_tkl_primary'
  DEFENSE_XPBLK = 'defense_xpblk'
  FIRST_DOWN = 'first_down'
  FOURTH_DOWN_ATT = 'fourth_down_att'
  FOURTH_DOWN_CONV = 'fourth_down_conv'
  FOURTH_DOWN_FAILED = 'fourth_down_failed'
  FUMBLES_FORCED = 'fumbles_forced'
  FUMBLES_LOST = 'fumbles_lost'
  FUMBLES_NOTFORCED = 'fumbles_notforced'
  FUMBLES_OOB = 'fumbles_oob'
  FUMBLES_REC = 'fumbles_rec'
  FUMBLES_REC_TDS = 'fumbles_rec_tds'
  FUMBLES_REC_YDS = 'fumbles_rec_yds'
  FUMBLES_TOT = 'fumbles_tot'
  KICKING_ALL_YDS = 'kicking_all_yds'
  KICKING_DOWNED = 'kicking_downed'
  KICKING_FGA = 'kicking_fga'
  KICKING_FGB = 'kicking_fgb'
  KICKING_FGM = 'kicking_fgm'
  KICKING_FGM_YDS = 'kicking_fgm_yds'
  KICKING_FGMISSED = 'kicking_fgmissed'
  KICKING_FGMISSED_YDS = 'kicking_fgmissed_yds'
  KICKING_I20 = 'kicking_i20'
  KICKING_REC = 'kicking_rec'
  KICKING_REC_TDS = 'kicking_rec_tds'
  KICKING_TOT = 'kicking_tot'
  KICKING_TOUCHBACK = 'kicking_touchback'
  KICKING_XPA = 'kicking_xpa'
  KICKING_XPB = 'kicking_xpb'
  KICKING_XPMADE = 'kicking_xpmade'
  KICKING_XPMISSED = 'kicking_xpmissed'
  KICKING_YDS = 'kicking_yds'
  KICKRET_FAIR = 'kickret_fair'
  KICKRET_OOB = 'kickret_oob'
  KICKRET_RET = 'kickret_ret'
  KICKRET_TDS = 'kickret_tds'
  KICKRET_TOUCHBACK = 'kickret_touchback'
  KICKRET_YDS = 'kickret_yds'
  PASSING_ATT = 'passing_att'
  PASSING_CMP = 'passing_cmp'
  PASSING_CMP_AIR_YDS = 'passing_cmp_air_yds'
  PASSING_FIRST_DOWN = 'passing_first_down'
  PASSING_INCMP = 'passing_incmp'
  PASSING_INCMP_AIR_YDS = 'passing_incmp_air_yds'
  PASSING_INT = 'passing_int'
  PASSING_SK = 'passing_sk'
  PASSING_SK_YDS = 'passing_sk_yds'
  PASSING_TDS = 'passing_tds'
  PASSING_TWOPTA = 'passing_twopta'
  PASSING_TWOPTM = 'passing_twoptm'
  PASSING_TWOPTMISSED = 'passing_twoptmissed'
  PASSING_YDS = 'passing_yds'
  PENALTY = 'penalty'
  PENALTY_FIRST_DOWN = 'penalty_first_down'
  PENALTY_YDS = 'penalty_yds'
  PUNTING_BLK = 'punting_blk'
  PUNTING_I20 = 'punting_i20'
  PUNTING_TOT = 'punting_tot'
  PUNTING_TOUCHBACK = 'punting_touchback'
  PUNTING_YDS = 'punting_yds'
  PUNTRET_DOWNED = 'puntret_downed'
  PUNTRET_FAIR = 'puntret_fair'
  PUNTRET_OOB = 'puntret_oob'
  PUNTRET_TDS = 'puntret_tds'
  PUNTRET_TOT = 'puntret_tot'
  PUNTRET_TOUCHBACK = 'puntret_touchback'
  PUNTRET_YDS = 'puntret_yds'
  RECEIVING_REC = 'receiving_rec'
  RECEIVING_TAR = 'receiving_tar'
  RECEIVING_TDS = 'receiving_tds'
  RECEIVING_TWOPTA = 'receiving_twopta'
  RECEIVING_TWOPTM = 'receiving_twoptm'
  RECEIVING_TWOPTMISSED = 'receiving_twoptmissed'
  RECEIVING_YAC_YDS = 'receiving_yac_yds'
  RECEIVING_YDS = 'receiving_yds'
  RUSHING_ATT = 'rushing_att'
  RUSHING_FIRST_DOWN = 'rushing_first_down'
  RUSHING_LOSS = 'rushing_loss'
  RUSHING_LOSS_YDS = 'rushing_loss_yds'
  RUSHING_TDS = 'rushing_tds'
  RUSHING_TWOPTA = 'rushing_twopta'
  RUSHING_TWOPTM = 'rushing_twoptm'
  RUSHING_TWOPTMISSED = 'rushing_twoptmissed'
  RUSHING_YDS = 'rushing_yds'
  THIRD_DOWN_ATT = 'third_down_att'
  THIRD_DOWN_CONV = 'third_down_conv'
  THIRD_DOWN_FAILED = 'third_down_failed'
  TIMEOUT = 'timeout'
  XP_ABORTED = 'xp_aborted'

class LeagueStat(models.Model):
  league = models.ForeignKey(League, on_delete=models.CASCADE)
  name = models.TextField()
  field = models.CharField(max_length=21, choices=StatField.choices)
  # when true, look for conditions in StatCondition
  conditions = models.BooleanField(default=False)
  # used for calculating scores
  multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=0)

  def __repr__(self):
    return (f"{{'model': 'LeagueStat', 'league': '{self.league.name}', 'name': "
    f"'{self.name}'}}")
  def __str__(self):
    return f"{{Stat '{self.name}' from League '{self.league.name}'}}"
  def __eq__(self, other):
    if isinstance(other, LeagueStat):
      return (self.league == other.league and self.name == other.name)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('LeagueStat', self.league, self.name))

class StatCondition(models.Model):
  class Comparison(models.TextChoices):
    EQ = '='
    GT = '>'
    LT = '<'
    GTE = '>='
    LTE = '<='

  league_stat = models.ForeignKey(LeagueStat, on_delete=models.CASCADE)
  field = models.CharField(max_length=21, choices=StatField.choices)
  comparison = models.CharField(max_length=2, choices=Comparison.choices)
  value = models.SmallIntegerField(default=0)

  def __repr__(self):
    return (f"{{'model': 'StatCondition', 'league': " 
      f"'{self.league_stat.league.name}', 'stat': '{self.league_stat.name}', "
      f"'field': '{self.field}', 'comparison': '{self.comparison}', "
      f"'value': {self.value}}}")
  def __str__(self):
    return (f"{{Condition {self.field}{self.comparison}{self.value} for "
      f"'{self.league_stat.name}' in League '{self.league_stat.league.name}'}}")
  def __eq__(self, other):
    if isinstance(other, StatCondition):
      return (self.league_stat == other.league_stat and self.field == other.field 
        and self.comparison == other.comparison and self.value == other.value)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('StatCondition', self.league_stat, self.field, self.comparison, 
      self.value))

class Member(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  league = models.ForeignKey(League, on_delete=models.CASCADE)
  admin = models.BooleanField(default=False)

  def __repr__(self):
    return (f"{{'model': 'Member', 'username': '{self.user.username}', 'league': "
    f"'{self.league.name}'}}")
  def __str__(self):
    return f"{{User '{self.user.username}' in League '{self.league.name}'}}"
  def __eq__(self, other):
    if isinstance(other, Member):
      return (self.user.username == other.user.username and self.league == 
        other.league)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Member', self.user.username, self.league))
  def is_admin(self):
    return self.admin
  def get_lineup(self, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    lineup_entries = Lineup.objects.filter(member=self, season_type=season_type, 
      season_year=season_year, week=week).order_by('player__position')
    return [entry.player.data_dict() for entry in lineup_entries]
  def lineup_delete(self, player_id, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    row = Lineup.objects.filter(member=self, season_type=season_type, 
      season_year=season_year, week=week, player_id=player_id)
    if len(row) == 1:
      row[0].delete()
  def lineup_add(self, player_id, season_type='', season_year='', week=''):
    if not season_type or not season_year or not week:
      season_year, season_type, week = get_current_week()
    Lineup.objects.create(member=self, season_type=season_type, 
      season_year=season_year, week=week, player_id=player_id)      

class Lineup(models.Model):
  member = models.ForeignKey(Member, on_delete=models.CASCADE)
  season_year = models.SmallIntegerField()
  season_type = models.CharField(max_length=4, choices=SeasonType.choices)
  week = models.SmallIntegerField()
  player = models.ForeignKey(Player, on_delete=models.CASCADE)

  def __repr__(self):
    return (f"{{'model': 'Lineup', 'user': '{self.member.user.username}', "
    f"'league': '{self.member.league.name}', 'season_year': {self.season_year}, "
    f"'season_type': '{self.season_type}', 'week': {self.week}, "
    f"'player_id': '{self.player.player_id}'}}")
  def __str__(self):
    return (f"{{Player '{self.player.player_id}' for User '{self.member.user.username}' "
    f"in League '{self.member.league.name}' for '{self.season_type}' "
    f"{self.season_year} week {self.week}}}")
  def __eq__(self, other):
    if isinstance(other, Lineup):
      return (self.member == other.member and self.season_year == 
        other.season_year and self.season_type == other.season_type and 
        self.week == other.week and self.player == other.player)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('Lineup', self.member, self.season_year, self.season_type, 
      self.week, self.player))                 