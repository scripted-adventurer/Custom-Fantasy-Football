from django.test import TestCase

import datetime
from freezegun import freeze_time
import os
import pytz

import data.models as db_models
from .setup import TestData

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

class ModelsTest(TestCase):
  # automatically loaded:
  # 5 test users (referenced with TestData().user)
  # all active players and teams (prior to the 2020 season)
  # all games from 2019 REG 17
  # all drives, plays, and play_players from game 10160000-0581-45c0-455c-8dcc2dd0671b
  
  fixtures = ['user', 'team', 'player', 'game', 'drive', 'play', 'play_player']

  def setUp(self):
    super().setUp()
    self.data = TestData()
  
  def test_game(self):
    main = db_models.Game.objects.get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    same = db_models.Game.objects.get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    different = db_models.Game.objects.get(game_id='10160000-0581-4680-ba82-12e629d4584f')
    other = db_models.Drive.objects.get(id=76757)
    self.assertEqual(repr(main), "{'model': 'Game', 'game_id': '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual(str(main), "{Game '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual(main.data_dict(), 
      {'id': '10160000-0581-45c0-455c-8dcc2dd0671b', 'start_time': "2019-12-29 18:00", 
      'season_type': 'REG', 'season_year': 2019, 'week': 17, 'home_team': 'DET', 
      'away_team': 'GB', 'home_score': 20, 'away_score': 23})
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)
  
  def test_drive(self):
    main = db_models.Drive.objects.get(id=76756)
    same = db_models.Drive.objects.get(id=76756)
    different = db_models.Drive.objects.get(id=76757)
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), "{'model': 'Drive', 'game_id': "
      "'10160000-0581-45c0-455c-8dcc2dd0671b', 'drive_id': 14}")
    self.assertEqual(str(main), 
      "{Drive 14 from Game '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)
  
  def test_play(self):
    main = db_models.Play.objects.get(id=544462)
    same = db_models.Play.objects.get(id=544462)
    different = db_models.Play.objects.get(id=544463)
    other = db_models.Drive.objects.get(id=76757)
    self.assertEqual(repr(main), 
      "{'model': 'Play', 'game_id': '10160000-0581-45c0-455c-8dcc2dd0671b', "
      "'drive_id': 14, 'play_id': 2945}")
    self.assertEqual(str(main), 
      "{Play 2945 from Drive 14 from Game '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)
  
  def test_play_player(self):
    main = db_models.PlayPlayer.objects.get(id=1277030)
    same = db_models.PlayPlayer.objects.get(id=1277030)
    different = db_models.PlayPlayer.objects.get(id=1277031)
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), 
      "{'model': 'PlayPlayer', 'player': '3200524f-4433-9293-a3cf-ad7758d03003', "
      "'game_id': '10160000-0581-45c0-455c-8dcc2dd0671b', 'drive_id': 14, "
      "'play_id': 2945}")
    self.assertEqual(str(main), 
      "{Player '3200524f-4433-9293-a3cf-ad7758d03003' from Play 2945 from Drive "
      "14 from Game '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)

  def test_player(self):
    main = db_models.Player.objects.get(
      player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    same = db_models.Player.objects.get(
      player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    different = db_models.Player.objects.get(
      player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), "{'model': 'Player', 'player_id': "
      "'3200524f-4433-9293-a3cf-ad7758d03003'}")
    self.assertEqual(str(main), "{Aaron Rodgers QB GB}")
    self.assertEqual(main.data_dict(), {'id': '3200524f-4433-9293-a3cf-ad7758d03003', 
      'name': 'Aaron Rodgers', 'team': 'GB', 'position': 'QB', 'status': 'ACT'})
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)
      
  # Sunday during Packers 2019 bye week 
  @freeze_time("2019-11-17 20:00:00")
  def test_player_is_locked_bye_week(self):
    gb_qb = db_models.Player.objects.get(
      player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    self.assertEqual(gb_qb.is_locked(), False)

  # Saturday during Week 17 2019
  @freeze_time("2019-12-28 12:00:00")
  def test_player_is_locked_neither(self):
    gb_qb = db_models.Player.objects.get(
      player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = db_models.Player.objects.get(
      player_id='32005749-4c77-7781-795c-94c753706d1d')
    self.assertEqual(gb_qb.is_locked(), False)
    self.assertEqual(sea_qb.is_locked(), False)
  
  # Sunday afternoon during Week 17 2019
  @freeze_time("2019-12-29 18:30:00")
  def test_player_is_locked_one(self):
    gb_qb = db_models.Player.objects.get(
      player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = db_models.Player.objects.get(
      player_id='32005749-4c77-7781-795c-94c753706d1d')
    self.assertEqual(gb_qb.is_locked(), True)
    self.assertEqual(sea_qb.is_locked(), False)
  
  # Monday during Week 1 2019
  @freeze_time("2019-12-30 12:00:00")
  def test_player_is_locked_both(self):
    gb_qb = db_models.Player.objects.get(
      player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = db_models.Player.objects.get(
      player_id='32005749-4c77-7781-795c-94c753706d1d')
    self.assertEqual(gb_qb.is_locked(), True)
    self.assertEqual(sea_qb.is_locked(), True)   
  
  def test_team(self):
    main = db_models.Team.objects.get(team_id='GB')
    same = db_models.Team.objects.get(team_id='GB')
    different = db_models.Team.objects.get(team_id='CHI')
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), "{'model': 'Team', 'team_id': 'GB'}")
    self.assertEqual(str(main), "{Green Bay Packers}")
    self.assertEqual(main.data_dict(), {'id': 'GB', 'name': 'Green Bay Packers'})
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)

  def test_league_basic(self):
    self.data.create('League', name='test_league_basic_0', password='password')
    self.data.create('League', name='test_league_basic_1', password='password')
    main = db_models.League.objects.get(name=self.data.league[0].name)
    same = db_models.League.objects.get(name=self.data.league[0].name)
    different = self.data.league[1]
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), 
      f"{{'model': 'League', 'name': '{self.data.league[0].name}'}}")
    self.assertEqual(str(main), f"{{League {self.data.league[0].name}}}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)
    
  def test_league_additional(self):
    password_hash = common.Utility().custom_hash('password')
    lineup_settings = {'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2}
    scoring_settings = [
      {'name': 'passing yards', 'field': 'passing_yds', 'conditions': [], 
      'multiplier': .04},
      {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
      {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 40}, 
      {'field': 'kicking_fgm_yds', 'comparison': '<', 'value': 50}], 
      'multiplier': 2.0}, 
      {'name': 'fg made 50+ yards', 'field': 'kicking_fgm', 'conditions': [
      {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 50}], 
      'multiplier': 3.0}]
    new_scoring_settings = [
      {'name': 'rushing yards', 'field': 'rushing_yds', 'conditions': [], 
      'multiplier': .1}]
    # league 0 is blank, league 1 has standard settings
    self.data.create('League', name='test_league_additional_0', 
      password=password_hash)
    self.data.create('League', name='test_league_additional_1', 
      password=password_hash, qb=1, rb=2, wr=2, te=1, k=1)
    for stat in scoring_settings:
      conditions = True if stat['conditions'] else False
      self.data.create('LeagueStat', league=self.data.league[1], name=stat['name'], 
        field=stat['field'], conditions=conditions, multiplier=stat['multiplier'])
    self.data.create('StatCondition', league_stat=self.data.leaguestat[1], 
      field='kicking_fgm_yds', comparison='>=', value=40)
    self.data.create('StatCondition', league_stat=self.data.leaguestat[1], 
      field='kicking_fgm_yds', comparison='<', value=50)
    self.data.create('StatCondition', league_stat=self.data.leaguestat[2], 
      field='kicking_fgm_yds', comparison='>=', value=50)
    self.data.create('Member', league=self.data.league[1], user=self.data.user[0], 
      admin=True)
    self.data.create('Member', league=self.data.league[1], user=self.data.user[1])
    self.data.create('Member', league=self.data.league[1], user=self.data.user[2])
    self.assertEqual(self.data.league[0].correct_password('password'), True)
    self.assertEqual(self.data.league[0].correct_password('incorrect'), False)
    self.assertEqual(self.data.league[0].get_lineup_settings(), {})
    self.assertEqual(self.data.league[0].get_scoring_settings(), [])
    self.assertEqual(self.data.league[0].get_members(), [])
    self.assertEqual(self.data.league[1].get_lineup_settings(), 
      lineup_settings)
    self.assertEqual(self.data.league[1].get_scoring_settings(), 
      scoring_settings)
    self.assertEqual(self.data.league[1].get_members(), [self.data.user[0].username, 
      self.data.user[1].username, self.data.user[2].username])
    
    self.data.league[1].set_lineup_settings(lineup_settings)
    self.data.league[1].set_scoring_settings(scoring_settings)
    self.data.league[1].set_password('new_password')
    # check all changes were made
    self.data.league[1] = db_models.League.objects.get(name='test_league_additional_1')
    self.assertEqual(self.data.league[1].get_lineup_settings(), 
      lineup_settings)
    self.assertEqual(self.data.league[1].get_scoring_settings(), 
      scoring_settings)
    self.assertEqual(self.data.league[1].correct_password('new_password'), True)
    # check updating stats deletes old stats
    self.data.league[1].set_scoring_settings(new_scoring_settings)
    self.data.league[1] = db_models.League.objects.get(name='test_league_additional_1')
    self.assertEqual(self.data.league[1].get_scoring_settings(), 
      new_scoring_settings)

  def test_league_stat(self):
    password_hash = common.Utility().custom_hash('password')
    self.data.create('League', name='test_league_stat_0', password=password_hash)
    self.data.create('LeagueStat', league=self.data.league[0], name='passing yards', 
      field='passing_yds', multiplier=.04)
    self.data.create('LeagueStat', league=self.data.league[0], name='rushing tds', 
      field='rushing_tds', multiplier=6)

    main = db_models.LeagueStat.objects.get(league=self.data.league[0], 
      name='passing yards')
    same = db_models.LeagueStat.objects.get(league=self.data.league[0], 
      name='passing yards')
    different = db_models.LeagueStat.objects.get(league=self.data.league[0], 
      name='rushing tds')
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), 
      ("{'model': 'LeagueStat', 'league': 'test_league_stat_0', 'name': " +
      "'passing yards'}"))
    self.assertEqual(str(main), 
      "{Stat 'passing yards' from League 'test_league_stat_0'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)

  def test_stat_condition(self):
    password_hash = common.Utility().custom_hash('password')
    self.data.create('League', name='test_stat_condition_0', password=password_hash)
    self.data.create('LeagueStat', league=self.data.league[0], 
      name='fg bonus (40-49)', field='kicking_fgm', conditions=True, multiplier=1)
    self.data.create('StatCondition', league_stat=self.data.leaguestat[0], 
      field='kicking_fgm_yds', comparison='>=', value=40)
    self.data.create('StatCondition', league_stat=self.data.leaguestat[0], 
      field='kicking_fgm_yds', comparison='<', value=50)

    main = db_models.StatCondition.objects.get(league_stat=self.data.leaguestat[0], 
      field='kicking_fgm_yds', comparison='>=', value=40)
    same = db_models.StatCondition.objects.get(league_stat=self.data.leaguestat[0], 
      field='kicking_fgm_yds', comparison='>=', value=40)
    different = db_models.StatCondition.objects.get(league_stat=self.data.leaguestat[0], 
      field='kicking_fgm_yds', comparison='<', value=50)
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), 
      ("{'model': 'StatCondition', 'league': 'test_stat_condition_0', "
      "'stat': 'fg bonus (40-49)', 'field': 'kicking_fgm_yds', "
      "'comparison': '>=', 'value': 40}"))
    self.assertEqual(str(main), 
      ("{Condition kicking_fgm_yds>=40 for 'fg bonus (40-49)' in League "
        "'test_stat_condition_0'}"))
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)

  def test_member_basic(self):
    password_hash = common.Utility().custom_hash('password')
    self.data.create('League', name='test_member_basic_0', password=password_hash)
    self.data.create('Member', user=self.data.user[0], league=self.data.league[0])
    self.data.create('Member', user=self.data.user[1], league=self.data.league[0])

    main = db_models.Member.objects.get(user=self.data.user[0], 
      league=self.data.league[0])
    same = db_models.Member.objects.get(user=self.data.user[0], 
      league=self.data.league[0])
    different = db_models.Member.objects.get(user=self.data.user[1], 
      league=self.data.league[0])
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), 
      ("{'model': 'Member', 'username': 'test_user_0', 'league': " +
      "'test_member_basic_0'}"))
    self.assertEqual(str(main), 
      ("{User 'test_user_0' in League 'test_member_basic_0'}"))
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)

  def test_member_additional(self):
    password_hash = common.Utility().custom_hash('password')
    self.data.create('League', name='test_member_additional_0', 
      password=password_hash)
    self.data.create('Member', user=self.data.user[0], league=self.data.league[0])
    self.data.create('Member', user=self.data.user[1], league=self.data.league[0])
    # past
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    # current
    season_year, season_type, week = db_models.get_current_week()
    self.data.create('Lineup', member=self.data.member[1], season_type=season_type, 
      season_year=season_year, week=week, 
      player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    self.data.create('Lineup', member=self.data.member[1], season_type=season_type, 
      season_year=season_year, week=week, 
      player_id='32005749-4c77-7781-795c-94c753706d1d')
    # no lineup
    self.assertEqual(self.data.member[0].get_lineup('REG', 2019, 17), [])
    self.assertEqual(self.data.member[0].get_lineup(), [])
    # existing lineup past
    existing_lineup = self.data.member[1].get_lineup('REG', 2019, 17)
    self.assertEqual(existing_lineup[0]['id'], '3200524f-4433-9293-a3cf-ad7758d03003')
    self.assertEqual(existing_lineup[1]['id'], '3200434f-5570-9400-e1ae-f835abb5963e')
    # existing lineup current
    existing_lineup = self.data.member[1].get_lineup()
    self.assertEqual(existing_lineup[0]['id'], '3200524f-4433-9293-a3cf-ad7758d03003')
    self.assertEqual(existing_lineup[1]['id'], '32005749-4c77-7781-795c-94c753706d1d')
    # lineup add previous week
    self.data.member[0].lineup_add('3200524f-4433-9293-a3cf-ad7758d03003', 
      'REG', 2019, 17)
    previous_lineup = self.data.member[0].get_lineup('REG', 2019, 17)
    self.assertEqual(previous_lineup[0]['name'], 'Aaron Rodgers')
    # lineup add current week
    self.data.member[0].lineup_add('3200434f-5570-9400-e1ae-f835abb5963e')
    current_lineup = self.data.member[0].get_lineup()
    self.assertEqual(current_lineup[0]['team'], 'MIN')
    # lineup delete previous week - player doesn't exist
    self.data.member[0].lineup_delete('32005749-4c77-7781-795c-94c753706d1d', 
      'REG', 2019, 17)
    previous_lineup = self.data.member[0].get_lineup('REG', 2019, 17)
    self.assertEqual(previous_lineup[0]['position'], 'QB')
    # lineup delete previous week - player exists
    self.data.member[0].lineup_delete('3200524f-4433-9293-a3cf-ad7758d03003', 
      'REG', 2019, 17)
    self.assertEqual(self.data.member[0].get_lineup('REG', 2019, 17), [])
    # lineup delete current week - player doesn't exist
    self.data.member[0].lineup_delete('32005749-4c77-7781-795c-94c753706d1d')
    current_lineup = self.data.member[0].get_lineup()
    self.assertEqual(current_lineup[0]['status'], 'ACT')
    # lineup delete current week - player exists
    self.data.member[0].lineup_delete('3200434f-5570-9400-e1ae-f835abb5963e')
    self.assertEqual(self.data.member[0].get_lineup(), [])

  def test_lineup(self):
    password_hash = common.Utility().custom_hash('password')
    self.data.create('League', name='test_lineup_0', password=password_hash)
    self.data.create('Member', user=self.data.user[0], league=self.data.league[0])
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='3200434f-5570-9400-e1ae-f835abb5963e')

    main = db_models.Lineup.objects.get(member=self.data.member[0], 
      season_type='REG', season_year=2019, week=17, 
      player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    same = db_models.Lineup.objects.get(member=self.data.member[0], 
      season_type='REG', season_year=2019, week=17, 
      player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    different = db_models.Lineup.objects.get(member=self.data.member[0], 
      season_type='REG', season_year=2019, week=17, 
      player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    other = db_models.Play.objects.get(id=544463)
    self.assertEqual(repr(main), 
      ("{'model': 'Lineup', 'user': 'test_user_0', 'league': " 
      "'test_lineup_0', 'season_year': 2019, 'season_type': 'REG', " 
      "'week': 17, 'player_id': '3200524f-4433-9293-a3cf-ad7758d03003'}"))
    self.assertEqual(str(main), 
      ("{Player '3200524f-4433-9293-a3cf-ad7758d03003' for User 'test_user_0' "
      "in League 'test_lineup_0' for 'REG' 2019 week 17}"))
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    self.assertEqual(main == other, False)