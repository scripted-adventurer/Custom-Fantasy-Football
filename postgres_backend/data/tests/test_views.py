from django.test import TestCase
from django.db import connection
from django.contrib.auth.models import User
from django.db import connection

from freezegun import freeze_time
import os

from .view_test_request import ViewTestRequest
from .setup import TestData, TestCases
import data.models as db_models

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Utility = common.Utility

class ViewsTest(TestCase):
  # automatically loaded:
  # 5 test users (referenced with TestData().user)
  # all active players and teams (prior to the 2020 season)
  # all games from 2019 REG 17
  # all drives, plays, and play_players from game 10160000-0581-45c0-455c-8dcc2dd0671b
  
  fixtures = ['user', 'team', 'player', 'game', 'drive', 'play', 'play_player']

  def setUp(self):
    super().setUp()
    self.data = TestData()
    self.test_cases = TestCases().get()

  def test_games(self):
    for test in self.test_cases['games']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

  def test_league(self):
    self.data.create('League', name='test_league_0')
    self.data.create('Member', user=self.data.user[0], 
      league=self.data.league[0])
    self.data.create('Member', user=self.data.user[1], 
      league=self.data.league[0], admin=True)

    for test in self.test_cases['league']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

    # check data is updated
    league = db_models.League.objects.get(name=self.data.league[0].name)
    self.assertEqual(league.password, Utility().custom_hash('new_password'))
 
  def test_league_member(self):
    self.data.create('League', name='test_league_0')
    self.data.create('Member', user=self.data.user[0], 
      league=self.data.league[0], admin=True)
    self.data.create('Member', user=self.data.user[1], 
      league=self.data.league[0])
    self.data.create('Member', user=self.data.user[2], 
      league=self.data.league[0])

    for test in self.test_cases['league_member']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

    # check members are removed
    league = db_models.League.objects.get(name=self.data.league[0].name)
    self.assertEqual(league.get_members(), ['test_user_0'])

  # Sunday 2PM during Week 17 2019 (1PM players are locked, others available)
  @freeze_time("2019-12-29 19:00:00")
  def test_league_member_lineup(self):
    self.data.create('League', name='test_league_0', qb=1, rb=2,
      wr=2, te=1, k=1)
    self.data.create('Member', user=self.data.user[0], 
      league=self.data.league[0])
    self.data.create('Member', user=self.data.user[1], 
      league=self.data.league[0])
    # Travis Kelce ('32004b45-4c01-2458-b7b6-3a14cdb414dd') is locked here 
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='32005455-4322-4643-f70e-a24b7ce9db07')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='32005745-4e61-5770-9c68-1652f876bc72')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='32004241-5219-2674-af43-1519254e563d')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='3200454c-4c28-9284-cdcc-74694c8d1749')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='32004b45-4c01-2458-b7b6-3a14cdb414dd')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='32005748-4972-2063-1ea8-adb8ac89fa9d')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG',
      season_year=2019, week=17, player_id='32004b55-5053-4597-b958-87408c31956f')

    for test in self.test_cases['league_member_lineup']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

  def test_league_members(self):
    self.data.create('League', name='test_league_0')
    self.data.league[0].set_password('password')

    for test in self.test_cases['league_members']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

  def test_league_stats_scores(self):
    self.data.create('League', name='test_league_0')
    lineup_settings = {'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2}
    scoring_settings = [
    {'name': 'passing yards', 'field': 'passing_yds', 'conditions': [], 'multiplier': .04},
    {'name': 'passing TDs', 'field': 'passing_tds', 'conditions': [], 'multiplier': 4},
    {'name': 'passing 2pts', 'field': 'passing_twoptm', 'conditions': [], 'multiplier': 2},
    {'name': 'rushing yards', 'field': 'rushing_yds', 'conditions': [], 'multiplier': .1},
    {'name': 'rushing TDs', 'field': 'rushing_tds', 'conditions': [], 'multiplier': 6},
    {'name': 'rushing 2pts', 'field': 'rushing_twoptm', 'conditions': [], 'multiplier': 2},
    {'name': 'receiving yards', 'field': 'receiving_yds', 'conditions': [], 'multiplier': .1},
    {'name': 'receiving TDs', 'field': 'receiving_tds', 'conditions': [], 'multiplier': 6},
    {'name': 'receiving 2pts', 'field': 'receiving_twoptm', 'conditions': [], 'multiplier': 2},
    {'name': 'field goals made', 'field': 'kicking_fgm', 'conditions': [], 'multiplier': 3},
    {'name': 'extra points made', 'field': 'kicking_xpmade', 'conditions': [], 'multiplier': 1},
    {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
    {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 40}, 
    {'field': 'kicking_fgm_yds', 'comparison': '<', 'value': 50}], 'multiplier': 1},
    {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
    {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 50}], 'multiplier': 2}]
    self.data.league[0].set_lineup_settings(lineup_settings)
    self.data.league[0].set_scoring_settings(scoring_settings)

    self.data.create('Member', user=self.data.user[0], 
      league=self.data.league[0])
    self.data.create('Member', user=self.data.user[1], 
      league=self.data.league[0])
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='32004a4f-4e02-6624-33bd-3ba151b7013d')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='32004241-5219-2674-af43-1519254e563d')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='32004144-4121-8591-4d26-4c0ac739af41')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='32004144-4121-8591-4d26-4c0ac739af41')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='32004552-5480-0920-32a6-165b5a77814e')
    self.data.create('Lineup', member=self.data.member[0], season_type='REG', 
      season_year=2019, week=17, player_id='32004352-4f36-9933-a863-d4bf2cc5772e')

    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='3200424c-4f31-5389-8dc7-e49c9f486370')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='32004a4f-4839-9188-cb7b-f29b5ea64839')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='3200454c-4c28-9284-cdcc-74694c8d1749')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='3200474f-4c57-3546-c21d-b780be32aca0')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='3200434f-4f29-9382-29e1-70020b0a09be')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='32004b45-4c01-2458-b7b6-3a14cdb414dd')
    self.data.create('Lineup', member=self.data.member[1], season_type='REG', 
      season_year=2019, week=17, player_id='32005052-4114-3616-ccef-0127103fb075')

    for test in self.test_cases['league_stats']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

    for test in self.test_cases['league_scores']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

  def test_leagues(self):
    self.data.create('League', name='test_league_0')
    self.data.league[0].set_password('password')

    for test in self.test_cases['leagues']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

    # check data is created
    league = db_models.League.objects.get(name='new_league')
    member = db_models.Member.objects.get(user=self.data.user[0], 
      league__name='new_league')
    self.assertEqual(member.admin, True)  

  def test_player(self):
    for test in self.test_cases['player']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())

  # Sunday afternoon during Week 17 2019
  @freeze_time("2019-12-29 18:30:00")
  def test_players(self):
    # add the fuzzystrmatch extension to Postgres for player search
    with connection.cursor() as cursor:
      cursor.execute("CREATE EXTENSION fuzzystrmatch;")

    for test in self.test_cases['players']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())   

  def test_session(self):
    for test in self.test_cases['session']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())   

  def test_team(self):
    for test in self.test_cases['team']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run()) 

  def test_teams(self):
    for test in self.test_cases['teams']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run()) 

  def test_user(self):
    password_hash = Utility().custom_hash('password')
    self.data.create('League', name='test_league_0', 
      password=password_hash)
    self.data.create('League', name='test_league_1', 
      password=password_hash)
    self.data.create('Member', user=self.data.user[1], 
      league=self.data.league[0])
    self.data.create('Member', user=self.data.user[1], 
      league=self.data.league[1])

    for test in self.test_cases['user']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run()) 
    
    # check data was updated
    user_1 = db_models.get_safe('User', username=self.data.user[1].username)
    self.assertEqual(user_1, None) 

  def test_users(self):
    for test in self.test_cases['users']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run()) 

    # check data is created
    user1 = db_models.User.objects.get(username='test_new_user')
    user2 = db_models.User.objects.get(username='test_new_user_2')

  def test_week(self):
    for test in self.test_cases['week']:
      test_case = ViewTestRequest(test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      self.assertEqual(True, test_case.run())