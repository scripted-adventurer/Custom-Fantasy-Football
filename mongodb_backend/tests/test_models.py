import unittest

import datetime
from freezegun import freeze_time
import os
import pytz

from mongodb_backend import models 

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Utility = common.Utility

class TestModels(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.data = TestData()
  
  def test_game(self):
    main = models.Game().get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    same = models.Game().get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    different = models.Game().get(game_id='10160000-0581-4680-ba82-12e629d4584f')
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
  
  def test_drive(self):
    game = models.Game().get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    main = game.drives[13]
    same = game.drives[13]
    different = game.drives[14]
    self.assertEqual(repr(main), "{'model': 'Drive', 'game_id': "
      "'10160000-0581-45c0-455c-8dcc2dd0671b', 'drive_id': 14}")
    self.assertEqual(str(main), 
      "{Drive 14 from Game '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
  
  def test_play(self):
    game = models.Game().get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    main = game.plays[45]
    same = game.plays[45]
    different = game.plays[46]
    self.assertEqual(repr(main), 
      "{'model': 'Play', 'game_id': '10160000-0581-45c0-455c-8dcc2dd0671b', "
      "'drive_id': 14, 'play_id': 2945}")
    self.assertEqual(str(main), 
      "{Play 2945 from Drive 14 from Game '10160000-0581-45c0-455c-8dcc2dd0671b'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)

  def test_player(self):
    main = models.Player().get(player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    same = models.Player().get(player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    different = models.Player().get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    self.assertEqual(repr(main), "{'model': 'Player', 'player_id': "
      "'3200524f-4433-9293-a3cf-ad7758d03003'}")
    self.assertEqual(str(main), "{Aaron Rodgers QB GB}")
    self.assertEqual(main.as_dict(), {'id': '3200524f-4433-9293-a3cf-ad7758d03003', 
      'name': 'Aaron Rodgers', 'team': 'GB', 'position': 'QB', 'status': 'ACT', 
      'jersey_number': 12})
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
      
  # Saturday during Week 17 2019
  @freeze_time("2019-12-28 12:00:00")
  def test_player_is_locked_neither(self):
    gb_qb = models.Player().get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = models.Player().get(player_id='32005749-4c77-7781-795c-94c753706d1d')
    self.assertEqual(gb_qb.is_locked(), False)
    self.assertEqual(sea_qb.is_locked(), False)
  
  # Sunday afternoon during Week 17 2019
  @freeze_time("2019-12-29 18:30:00")
  def test_player_is_locked_one(self):
    gb_qb = models.Player().get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = models.Player().get(player_id='32005749-4c77-7781-795c-94c753706d1d')
    self.assertEqual(gb_qb.is_locked(), True)
    self.assertEqual(sea_qb.is_locked(), False)
  
  # Monday during Week 1 2019
  @freeze_time("2019-12-30 12:00:00")
  def test_player_is_locked_both(self):
    gb_qb = models.Player().get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = models.Player().get(player_id='32005749-4c77-7781-795c-94c753706d1d')
    self.assertEqual(gb_qb.is_locked(), True)
    self.assertEqual(sea_qb.is_locked(), True)

  def test_league_basic(self):
    name = 'test_league_basic'
    models.League().create(name=f"{name}_0", password='password')
    models.League().create(name=f"{name}_1", password='password')
    
    main = models.League().get(name=f"{name}_0")
    same = models.League().get(name=f"{name}_0")
    different = models.League().get(name=f"{name}_1")
    self.assertEqual(repr(main), 
      f"{{'model': 'League', 'name': '{name}_0'}}")
    self.assertEqual(str(main), f"{{League {name}_0}}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    
  def test_league_additional(self):
    name = 'test_league_additional'
    lineup_settings = {'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2}
    scoring_settings = [
      {'name': 'passing yards', 'field': 'passing_yds', 'conditions': [], 
      'multiplier': .1},
      {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
      {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 40}, 
      {'field': 'kicking_fgm_yds', 'comparison': '<', 'value': 50}], 
      'multiplier': 2.0}, 
      {'name': 'fg made 50+ yards', 'field': 'kicking_fgm', 'conditions': [
      {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 50}], 
      'multiplier': 3.0}]
    # league 0 is blank, league 1 has standard settings
    league_0 = models.League().create(name=f"{name}_0", password='password')
    league_1 = models.League().create(name=f"{name}_1", password='password', 
      lineup_settings=lineup_settings, scoring_settings=scoring_settings)  
    user_0 = models.User().create(username=f"{name}_0")
    user_1 = models.User().create(username=f"{name}_1")
    user_2 = models.User().create(username=f"{name}_2")
    member_0 = models.Member().create(username=f"{name}_0", league_name=f"{name}_0")
    member_1 = models.Member().create(username=f"{name}_1", league_name=f"{name}_0")
    member_2 = models.Member().create(username=f"{name}_2", league_name=f"{name}_0")

    self.assertEqual(league_0.correct_password('password'), True)
    self.assertEqual(league_0.correct_password('incorrect'), False)
    self.assertEqual(league_0.get_lineup_settings(), {})
    self.assertEqual(league_0.get_scoring_settings(), [])
    self.assertEqual(league_0.get_members(), [])
    self.assertEqual(league_1.get_lineup_settings(), lineup_settings)
    self.assertEqual(league_1.get_scoring_settings(), scoring_settings)
    self.assertEqual(league_1.get_members(), [f"{name}_0", f"{name}_1", 
      f"{name}_2"])
    
    league_0.set_lineup_settings(lineup_settings)
    league_0.set_scoring_settings(scoring_settings)
    league_0.set_password('new_password')
    # check all changes were made
    league_0 = models.League().get(name=f"{name}_1")
    self.assertEqual(league_0.get_lineup_settings(), lineup_settings)
    self.assertEqual(league_0.get_scoring_settings(), scoring_settings)
    self.assertEqual(league_0.correct_password('new_password'), True)

  def test_member_basic(self):
    name = 'test_member_basic'
    league_0 = models.League().create(name=f"{name}_0", password='password')
    user_0 = models.User().create(username=f"{name}_0")
    user_1 = models.User().create(username=f"{name}_1")
    member_0 = models.Member().create(username=f"{name}_0", 
      league_name=f"{name}_0")
    member_1 = models.Member().create(username=f"{name}_1", 
      league_name=f"{name}_0")

    main = models.Member().get(username=f"{name}_0", league_name=f"{name}_0")
    same = models.Member().get(username=f"{name}_0", league_name=f"{name}_0")
    different = models.Member().get(username=f"{name}_1", league_name=f"{name}_0")
    self.assertEqual(repr(main), 
      (f"{{'model': 'Member', 'username': '{name}_0', 'league': '{name}_0'}}"))
    self.assertEqual(str(main), 
      (f"{{User '{name}_0' in League '{name}_0'}}"))
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)

  def test_member_additional(self):
    name = 'test_member_additional'
    league_0 = models.League().create(name=f"{name}_0", password='password')
    user_0 = models.User().create(username=f"{name}_0")
    user_1 = models.User().create(username=f"{name}_1")
    member_0 = models.Member().create(username=f"{name}_0", 
      league_name=f"{name}_0")
    member_1 = models.Member().create(username=f"{name}_1", 
      league_name=f"{name}_0")
    past_lineup = [
      {"id": "3200524f-4433-9293-a3cf-ad7758d03003", "name": "Aaron Rodgers", 
      "team": "GB", "position": "QB", "status": "ACT","jerseyNumber": "12"}, 
      {"id": "3200434f-5570-9400-e1ae-f835abb5963e", "name": "Kirk Cousins",
      "team": "MIN", "position": "QB", "status": "ACT", "jerseyNumber": "08"}
    ]
    current_lineup = [
      {"id": "3200524f-4433-9293-a3cf-ad7758d03003", "name": "Aaron Rodgers", 
      "team": "GB", "position": "QB", "status": "ACT","jerseyNumber": "12"},
      {"id": "32005749-4c77-7781-795c-94c753706d1d", "name": "Russell Wilson",
      "team": "SEA", "position": "QB", "status": "ACT", "jerseyNumber": "03"}
    ]
    member_1.lineup_add(past_lineup, 'REG', 2019, 17)
    member_1.lineup_add(current_lineup)

    # no lineup
    self.assertEqual(member_0.get_lineup('REG', 2019, 17), [])
    self.assertEqual(member_0.get_lineup(), [])
    # existing lineup
    member_1_lineup = member_1.get_lineup('REG', 2019, 17)
    self.assertEqual(member_1_lineup, past_lineup)
    member_1_lineup = member_1.get_lineup()
    self.assertEqual(member_1_lineup, current_lineup)
    # lineup add previous week
    member_0.lineup_add(past_lineup, 'REG', 2019, 17)
    member_0_lineup = member_0.get_lineup('REG', 2019, 17)
    self.assertEqual(member_0_lineup, past_lineup)
    # lineup add current week
    member_0.lineup_add(current_lineup)
    member_0_lineup = member_0.get_lineup()
    self.assertEqual(member_0_lineup, current_lineup)
    # lineup delete previous week - week doesn't exist
    member_0.lineup_delete('REG', 2019, 16)
    member_0_lineup = member_0.get_lineup('REG', 2019, 16)
    self.assertEqual(member_0_lineup, [])
    # lineup delete previous week - week exists
    member_0.lineup_delete('REG', 2019, 17)
    member_0_lineup = member_0.get_lineup('REG', 2019, 17)
    self.assertEqual(member_0_lineup, [])
    # lineup delete current week
    member_0.lineup_delete()
    member_0_lineup = member_0.get_lineup()
    self.assertEqual(member_0_lineup, [])

if __name__ == '__main__':
  unittest.main()