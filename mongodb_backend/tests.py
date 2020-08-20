import gzip
import json
import unittest

from models import Game, Drive, Play 

class TestModels(unittest.TestCase):

  def setUp(self):
    with open("json/schedule/2019.json") as schedule_file:
      schedule = json.load(schedule_file)
      self.game_1_info = schedule["data"]["viewer"]["league"]["games"]["edges"][65]
      self.game_2_info = schedule["data"]["viewer"]["league"]["games"]["edges"][66]
    game_1_path = f'json/games/{self.game_1_info["node"]["gameDetailId"]}.json.gz'
    game_2_path = f'json/games/{self.game_2_info["node"]["gameDetailId"]}.json.gz'
    with gzip.open(game_1_path) as game_1_json:
      self.game_1_detail = json.load(game_1_json)
    with gzip.open(game_2_path) as game_2_json:
      self.game_2_detail = json.load(game_2_json)

  def test_game(self):
    game_1 = Game(self.game_1_info, self.game_1_detail)
    game_1a = Game(self.game_1_info, self.game_1_detail)
    game_2 = Game(self.game_2_info, self.game_2_detail)
    self.assertEqual(repr(game_1), ("models.Game(id=2019090500)"))
    self.assertEqual(str(game_1), '{Game 2019090500}')
    self.assertEqual((game_1 == game_1a), True)
    self.assertEqual((game_1 == game_2), False)
    self.assertEqual((hash(game_1) == hash(game_1a)), True)
    self.assertEqual((hash(game_1) == hash(game_2)), False)

  def test_drive(self):
    drive_1 = Drive(self.game_1_detail["data"]["viewer"]["gameDetail"]["drives"][0])
    drive_1a = Drive(self.game_1_detail["data"]["viewer"]["gameDetail"]["drives"][0])
    drive_2 = Drive(self.game_1_detail["data"]["viewer"]["gameDetail"]["drives"][1])
    drive_1_repr = ("models.Drive({'start_quarter': 1, 'start_transition': " + 
      "'KICKOFF', 'start_time': '15:00', 'end_quarter': 1, 'end_transition': " + 
      "'PUNT', 'end_time': '13:01', 'possession_team': {'name': 'Packers', " + 
      "'id': 'GB'}, 'possession_time': '1:59', 'first_downs': 0, 'penalty_yards': " + 
      "0, 'yards_gained': -10, 'play_count': 3, 'start_yardline': -25, " + 
      "'end_yardline': -15}))")
    self.assertEqual(repr(drive_1), drive_1_repr)
    self.assertEqual(str(drive_1), drive_1_repr)
    self.assertEqual((drive_1 == drive_1a), True)
    self.assertEqual((drive_1 == drive_2), False)
    self.assertEqual((hash(drive_1) == hash(drive_1a)), True)
    self.assertEqual((hash(drive_1) == hash(drive_2)), False)

  def test_play(self):
    play_1 = Play(self.game_1_detail["data"]["viewer"]["gameDetail"]["plays"][3])
    play_1a = Play(self.game_1_detail["data"]["viewer"]["gameDetail"]["plays"][3])
    play_2 = Play(self.game_1_detail["data"]["viewer"]["gameDetail"]["plays"][4])
    play_1_repr = ("models.Play({'drive_id': 1, 'quarter': 1, 'possession_team': " + 
      "{'name': 'Packers', 'id': 'GB'}, 'start_time': '14:33', 'end_time': '', " + 
      "'down': 2, 'yards_to_go': 10, 'yards_gained': 0, 'description': '(14:33) " + 
      "A.Rodgers pass short left to A.Jones to GB 25 for no gain (R.Smith).', " + 
      "'first_down': False, 'penalty': False, 'play_type': 'PASS', " + 
      "'scoring_play_type': None, 'play_clock': '18', 'time_of_day': '00:24:02', " + 
      "'start_yardline': -25, 'end_yardline': -25, 'aggregate': {'passing_yds': 0," + 
      " 'passing_att': 1, 'passing_cmp': 1, 'passing_cmp_air_yds': -1, " + 
      "'receiving_yds': 0, 'receiving_rec': 1, 'receiving_tar': 1, " + 
      "'receiving_yac_yds': 1, 'defense_tkl': 1}, 'player_stats': [{'id': " + 
      "'3200524f-4433-9293-a3cf-ad7758d03003', 'passing_yds': 0, 'passing_att': 1, " + 
      "'passing_cmp': 1, 'passing_cmp_air_yds': -1}, {'id': " + 
      "'32004a4f-4e02-6624-33bd-3ba151b7013d', 'receiving_yds': 0, " + 
      "'receiving_rec': 1, 'receiving_tar': 1, 'receiving_yac_yds': 1}, " + 
      "{'id': '3200534d-4968-5032-ead5-4d96dc1134f2', 'defense_tkl': 1}]}))")
    self.assertEqual(repr(play_1), play_1_repr)
    self.assertEqual(str(play_1), play_1_repr)
    self.assertEqual((play_1 == play_1a), True)
    self.assertEqual((play_1 == play_2), False)
    self.assertEqual((hash(play_1) == hash(play_1a)), True)
    self.assertEqual((hash(play_1) == hash(play_2)), False)

if __name__ == '__main__':
  unittest.main()