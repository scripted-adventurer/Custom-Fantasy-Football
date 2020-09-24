# -*- coding: utf-8 -*-
from freezegun import freeze_time

from mongodb_backend.flaskr import models 
from common.hashing import generate_hash, compare_hash

def test_models(app):
  # to speed up execution, run all the tests within one database setup/teardown
  hashed_password = generate_hash('password')

  def test_week():
    main = models.Week(season_type='REG', season_year=2019, week=17)
    same = models.Week(season_type='REG', season_year=2019, week=17)
    different = models.Week(season_type='REG', season_year=2020, week=1)
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'Week', 'season_type': 'REG', "
      "'season_year': 2019, 'week': 17}")
    assert str(main) == "{Week #17 in 2019 REG}"
    assert main.as_key() == '2019REG17'
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_game_score():
    main = models.GameScore(total=24, Q1=7, Q2=0, Q3=14, Q4=3, overtime=0)
    same = models.GameScore(total=24, Q1=7, Q2=0, Q3=14, Q4=3, overtime=0)
    different = models.GameScore(total=28, Q1=7, Q2=0, Q3=14, Q4=7, overtime=0)
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'GameScore', 'total': 24, 'Q1': 7, "
      "'Q2': 0, 'Q3': 14, 'Q4': 3, 'overtime': 0}")
    assert str(main) == "{Score with total 24}"
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_team():
    main = models.Team(team_id='GB', name='Green Bay Packers')
    same = models.Team(team_id='GB', name='Green Bay Packers')
    different = models.Team(team_id='CHI', name='Chicago Bears')
    other = models.Week(season_type='REG', season_year=2020, week=1)
    assert repr(main) == "{'model': 'Team', 'team_id': 'GB'}"
    assert str(main) == "{Green Bay Packers}"
    assert main.data_dict() == {'id': 'GB', 'name': 'Green Bay Packers'}
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other  

  def test_drive():
    game = models.Game.objects.get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    main = game.drives[13]
    same = game.drives[13]
    different = game.drives[14]
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'Drive', 'game_id': "
      "'10160000-0581-45c0-455c-8dcc2dd0671b', 'drive_id': 14}")
    assert str(main) == "{Drive 14 from Game '10160000-0581-45c0-455c-8dcc2dd0671b'}"
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_play():
    game = models.Game.objects.get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    main = game.plays[45]
    same = game.plays[45]
    different = game.plays[46]
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'Play', 'game_id': " 
      "'10160000-0581-45c0-455c-8dcc2dd0671b', 'drive_id': 6, 'play_id': 1095}")
    assert str(main) == ("{Play 1095 from Drive 6 from Game "
      "'10160000-0581-45c0-455c-8dcc2dd0671b'}")
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_game():
    main = models.Game.objects.get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    same = models.Game.objects.get(game_id='10160000-0581-45c0-455c-8dcc2dd0671b')
    different = models.Game.objects.get(game_id='10160000-0581-4680-ba82-12e629d4584f')
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == "{'model': 'Game', 'game_id': '10160000-0581-45c0-455c-8dcc2dd0671b'}"
    assert str(main) == "{Game '10160000-0581-45c0-455c-8dcc2dd0671b'}"
    assert main.data_dict() == {'id': '10160000-0581-45c0-455c-8dcc2dd0671b', 
      'start_time': "2019-12-29 18:00", 'season_type': 'REG', 'season_year': 2019, 
      'week': 17, 'home_team': 'DET', 'away_team': 'GB', 'home_score': 20, 
      'away_score': 23}
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_player():
    main = models.Player.objects.get(player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    same = models.Player.objects.get(player_id='3200524f-4433-9293-a3cf-ad7758d03003')
    different = models.Player.objects.get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'Player', 'player_id': "
      "'3200524f-4433-9293-a3cf-ad7758d03003'}")
    assert str(main) == "{Aaron Rodgers QB GB}"
    assert main.data_dict() == {'id': '3200524f-4433-9293-a3cf-ad7758d03003', 
      'name': 'Aaron Rodgers', 'team': 'GB', 'position': 'QB', 'status': 'ACT'}
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other
 
  # Sunday during Packers 2019 bye week 
  @freeze_time("2019-11-17 20:00:00")
  def test_player_is_locked_bye_week():
    gb_qb = models.Player.objects.get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    assert not gb_qb.is_locked()

  # Saturday during Week 17 2019
  @freeze_time("2019-12-28 12:00:00")
  def test_player_is_locked_neither():
    gb_qb = models.Player.objects.get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = models.Player.objects.get(player_id='32005749-4c77-7781-795c-94c753706d1d')
    assert not gb_qb.is_locked()
    assert not sea_qb.is_locked()

  # Sunday afternoon during Week 17 2019
  @freeze_time("2019-12-29 18:30:00")
  def test_player_is_locked_one():
    gb_qb = models.Player.objects.get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = models.Player.objects.get(player_id='32005749-4c77-7781-795c-94c753706d1d')
    assert gb_qb.is_locked()
    assert not sea_qb.is_locked()

  # Monday during Week 1 2019
  @freeze_time("2019-12-30 12:00:00")
  def test_player_is_locked_both():
    gb_qb = models.Player.objects.get(player_id='3200434f-5570-9400-e1ae-f835abb5963e')
    sea_qb = models.Player.objects.get(player_id='32005749-4c77-7781-795c-94c753706d1d')
    assert gb_qb.is_locked()
    assert sea_qb.is_locked()

  def test_lineup_settings():
    main = models.LineupSettings(K=1, QB=1, RB=2, TE=1, WR=2)
    same = models.LineupSettings(K=1, QB=1, RB=2, TE=1, WR=2)
    different = models.LineupSettings(K=1, QB=2, RB=2, TE=1, WR=2)
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'LineupSettings', 'K': 1, 'QB': 1, "
      "'RB': 2, 'TE': 1, 'WR': 2}")
    assert str(main) == "{Lineup Settings: 1 K, 1 QB, 2 RB, 1 TE, 2 WR}"
    assert main.data_dict() == {'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2}
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_score_setting():
    main = models.ScoreSetting(name='passing yards', field='passing_yds', 
      conditions=[], multiplier=0.04)
    same = models.ScoreSetting(name='passing yards', field='passing_yds', 
      conditions=[], multiplier=0.04)
    different = models.ScoreSetting(name='rushing yards', field='rushing_yds', 
      conditions=[], multiplier=0.1)
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == "{'model': 'ScoreSetting', 'name': 'passing yards'}"
    assert str(main) == "{ScoreSetting passing yards}"
    assert main.data_dict() == {'name': 'passing yards', 'field': 'passing_yds', 
      'conditions': [], 'multiplier': 0.04}
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_stat_condition():
    main = models.StatCondition(field='kicking_fgm_yds', comparison='>=', value=50)
    same = models.StatCondition(field='kicking_fgm_yds', comparison='>=', value=50)
    different = models.StatCondition(field='kicking_fgm_yds', comparison='>=', value=40)
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == ("{'model': 'StatCondition', 'field': "
      "'kicking_fgm_yds', 'comparison': '>=', 'value': 50.00}")
    assert str(main) == "{StatCondition kicking_fgm_yds>=50.00}"
    assert main.data_dict() == {'field': 'kicking_fgm_yds', 'comparison': '>=', 
      'value': 50.00}
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_league_basic():
    name = 'test_league_basic'
    models.League(name=f"{name}_0", password=hashed_password).save()
    models.League(name=f"{name}_1", password=hashed_password).save()
    
    main = models.League.objects.get(name=f"{name}_0")
    same = models.League.objects.get(name=f"{name}_0")
    different = models.League.objects.get(name=f"{name}_1")
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == f"{{'model': 'League', 'name': '{name}_0'}}"
    assert str(main) == f"{{League {name}_0}}"
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other
    
  def test_league_additional():
    name = 'test_league_additional'
    lineup_settings = {'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2}
    scoring_settings = [
      {'name': 'passing yards', 'field': 'passing_yds', 'conditions': [], 
      'multiplier': .1},
      {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
      {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 40.00}, 
      {'field': 'kicking_fgm_yds', 'comparison': '<', 'value': 50.00}], 
      'multiplier': 2.0}, 
      {'name': 'fg made 50+ yards', 'field': 'kicking_fgm', 'conditions': [
      {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 50.00}], 
      'multiplier': 3.0}]
    # league 0 is blank, league 1 has standard settings
    league_0 = models.League(name=f"{name}_0", password=hashed_password).save()
    league_1 = models.League(name=f"{name}_1", password=hashed_password, 
      lineup_settings=lineup_settings, scoring_settings=scoring_settings).save()
    user_0 = models.User(username=f"{name}_0", password=hashed_password).save()
    user_1 = models.User(username=f"{name}_1", password=hashed_password).save()
    user_2 = models.User(username=f"{name}_2", password=hashed_password).save()
    member_0 = models.Member(user=user_0, league=league_1).save()
    member_1 = models.Member(user=user_1, league=league_1).save()
    member_2 = models.Member(user=user_2, league=league_1).save()

    assert league_0.correct_password('password')
    assert not league_0.correct_password('incorrect')
    assert league_0.get_lineup_settings() == {}
    assert league_0.get_scoring_settings() == []
    assert league_0.get_members() == []
    assert league_1.get_lineup_settings() == lineup_settings
    assert league_1.get_scoring_settings() == scoring_settings
    assert league_1.get_members() == [f"{name}_0", f"{name}_1", f"{name}_2"]
    
    league_0.set_lineup_settings(lineup_settings)
    league_0.set_scoring_settings(scoring_settings)
    league_0.set_password('new_password')
    # check all changes were made
    league_0 = models.League.objects.get(name=f"{name}_0")
    assert league_0.get_lineup_settings() == lineup_settings
    assert league_0.get_scoring_settings() == scoring_settings
    assert league_0.correct_password('new_password')

  def test_user():
    name = 'test_user'
    main = models.User(username=f'{name}_0', password='password').save()
    same = models.User.objects.get(username=f'{name}_0')
    different = models.User(username=f'{name}_1', password='password').save()
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == f"{{'model': 'User', 'username': '{name}_0'}}"
    assert str(main) == main.get_id()
    assert main.is_active
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other
    main.set_password('new_password')
    compare_hash(main.password, 'new_password')

  def test_member_basic():
    name = 'test_member_basic'
    league_0 = models.League(name=f"{name}_0", password=hashed_password).save()
    user_0 = models.User(username=f"{name}_0", password=hashed_password).save()
    user_1 = models.User(username=f"{name}_1", password=hashed_password).save()
    member_0 = models.Member(user=user_0, league=league_0).save()
    member_1 = models.Member(user=user_1, league=league_0).save()

    main = models.Member.objects.get(user=user_0, league=league_0)
    same = models.Member.objects.get(user=user_0, league=league_0)
    different = models.Member.objects.get(user=user_1, league=league_0)
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == (f"{{'model': 'Member', 'username': '{name}_0', "
      f"'league': '{name}_0'}}")
    assert str(main) == f"{{User '{name}_0' in League '{name}_0'}}"
    assert main.is_admin() == False
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_member_additional():
    name = 'test_member_additional'
    league_0 = models.League(name=f"{name}_0", password=hashed_password).save()
    user_0 = models.User(username=f"{name}_0", password=hashed_password).save()
    user_1 = models.User(username=f"{name}_1", password=hashed_password).save()
    member_0 = models.Member(user=user_0, league=league_0).save()
    member_1 = models.Member(user=user_1, league=league_0).save()
    past_lineup_base = ["3200524f-4433-9293-a3cf-ad7758d03003", 
      "3200434f-5570-9400-e1ae-f835abb5963e"]
    past_lineup_detailed = [
      {"id": "3200524f-4433-9293-a3cf-ad7758d03003", "name": "Aaron Rodgers", 
      "team": "GB", "position": "QB", "status": "ACT"}, 
      {"id": "3200434f-5570-9400-e1ae-f835abb5963e", "name": "Kirk Cousins",
      "team": "MIN", "position": "QB", "status": "ACT"}
    ]
    current_lineup_base = ["3200524f-4433-9293-a3cf-ad7758d03003", 
      "32005749-4c77-7781-795c-94c753706d1d"]
    current_lineup_detailed = [
      {"id": "3200524f-4433-9293-a3cf-ad7758d03003", "name": "Aaron Rodgers", 
      "team": "GB", "position": "QB", "status": "ACT"},
      {"id": "32005749-4c77-7781-795c-94c753706d1d", "name": "Russell Wilson",
      "team": "SEA", "position": "QB", "status": "ACT"}
    ]
    member_1.lineup_add(past_lineup_base, 'REG', 2019, 17)
    member_1.lineup_add(current_lineup_base)

    # no lineup
    assert member_0.get_lineup('REG', 2019, 17) == []
    assert member_0.get_lineup() == []
    # existing lineup
    member_1_lineup = member_1.get_lineup('REG', 2019, 17)
    assert member_1_lineup == past_lineup_detailed
    member_1_lineup = member_1.get_lineup()
    assert member_1_lineup == current_lineup_detailed
    # lineup add previous week
    member_0.lineup_add(past_lineup_base, 'REG', 2019, 17)
    member_0_lineup = member_0.get_lineup('REG', 2019, 17)
    assert member_0_lineup == past_lineup_detailed
    # lineup add current week
    member_0.lineup_add(current_lineup_base)
    member_0_lineup = member_0.get_lineup()
    assert member_0_lineup == current_lineup_detailed
    # lineup delete previous week - week doesn't exist
    member_0.lineup_delete('REG', 2019, 16)
    member_0_lineup = member_0.get_lineup('REG', 2019, 16)
    assert member_0_lineup == []
    # lineup delete previous week - week exists
    member_0.lineup_delete('REG', 2019, 17)
    member_0_lineup = member_0.get_lineup('REG', 2019, 17)
    assert member_0_lineup == []
    # lineup delete current week
    member_0.lineup_delete()
    member_0_lineup = member_0.get_lineup()
    assert member_0_lineup == []

  test_week()
  test_game_score()
  test_team()
  test_drive()
  test_play()
  test_game()
  test_player()
  test_player_is_locked_bye_week()
  test_player_is_locked_neither()
  test_player_is_locked_one()
  test_player_is_locked_both()
  test_lineup_settings()
  test_score_setting()
  test_stat_condition()
  test_league_basic()
  test_league_additional()
  test_user()
  test_member_basic()
  test_member_additional()